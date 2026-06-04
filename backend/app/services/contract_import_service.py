import hashlib
import json
import re
import tempfile
import unicodedata
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

import pandas as pd
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.contract import Contract, ContractImportLog
from app.models.contrato import Contrato, ContratoStatus
from app.models.fornecedor import Fornecedor
from app.models.secretaria import Secretaria

FIELD_ALIASES = {
    "tipo_instrumento": {"tipo", "tipo_instrumento", "instrumento", "tipo_do_instrumento"},
    "status": {"status", "situacao"},
    "numero_contrato": {"contrato", "numero", "numero_contrato", "n_contrato", "no_contrato"},
    "numero_aditivo": {"aditivo", "numero_aditivo", "n_aditivo"},
    "fornecedor": {"fornecedor", "contratada", "empresa"},
    "secretaria": {"secretaria", "unidade", "orgao"},
    "secretario": {"secretario", "secretaria_responsavel"},
    "gestor": {"gestor", "gestor_contrato"},
    "fiscal": {"fiscal", "fiscal_contrato"},
    "objeto": {"objeto", "descricao"},
    "vigencia_texto": {"vigencia", "periodo", "periodo_vigencia", "prazo"},
    "inicio_vigencia": {"inicio", "inicio_vigencia", "data_inicio"},
    "fim_vigencia": {
        "fim",
        "termino",
        "termino_da_vigencia",
        "fim_vigencia",
        "data_fim",
        "vencimento",
    },
    "data_os": {"data_os", "data_da_os", "ordem_servico", "data_ordem_servico"},
    "processo_administrativo": {"processo_administrativo", "processo_adm"},
    "processo_execucao": {"processo_execucao", "processo_exec"},
    "audesp_licitacao": {"audesp_licitacao", "audesp_lic"},
    "audesp_ajuste": {"audesp_ajuste", "ajuste_audesp"},
    "modalidade": {"modalidade", "modalidade_licitacao"},
    "valor_total": {"valor", "valor_total", "valor_contrato", "valor_total_contrato"},
    "data_assinatura": {"data_assinatura", "assinatura"},
    "data_publicacao": {"data_publicacao", "data_de_publicacao", "publicacao"},
    "observacao": {"observacao", "observacoes", "obs"},
}


@dataclass
class ImportContractResult:
    importados: int
    ignorados: int
    erros: int
    linhas_processadas: int
    linhas_com_erro: int
    detalhes_erro: list[dict[str, str | int]]
    sincronizados: int = 0

    def as_dict(self) -> dict[str, Any]:
        return {
            "importados": self.importados,
            "ignorados": self.ignorados,
            "erros": self.erros,
            "linhas_processadas": self.linhas_processadas,
            "linhas_com_erro": self.linhas_com_erro,
            "detalhes_erro": self.detalhes_erro,
            "sincronizados": self.sincronizados,
        }


def normalize_key(value: Any) -> str:
    text = str(value or "").replace("\n", " ").replace("\r", " ").strip().lower()
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return re.sub(r"_+", "_", text).strip("_")


def clean_headers(headers: list[Any]) -> list[str]:
    seen: dict[str, int] = {}
    cleaned = []
    for header in headers:
        base = normalize_key(header) or "coluna"
        count = seen.get(base, 0)
        seen[base] = count + 1
        cleaned.append(base if count == 0 else f"{base}_{count + 1}")
    return cleaned


def parse_date(value: Any) -> date | None:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    text = str(value).strip()
    if not text or text.lower() in {"nan", "nat", "-"}:
        return None
    parsed = pd.to_datetime(text, dayfirst=True, errors="coerce")
    if pd.isna(parsed):
        return None
    return parsed.date()


def parse_money(value: Any) -> Decimal | None:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    if isinstance(value, int | float | Decimal):
        return Decimal(str(value)).quantize(Decimal("0.01"))
    text = str(value).strip()
    if not text or text.lower() == "nan":
        return None
    normalized = re.sub(r"[^\d,.-]", "", text)
    if "," in normalized:
        normalized = normalized.replace(".", "").replace(",", ".")
    try:
        return Decimal(normalized).quantize(Decimal("0.01"))
    except InvalidOperation:
        return None


def extract_cpf(value: Any) -> tuple[str | None, str | None]:
    text = str(value or "").strip()
    match = re.search(r"\bCPF\b.*?([\d.\-]{11,14})", text, flags=re.IGNORECASE)
    if not match:
        return (text or None), None
    cpf = re.sub(r"\D", "", match.group(1))
    nome = text[: match.start()].strip(" -:")
    return (nome or None), cpf or None


def extract_cnpj(value: Any) -> tuple[str | None, str | None]:
    text = str(value or "").strip()
    match = re.search(r"\bCNPJ\b.*?([\d./-]{14,18})", text, flags=re.IGNORECASE)
    if not match:
        digits = re.sub(r"\D", "", text)
        return (text or None), digits if len(digits) == 14 else None
    cnpj = re.sub(r"\D", "", match.group(1))
    nome = text[: match.start()].strip(" -:")
    return (nome or None), cnpj or None


def parse_period(value: Any) -> tuple[date | None, date | None]:
    text = str(value or "").strip()
    dates = re.findall(r"\d{1,2}/\d{1,2}/\d{2,4}", text)
    if len(dates) < 2:
        return None, None
    return parse_date(dates[0]), parse_date(dates[1])


def calculate_days_to_expiration(end_date: date | None, today: date | None = None) -> int | None:
    if end_date is None:
        return None
    return (end_date - (today or date.today())).days


def _status_contrato_oficial(contract: Contract) -> str:
    raw_status = normalize_key(contract.status)
    if raw_status in {
        ContratoStatus.ativo.value,
        ContratoStatus.alerta.value,
        ContratoStatus.critico.value,
        ContratoStatus.suspenso.value,
        ContratoStatus.encerrado.value,
        ContratoStatus.rescindido.value,
        ContratoStatus.rascunho.value,
    }:
        return raw_status
    if contract.fim_vigencia is None:
        return ContratoStatus.rascunho.value
    dias = calculate_days_to_expiration(contract.fim_vigencia) or 0
    if dias < 0:
        return ContratoStatus.encerrado.value
    if dias <= 30:
        return ContratoStatus.critico.value
    if dias <= 60:
        return ContratoStatus.alerta.value
    return ContratoStatus.ativo.value


def _stable_cnpj_placeholder(nome: str) -> str:
    digest = hashlib.sha1(nome.encode("utf-8")).hexdigest()
    number = int(digest[:12], 16) % 10_000_000_000_000
    return f"{number:014d}"


def _get_or_create_secretaria(db: Session, nome: str | None) -> Secretaria:
    secretaria_nome = (nome or "Sem secretaria informada").strip()[:180]
    secretaria = db.scalar(select(Secretaria).where(Secretaria.nome == secretaria_nome))
    if secretaria is not None:
        return secretaria
    secretaria = Secretaria(nome=secretaria_nome, sigla=None, is_active=True)
    db.add(secretaria)
    db.flush()
    return secretaria


def _get_or_create_fornecedor(db: Session, nome: str | None, cnpj: str | None) -> Fornecedor:
    razao_social = (nome or "Fornecedor nao informado").strip()[:220]
    cnpj_value = (cnpj or _stable_cnpj_placeholder(razao_social)).strip()[:18]
    fornecedor = db.scalar(select(Fornecedor).where(Fornecedor.cnpj == cnpj_value))
    if fornecedor is not None:
        if fornecedor.razao_social != razao_social and razao_social != "Fornecedor nao informado":
            fornecedor.razao_social = razao_social
            db.add(fornecedor)
        return fornecedor
    fornecedor = Fornecedor(razao_social=razao_social, cnpj=cnpj_value, is_active=True)
    db.add(fornecedor)
    db.flush()
    return fornecedor


def _contrato_payload_from_contract(
    db: Session,
    contract: Contract,
) -> dict[str, Any] | None:
    if not contract.numero_contrato or not contract.objeto or not contract.fim_vigencia:
        return None
    inicio = contract.inicio_vigencia or contract.data_assinatura or contract.data_os
    if inicio is None or inicio > contract.fim_vigencia:
        inicio = contract.fim_vigencia
    secretaria = _get_or_create_secretaria(db, contract.secretaria)
    fornecedor = _get_or_create_fornecedor(db, contract.fornecedor, contract.cnpj)
    tags = [
        value
        for value in (
            contract.modalidade,
            contract.processo_administrativo,
            contract.processo_execucao,
        )
        if value
    ]
    return {
        "tipo_instrumento": contract.tipo_instrumento,
        "numero": contract.numero_contrato[:80],
        "orgao": (contract.secretaria or contract.secretario or "Orgao nao informado")[:180],
        "objeto": contract.objeto,
        "valor": contract.valor_total or Decimal("0.00"),
        "inicio": inicio,
        "termino": contract.fim_vigencia,
        "status": _status_contrato_oficial(contract),
        "tags": "; ".join(tags) or None,
        "secretaria_id": secretaria.id,
        "fornecedor_id": fornecedor.id,
    }


def sync_imported_contracts_to_contratos(db: Session) -> int:
    synced = 0
    contracts = db.scalars(select(Contract)).all()
    synced = _sync_contracts_to_contratos(db, contracts)
    db.commit()
    return synced


def _sync_contracts_to_contratos(db: Session, contracts: list[Contract]) -> int:
    synced = 0
    for contract in contracts:
        payload = _contrato_payload_from_contract(db, contract)
        if payload is None:
            continue
        contrato = db.scalar(
            select(Contrato).where(
                Contrato.tipo_instrumento == payload["tipo_instrumento"],
                Contrato.numero == payload["numero"],
            )
        )
        if contrato is None:
            db.add(Contrato(**payload))
            synced += 1
            continue
        changed = False
        for field, value in payload.items():
            if getattr(contrato, field) != value:
                setattr(contrato, field, value)
                changed = True
        if changed:
            db.add(contrato)
            synced += 1
    return synced


def _read_spreadsheet(path: Path) -> pd.DataFrame:
    suffix = path.suffix.lower()
    if suffix not in {".xls", ".xlsx"}:
        raise ValueError("Arquivo deve ser .xls ou .xlsx")
    engine = "xlrd" if suffix == ".xls" else "openpyxl"
    raw = pd.read_excel(path, engine=engine, dtype=object, header=None)
    header_index = _detect_header_row(raw)
    headers = clean_headers(list(raw.iloc[header_index]))
    frame = raw.iloc[header_index + 1 :].copy()
    frame.columns = headers
    return frame.reset_index(drop=True)


def _detect_header_row(frame: pd.DataFrame) -> int:
    required = {"contrato", "fornecedor", "objeto"}
    best_index = 0
    best_score = -1
    for index in range(min(20, len(frame))):
        keys = set(clean_headers(list(frame.iloc[index])))
        score = len(required & keys)
        if score > best_score:
            best_score = score
            best_index = index
        if required <= keys:
            return index
    return best_index


def _canonical_row(row: dict[str, Any]) -> dict[str, Any]:
    canonical: dict[str, Any] = {}
    for field, aliases in FIELD_ALIASES.items():
        for alias in aliases:
            if alias in row and not _is_empty(row[alias]):
                canonical[field] = row[alias]
                break
    return canonical


def _is_empty(value: Any) -> bool:
    return value is None or (isinstance(value, float) and pd.isna(value)) or not str(value).strip()


def _is_section_title(row: dict[str, Any]) -> bool:
    values = [str(value).strip() for value in row.values() if not _is_empty(value)]
    if not values:
        return True
    joined = " ".join(values).upper()
    if "CONTRATOS COM VENCIMENTO" in joined:
        return True
    return len(values) == 1 and not re.search(r"\d", values[0])


def _payload_from_row(row: dict[str, Any]) -> dict[str, Any] | None:
    if _is_section_title(row):
        return None
    data = _canonical_row(row)
    fornecedor, cnpj = extract_cnpj(data.get("fornecedor"))
    secretario, secretario_cpf = extract_cpf(data.get("secretario"))
    gestor, gestor_cpf = extract_cpf(data.get("gestor"))
    fiscal, fiscal_cpf = extract_cpf(data.get("fiscal"))
    inicio_periodo, fim_periodo = parse_period(data.get("vigencia_texto"))
    inicio = parse_date(data.get("inicio_vigencia")) or inicio_periodo
    fim = parse_date(data.get("fim_vigencia")) or fim_periodo
    tipo_instrumento = _normalize_tipo_instrumento(data.get("tipo_instrumento"))

    payload = {
        "tipo_instrumento": tipo_instrumento,
        "status": str(data.get("status") or "ativo").strip()[:50],
        "numero_contrato": _clean_text(data.get("numero_contrato"), 50),
        "numero_aditivo": _clean_text(data.get("numero_aditivo"), 50),
        "fornecedor": fornecedor,
        "cnpj": cnpj,
        "secretaria": _clean_text(data.get("secretaria"), 120),
        "secretario": secretario,
        "gestor": gestor,
        "gestor_cpf": gestor_cpf,
        "fiscal": fiscal,
        "fiscal_cpf": fiscal_cpf,
        "objeto": _clean_text(data.get("objeto")),
        "vigencia_texto": _clean_text(data.get("vigencia_texto")),
        "inicio_vigencia": inicio,
        "fim_vigencia": fim,
        "data_os": parse_date(data.get("data_os")),
        "processo_administrativo": _clean_text(data.get("processo_administrativo"), 80),
        "processo_execucao": _clean_text(data.get("processo_execucao"), 80),
        "audesp_licitacao": _clean_text(data.get("audesp_licitacao"), 80),
        "audesp_ajuste": _clean_text(data.get("audesp_ajuste")),
        "modalidade": _clean_text(data.get("modalidade"), 100),
        "valor_total": parse_money(data.get("valor_total")),
        "data_assinatura": parse_date(data.get("data_assinatura")),
        "data_publicacao": parse_date(data.get("data_publicacao")),
        "observacao": _clean_text(data.get("observacao")),
        "dias_para_vencimento": calculate_days_to_expiration(fim),
    }
    if secretario_cpf and not payload["observacao"]:
        payload["observacao"] = f"CPF secretario: {secretario_cpf}"
    has_useful_data = any(
        payload.get(key) for key in ("numero_contrato", "fornecedor", "objeto", "fim_vigencia")
    )
    if not has_useful_data:
        return None
    return payload


def _normalize_tipo_instrumento(value: Any) -> str:
    text = normalize_key(value)
    if text in {"ata", "arp", "ata_registro_preco", "ata_de_registro_de_precos"}:
        return "ata_registro_preco"
    return "contrato"


def _clean_text(value: Any, max_length: int | None = None) -> str | None:
    if _is_empty(value):
        return None
    text = re.sub(r"\s+", " ", str(value).strip())
    return text[:max_length] if max_length else text


def import_contracts(
    file_path: str | Path,
    db: Session | None = None,
    *,
    usuario: str | None = None,
) -> dict[str, Any]:
    path = Path(file_path)
    frame = _read_spreadsheet(path)
    result = ImportContractResult(0, 0, 0, 0, 0, [])
    created: list[Contract] = []

    for index, raw_row in frame.iterrows():
        result.linhas_processadas += 1
        try:
            payload = _payload_from_row(raw_row.to_dict())
            if payload is None:
                result.ignorados += 1
                continue
            if db is not None and payload.get("numero_contrato"):
                exists = db.scalar(
                    select(Contract.id).where(
                        Contract.tipo_instrumento == payload["tipo_instrumento"],
                        Contract.numero_contrato == payload["numero_contrato"],
                    )
                )
                if exists:
                    result.ignorados += 1
                    continue
            contract = Contract(**payload)
            if db is not None:
                db.add(contract)
            created.append(contract)
            result.importados += 1
        except Exception as exc:
            result.erros += 1
            result.linhas_com_erro += 1
            result.detalhes_erro.append({"linha": int(index) + 2, "erro": str(exc)})

    if db is not None:
        db.add(
            ContractImportLog(
                arquivo=path.name,
                usuario=usuario,
                linhas_processadas=result.linhas_processadas,
                linhas_importadas=result.importados,
                linhas_com_erro=result.linhas_com_erro,
                detalhes_erro=json.dumps(result.detalhes_erro, ensure_ascii=False),
            )
        )
        db.flush()
        result.sincronizados = _sync_contracts_to_contratos(db, created)
        db.commit()

    payload = result.as_dict()
    payload["contracts"] = created
    return payload


async def persist_upload(filename: str, content: bytes) -> Path:
    suffix = Path(filename).suffix.lower()
    if suffix not in {".xls", ".xlsx"}:
        raise ValueError("Arquivo deve ser .xls ou .xlsx")
    safe_name = re.sub(r"[^A-Za-z0-9_.-]", "_", Path(filename).name)
    path = Path(tempfile.gettempdir()) / f"argos_{datetime.utcnow():%Y%m%d%H%M%S%f}_{safe_name}"
    path.write_bytes(content)
    return path
