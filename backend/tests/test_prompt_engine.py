import pytest

from app.schemas.processo_licitatorio import ProcessoLicitatorioCreate
from app.services.prompt_engine import gerar_prompt_documento, gerar_prompt_etp, gerar_prompt_tr


def _processo(tipo_documento: str = "ETP") -> ProcessoLicitatorioCreate:
    return ProcessoLicitatorioCreate(
        objeto="Aquisicao de notebooks para equipes tecnicas",
        secretaria="Secretaria de Administracao",
        justificativa="Modernizar os postos de trabalho e melhorar a produtividade.",
        quantidade=10,
        unidade_medida="unidade",
        modalidade="pregao eletronico",
        prazo_execucao="30 dias",
        observacoes="Entrega unica.",
        tipo_documento=tipo_documento,
        itens=[
            {
                "descricao": "Notebook corporativo",
                "quantidade": 10,
                "unidade_medida": "unidade",
                "observacoes": "Memoria minima de 16GB.",
            },
            {
                "descricao": "Mouse sem fio",
                "quantidade": 10,
                "unidade_medida": "unidade",
                "observacoes": None,
            },
        ],
    )


def test_gera_prompt_etp_estruturado() -> None:
    prompt = gerar_prompt_etp(_processo("ETP"))

    assert "Estudo Tecnico Preliminar (ETP)" in prompt
    assert "Lei 14.133/2021" in prompt
    assert "Aquisicao de notebooks" in prompt
    assert "Notebook corporativo - 10 unidade" in prompt
    assert "Mouse sem fio - 10 unidade" in prompt
    secoes_obrigatorias = [
        "Introducao",
        "Area requisitante",
        "Objeto",
        "Justificativa / descricao da necessidade",
        "Previsao no Plano de Aquisicao Anual",
        "Requisitos da aquisicao/contratacao",
        "Estimativas de quantidades",
        "Levantamento de mercado",
        "Estimativa de valor",
        "Descricao da solucao como um todo",
        "Justificativa para parcelamento ou nao da solucao",
        "Demonstrativo dos resultados pretendidos",
        "Providencias previas",
        "Contratacoes correlatas e/ou interdependentes",
        "Impactos ambientais",
        "Conclusao - viabilidade da contratacao",
        "Lista de anexos",
    ]
    for secao in secoes_obrigatorias:
        assert secao in prompt
    assert "Item, Descricao, Consumo Estimado" in prompt
    assert "tom robotico" in prompt


def test_gera_prompt_tr_estruturado() -> None:
    prompt = gerar_prompt_tr(_processo("TR"))

    assert "Termo de Referencia (TR)" in prompt
    assert "Lei 14.133/2021" in prompt
    assert "Area requisitante" in prompt
    assert "Justificativa / fundamentacao da contratacao" in prompt
    assert "Especificacoes e quantitativo" in prompt
    assert "Subcontratacao" in prompt
    assert "Exigencia de amostra e/ou catalogo" in prompt
    assert "Obrigacoes do contratante" in prompt
    assert "Obrigacoes do contratado" in prompt
    assert "Modelo de execucao do objeto" in prompt
    assert "Do fiscal" in prompt
    assert "Do gestor da ata/contrato" in prompt
    assert "Exigencias de habilitacao" in prompt
    assert "Adequacao orcamentaria" in prompt
    assert "layout/arte" in prompt
    assert "tom robotico" in prompt


def test_roteia_prompt_pelo_tipo_documento() -> None:
    assert "Estudo Tecnico Preliminar" in gerar_prompt_documento(_processo("ETP"))
    assert "Termo de Referencia" in gerar_prompt_documento(_processo("TR"))


def test_prompt_inclui_dados_institucionais() -> None:
    class Institucional:
        nome_orgao = "Prefeitura Municipal de Argos"
        nome_municipio = "Argos"
        uf = "SP"
        cnpj = "12.345.678/0001-90"
        endereco = "Praca Central, 100"
        autoridade_nome = "Maria Gestora"
        autoridade_cargo = "Prefeita"
        responsavel_tecnico = "Joao Tecnico"

    prompt = gerar_prompt_documento(_processo("TR"), Institucional())

    assert "Prefeitura Municipal de Argos" in prompt
    assert "Argos/SP" in prompt
    assert "Joao Tecnico" in prompt
    assert "papel timbrado" in prompt


def test_rejeita_tipo_documento_invalido() -> None:
    processo = _processo("ETP")
    processo.tipo_documento = "OUTRO"

    with pytest.raises(ValueError, match="tipo_documento deve ser ETP ou TR"):
        gerar_prompt_documento(processo)
