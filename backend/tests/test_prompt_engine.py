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
        "Descricao da necessidade",
        "Area requisitante",
        "Requisitos da contratacao",
        "Levantamento de mercado",
        "Descricao da solucao escolhida",
        "Estimativa das quantidades",
        "Estimativa do valor",
        "Justificativa do parcelamento ou nao",
        "Resultados pretendidos",
        "Providencias previas",
        "Contratacoes correlatas",
        "Impactos ambientais",
        "Riscos",
        "Conclusao",
    ]
    for secao in secoes_obrigatorias:
        assert secao in prompt
    assert "tom robotico" in prompt


def test_gera_prompt_tr_estruturado() -> None:
    prompt = gerar_prompt_tr(_processo("TR"))

    assert "Termo de Referencia (TR)" in prompt
    assert "Lei 14.133/2021" in prompt
    assert "Especificacoes" in prompt
    assert "Quantitativos" in prompt
    assert "Condicoes de execucao" in prompt
    assert "Gestao e fiscalizacao" in prompt
    assert "Obrigacoes da contratada" in prompt
    assert "Criterio de julgamento" in prompt
    assert "Estimativa de valor" in prompt
    assert "Fundamentacao legal" in prompt
    assert "tom robotico" in prompt


def test_roteia_prompt_pelo_tipo_documento() -> None:
    assert "Estudo Tecnico Preliminar" in gerar_prompt_documento(_processo("ETP"))
    assert "Termo de Referencia" in gerar_prompt_documento(_processo("TR"))


def test_rejeita_tipo_documento_invalido() -> None:
    processo = _processo("ETP")
    processo.tipo_documento = "OUTRO"

    with pytest.raises(ValueError, match="tipo_documento deve ser ETP ou TR"):
        gerar_prompt_documento(processo)
