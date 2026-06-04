from fastapi.testclient import TestClient


def test_cria_lista_e_busca_processo_licitatorio_por_id(client: TestClient) -> None:
    payload = {
        "objeto": "Aquisicao de notebooks para equipes tecnicas",
        "secretaria": "Secretaria de Administracao",
        "justificativa": "Modernizar os postos de trabalho e melhorar a produtividade.",
        "quantidade": "10",
        "unidade_medida": "unidade",
        "modalidade": "pregao eletronico",
        "prazo_execucao": "30 dias",
        "observacoes": "Entrega unica.",
        "tipo_documento": "ETP",
        "itens": [
            {
                "descricao": "Notebook corporativo",
                "quantidade": "10",
                "unidade_medida": "unidade",
                "observacoes": "Memoria minima de 16GB.",
            },
            {
                "descricao": "Mouse sem fio",
                "quantidade": "10",
                "unidade_medida": "unidade",
                "observacoes": None,
            },
        ],
    }

    create_response = client.post("/api/v1/processos-licitatorios/", json=payload)

    assert create_response.status_code == 201
    created = create_response.json()
    assert created["id"] == 1
    assert created["objeto"] == payload["objeto"]
    assert created["secretaria"] == payload["secretaria"]
    assert created["tipo_documento"] == "ETP"
    assert len(created["itens"]) == 2
    assert created["itens"][0]["descricao"] == "Notebook corporativo"
    assert created["itens"][1]["ordem"] == 2

    list_response = client.get("/api/v1/processos-licitatorios/")
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1

    detail_response = client.get("/api/v1/processos-licitatorios/1")
    assert detail_response.status_code == 200
    assert detail_response.json()["justificativa"] == payload["justificativa"]
    assert len(detail_response.json()["itens"]) == 2


def test_cria_item_de_compatibilidade_quando_payload_antigo_nao_envia_itens(
    client: TestClient,
) -> None:
    payload = {
        "objeto": "Contratacao de internet dedicada",
        "secretaria": "Secretaria de Governo",
        "justificativa": "Manter servicos digitais disponiveis.",
        "quantidade": "1",
        "unidade_medida": "servico",
        "modalidade": "pregao eletronico",
        "prazo_execucao": "12 meses",
        "observacoes": "Link principal.",
        "tipo_documento": "TR",
    }

    response = client.post("/api/v1/processos-licitatorios/", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert len(data["itens"]) == 1
    assert data["itens"][0]["descricao"] == payload["objeto"]
    assert data["itens"][0]["unidade_medida"] == "servico"


def test_retorna_404_para_processo_licitatorio_inexistente(client: TestClient) -> None:
    response = client.get("/api/v1/processos-licitatorios/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Processo licitatorio nao encontrado"


def test_dashboard_inicial_processos_licitatorios(client: TestClient) -> None:
    client.post(
        "/api/v1/processos-licitatorios/",
        json={
            "objeto": "Contratacao de plataforma de gestao",
            "secretaria": "Secretaria de Administracao",
            "justificativa": "Organizar documentos preparatorios.",
            "quantidade": "1",
            "unidade_medida": "servico",
            "modalidade": "pregao eletronico",
            "prazo_execucao": "12 meses",
            "observacoes": None,
            "tipo_documento": "ETP",
        },
    )

    response = client.get("/api/v1/processos-licitatorios/dashboard")

    assert response.status_code == 200
    data = response.json()
    assert data["total_processos"] == 1
    assert data["total_documentos_gerados"] == 0
    assert data["total_rascunho"] == 1
    assert data["total_gerado"] == 0
    assert data["total_revisado"] == 0
    assert data["ultimos_processos"][0]["status"] == "Rascunho"


def test_rejeita_campos_excessivamente_longos(client: TestClient) -> None:
    response = client.post(
        "/api/v1/processos-licitatorios/",
        json={
            "objeto": "x" * 2001,
            "secretaria": "Secretaria de Administracao",
            "justificativa": "Justificativa valida",
            "tipo_documento": "ETP",
        },
    )

    assert response.status_code == 422
