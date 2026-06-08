from fastapi.testclient import TestClient


def test_cria_lista_e_obtem_processo_lite(client: TestClient) -> None:
    payload = {
        "numero": "001/2026",
        "objeto": "Contratacao de solucao piloto",
        "area_requisitante": "Compras",
        "tipo_documento": "ETP",
    }

    create_response = client.post("/api/v1/processos-lite/", json=payload)

    assert create_response.status_code == 201
    created = create_response.json()
    assert created["id"] == 1
    assert created["status"] == "rascunho"
    assert created["numero"] == payload["numero"]

    list_response = client.get("/api/v1/processos-lite/")
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1

    detail_response = client.get("/api/v1/processos-lite/1")
    assert detail_response.status_code == 200
    assert detail_response.json()["objeto"] == payload["objeto"]


def test_retorna_404_para_processo_lite_inexistente(client: TestClient) -> None:
    response = client.get("/api/v1/processos-lite/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Processo nao encontrado"
