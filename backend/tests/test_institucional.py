from fastapi.testclient import TestClient


def test_obtem_e_atualiza_dados_institucionais(client: TestClient) -> None:
    initial = client.get("/api/v1/institucional")

    assert initial.status_code == 200
    assert initial.json()["nome_orgao"] == "Prefeitura Municipal"

    response = client.put(
        "/api/v1/institucional",
        json={
            "nome_orgao": "Prefeitura Municipal de Argos",
            "nome_municipio": "Argos",
            "uf": "SP",
            "cnpj": "12.345.678/0001-90",
            "endereco": "Praca Central, 100",
            "telefone": "(11) 3000-0000",
            "email": "administracao@argos.gov.br",
            "site": "https://argos.gov.br",
            "autoridade_nome": "Maria Gestora",
            "autoridade_cargo": "Prefeita",
            "responsavel_tecnico": "Joao Tecnico",
            "rodape_documentos": "Documento institucional de teste.",
            "logo_base64": None,
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["nome_orgao"] == "Prefeitura Municipal de Argos"
    assert data["nome_municipio"] == "Argos"
    assert data["uf"] == "SP"
    assert data["responsavel_tecnico"] == "Joao Tecnico"
