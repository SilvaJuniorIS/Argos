from uuid import UUID

from fastapi import UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.core import storage
from app.models.contract import Contract, ContractAttachment
from app.models.user import User
from app.schemas.anexo import ContractAttachmentOut
from app.services import log_auditoria


def _to_out(attachment: ContractAttachment) -> ContractAttachmentOut:
    return ContractAttachmentOut(
        id=attachment.id,
        contract_id=attachment.contract_id,
        nome_arquivo=attachment.nome_arquivo,
        tipo=attachment.tipo,
        versao=attachment.versao,
        uploaded_by=attachment.uploaded_by,
        created_at=attachment.created_at,
        url=f"/api/v1/contracts/documentos/{attachment.id}/download",
    )


def _get_contract(db: Session, contract_id: UUID) -> Contract:
    contract = db.get(Contract, contract_id)
    if contract is None:
        raise ValueError("Registro nao encontrado")
    return contract


async def upload(
    db: Session,
    contract_id: UUID,
    file: UploadFile,
    tipo: str,
    versao: int | None,
    user: User,
) -> ContractAttachmentOut:
    _get_contract(db, contract_id)
    caminho = await storage.save_file(file, f"contracts/{contract_id}")
    attachment = ContractAttachment(
        contract_id=contract_id,
        tipo=tipo,
        nome_arquivo=file.filename or "arquivo",
        caminho_storage=caminho,
        content_type=file.content_type,
        versao=versao or 1,
        uploaded_by_id=user.id,
    )
    db.add(attachment)
    db.flush()
    log_auditoria.registrar(
        db,
        user_id=user.id,
        entidade="contract_attachments",
        entidade_id=attachment.id,
        acao="upload",
        depois={
            "contract_id": str(contract_id),
            "arquivo": attachment.nome_arquivo,
            "tipo": tipo,
        },
    )
    db.commit()
    loaded = db.scalar(
        select(ContractAttachment)
        .options(joinedload(ContractAttachment.uploaded_by))
        .where(ContractAttachment.id == attachment.id)
    )
    return _to_out(loaded)  # type: ignore[arg-type]


def list_by_contract(db: Session, contract_id: UUID) -> list[ContractAttachmentOut]:
    _get_contract(db, contract_id)
    attachments = db.scalars(
        select(ContractAttachment)
        .options(joinedload(ContractAttachment.uploaded_by))
        .where(ContractAttachment.contract_id == contract_id)
        .order_by(ContractAttachment.created_at.desc())
    ).all()
    return [_to_out(attachment) for attachment in attachments]


def get_attachment(db: Session, attachment_id: int) -> ContractAttachment:
    attachment = db.get(ContractAttachment, attachment_id)
    if attachment is None:
        raise ValueError("Arquivo nao encontrado")
    return attachment


def delete(db: Session, attachment_id: int, user: User) -> None:
    attachment = get_attachment(db, attachment_id)
    antes = {
        "contract_id": str(attachment.contract_id),
        "arquivo": attachment.nome_arquivo,
        "caminho": attachment.caminho_storage,
    }
    storage.delete_file(attachment.caminho_storage)
    db.delete(attachment)
    log_auditoria.registrar(
        db,
        user_id=user.id,
        entidade="contract_attachments",
        entidade_id=attachment_id,
        acao="excluir",
        antes=antes,
    )
    db.commit()
