from fastapi.testclient import TestClient
from zipfile import ZipFile
from io import BytesIO

from app.services import documento_gerado_service
from app.services.llm_gateway.types import LLMResponse


def _llm_response(content: str = "Texto inicial", model: str = "modelo-teste") -> LLMResponse:
    return LLMResponse(
        content=content,
        model=model,
        provider="teste",
        usage={"total_tokens": 10},
        raw_response={"id": "mock"},
    )


def _criar_processo(client: TestClient, tipo_documento: str = "ETP") -> int:
    response = client.post(
        "/api/v1/processos-licitatorios/",
        json={
            "objeto": "Aquisicao de notebooks",
            "secretaria": "Secretaria de Administracao",
            "justificativa": "Modernizar os postos de trabalho.",
            "quantidade": "10",
            "unidade_medida": "unidade",
            "modalidade": "pregao eletronico",
            "prazo_execucao": "30 dias",
            "observacoes": "Entrega unica.",
            "tipo_documento": tipo_documento,
            "itens": [
                {
                    "descricao": "Notebook corporativo",
                    "quantidade": "10",
                    "unidade_medida": "unidade",
                    "observacoes": None,
                }
            ],
        },
    )
    assert response.status_code == 201
    return response.json()["id"]


def test_gera_e_salva_documento_com_llm_gateway_mockado(
    client: TestClient,
    monkeypatch,
) -> None:
    processo_id = _criar_processo(client, "ETP")
    monkeypatch.setattr(
        documento_gerado_service,
        "_gerar_texto_com_llm",
        lambda prompt: _llm_response(f"Documento gerado a partir de: {prompt[:40]}"),
    )

    response = client.post(
        "/api/v1/documentos/gerar",
        json={"processo_id": processo_id, "tipo_documento": "ETP"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["processo_id"] == processo_id
    assert data["tipo_documento"] == "ETP"
    assert data["modelo"] == "modelo-teste"
    assert "Documento gerado" in data["conteudo"]

    detail_response = client.get(f"/api/v1/documentos/gerados/{data['id']}")
    assert detail_response.status_code == 200
    assert detail_response.json()["conteudo"] == data["conteudo"]


def test_atualiza_documento_gerado(client: TestClient, monkeypatch) -> None:
    processo_id = _criar_processo(client, "TR")
    monkeypatch.setattr(
        documento_gerado_service,
        "_gerar_texto_com_llm",
        lambda prompt: _llm_response(),
    )
    created = client.post(
        "/api/v1/documentos/gerar",
        json={"processo_id": processo_id, "tipo_documento": "TR"},
    ).json()

    response = client.patch(
        f"/api/v1/documentos/gerados/{created['id']}",
        json={"conteudo": "Texto revisado pela equipe tecnica."},
    )

    assert response.status_code == 200
    assert response.json()["conteudo"] == "Texto revisado pela equipe tecnica."
    assert response.json()["revisado_em"] is not None

    dashboard = client.get("/api/v1/processos-licitatorios/dashboard")
    assert dashboard.status_code == 200
    assert dashboard.json()["total_revisado"] == 1
    assert dashboard.json()["ultimos_processos"][0]["status"] == "Revisado"


def test_rejeita_atualizacao_vazia(client: TestClient, monkeypatch) -> None:
    processo_id = _criar_processo(client, "ETP")
    monkeypatch.setattr(
        documento_gerado_service,
        "_gerar_texto_com_llm",
        lambda prompt: _llm_response(),
    )
    created = client.post(
        "/api/v1/documentos/gerar",
        json={"processo_id": processo_id},
    ).json()

    response = client.patch(
        f"/api/v1/documentos/gerados/{created['id']}",
        json={"conteudo": "   "},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Conteudo do documento nao pode ficar vazio"


def test_exporta_documento_gerado_em_docx(client: TestClient, monkeypatch) -> None:
    processo_id = _criar_processo(client, "ETP")
    client.put(
        "/api/v1/institucional",
        json={
            "nome_orgao": "Prefeitura Municipal de Argos",
            "nome_municipio": "Argos",
            "uf": "SP",
            "cnpj": "12.345.678/0001-90",
            "endereco": "Praca Central, 100",
            "telefone": None,
            "email": None,
            "site": None,
            "autoridade_nome": None,
            "autoridade_cargo": None,
            "responsavel_tecnico": "Joao Tecnico",
            "rodape_documentos": "Rodape institucional configurado.",
            "logo_base64": None,
        },
    )
    monkeypatch.setattr(
        documento_gerado_service,
        "_gerar_texto_com_llm",
        lambda prompt: _llm_response(
            "1. Objeto\n"
            "Texto revisado do documento.\n"
            "| Item | Descricao | Quantidade |\n"
            "| --- | --- | --- |\n"
            "| 1 | Item preservado | 10 |\n"
        ),
    )
    created = client.post(
        "/api/v1/documentos/gerar",
        json={"processo_id": processo_id},
    ).json()

    response = client.get(f"/api/v1/documentos/gerados/{created['id']}/exportar-docx")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith(
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
    with ZipFile(BytesIO(response.content)) as docx_zip:
        assert "word/document.xml" in docx_zip.namelist()
        assert "word/header1.xml" in docx_zip.namelist()
        document_xml = docx_zip.read("word/document.xml").decode("utf-8")
        header_xml = docx_zip.read("word/header1.xml").decode("utf-8")
        footer_xml = docx_zip.read("word/footer1.xml").decode("utf-8")
        assert "Prefeitura Municipal de Argos" in header_xml
        assert "Estudo Tecnico Preliminar" in document_xml
        assert "Minuta padronizada gerada com apoio do ARGOS" in document_xml
        assert "Joao Tecnico" in document_xml
        assert "Rodape institucional configurado." in footer_xml
        assert "1. Objeto" in document_xml
        assert "Item preservado" in document_xml
        assert "<w:tbl>" in document_xml


def test_retorna_404_para_processo_inexistente(client: TestClient) -> None:
    response = client.post("/api/v1/documentos/gerar", json={"processo_id": 999})

    assert response.status_code == 404
    assert response.json()["detail"] == "Processo licitatorio nao encontrado"


def test_rejeita_id_de_processo_invalido_para_geracao(client: TestClient) -> None:
    response = client.post("/api/v1/documentos/gerar", json={"processo_id": 0})

    assert response.status_code == 422


def test_retorna_503_quando_llm_nao_configurado(
    client: TestClient,
    monkeypatch,
) -> None:
    processo_id = _criar_processo(client, "TR")
    monkeypatch.setattr(
        documento_gerado_service,
        "_gerar_texto_com_llm",
        lambda prompt: (_ for _ in ()).throw(
            documento_gerado_service.LLMDocumentoConfigurationError(
                "Chave de API nao configurada para openrouter"
            )
        ),
    )

    response = client.post(
        "/api/v1/documentos/gerar",
        json={"processo_id": processo_id, "tipo_documento": "TR"},
    )

    assert response.status_code == 503
    assert "Chave de API" in response.json()["detail"]
