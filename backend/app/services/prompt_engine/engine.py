from dataclasses import dataclass
from decimal import Decimal
from textwrap import dedent

from app.models.processo_licitatorio import ProcessoLicitatorio
from app.schemas.processo_licitatorio import ProcessoLicitatorioCreate, ProcessoLicitatorioRead

ProcessoPromptInput = ProcessoLicitatorio | ProcessoLicitatorioCreate | ProcessoLicitatorioRead


@dataclass(frozen=True)
class DadosItemPrompt:
    descricao: str
    quantidade: Decimal | int | str | None
    unidade_medida: str | None
    observacoes: str | None


@dataclass(frozen=True)
class DadosProcessoPrompt:
    objeto: str
    secretaria: str
    justificativa: str
    quantidade: Decimal | int | str | None
    unidade_medida: str | None
    modalidade: str | None
    prazo_execucao: str | None
    observacoes: str | None
    tipo_documento: str
    itens: list[DadosItemPrompt]


@dataclass(frozen=True)
class DadosInstitucionaisPrompt:
    nome_orgao: str
    nome_municipio: str | None
    uf: str | None
    cnpj: str | None
    endereco: str | None
    autoridade_nome: str | None
    autoridade_cargo: str | None
    responsavel_tecnico: str | None


def gerar_prompt_documento(processo: ProcessoPromptInput, institucional=None) -> str:
    dados = _normalizar_dados(processo)
    dados_institucionais = _normalizar_institucional(institucional)
    tipo = dados.tipo_documento.upper()
    if tipo == "ETP":
        return gerar_prompt_etp(processo, dados_institucionais)
    if tipo == "TR":
        return gerar_prompt_tr(processo, dados_institucionais)
    raise ValueError("tipo_documento deve ser ETP ou TR")


def gerar_prompt_etp(
    processo: ProcessoPromptInput,
    institucional: DadosInstitucionaisPrompt | None = None,
) -> str:
    dados = _normalizar_dados(processo)
    return _limpar_prompt(
        f"""
        Voce e um especialista em planejamento de contratacoes publicas.

        Elabore um Estudo Tecnico Preliminar (ETP) com linguagem tecnica humana,
        profissional e objetiva, observando a Lei 14.133/2021.

        Dados do processo:
        {_formatar_dados(dados)}

        Dados institucionais:
        {_formatar_institucional(institucional)}

        Regras de redacao:
        - Escreva como uma minuta tecnica elaborada por servidor experiente, com fluidez,
          contexto e transicoes naturais entre as ideias.
        - Use texto claro, institucional e adequado a revisao por servidor publico.
        - Evite repeticoes, frases genericas, tom robotico e conclusoes sem fundamento nos
          dados fornecidos.
        - Nao invente informacoes. Quando faltar dado relevante, escreva "A preencher".
        - Mantenha coerencia entre necessidade, solucao, quantidade, prazo e modalidade.
        - Indique pontos que exigem validacao tecnica, juridica ou orcamentaria.
        - Nao produza uma lista seca de topicos. Desenvolva paragrafos objetivos em cada secao.
        - Use os dados institucionais apenas quando fizer sentido. Nao repita cabecalho,
          brasao, endereco ou rodape no corpo do texto, pois o sistema ja aplica papel timbrado.
        - Quando citar responsavel, autoridade, orgao ou municipio, use exatamente os dados
          institucionais informados.

        Estrutura obrigatoria do ETP:
        1. Descricao da necessidade
        2. Area requisitante
        3. Requisitos da contratacao
        4. Levantamento de mercado
        5. Descricao da solucao escolhida
        6. Estimativa das quantidades
        7. Estimativa do valor
        8. Justificativa do parcelamento ou nao
        9. Resultados pretendidos
        10. Providencias previas
        11. Contratacoes correlatas
        12. Impactos ambientais
        13. Riscos
        14. Conclusao

        Saida esperada:
        - Titulo do documento.
        - Secoes numeradas exatamente na ordem acima.
        - Paragrafos completos, sem listas vazias.
        - Campos pendentes claramente marcados como "A preencher".
        - Ao mencionar riscos, diferencie risco operacional, tecnico, orcamentario ou juridico
          quando os dados permitirem.
        """
    )


def gerar_prompt_tr(
    processo: ProcessoPromptInput,
    institucional: DadosInstitucionaisPrompt | None = None,
) -> str:
    dados = _normalizar_dados(processo)
    return _limpar_prompt(
        f"""
        Voce e um especialista em documentos preparatorios de licitacoes publicas.

        Elabore um Termo de Referencia (TR) com linguagem tecnica humana,
        profissional e objetiva, observando a Lei 14.133/2021.

        Dados do processo:
        {_formatar_dados(dados)}

        Dados institucionais:
        {_formatar_institucional(institucional)}

        Regras de redacao:
        - Escreva como uma minuta tecnica elaborada por servidor experiente, com linguagem
          humana, precisa e institucional.
        - Use linguagem direta e adequada para processo administrativo.
        - Evite repeticao de ideias, excesso de adjetivos, tom robotico e texto burocratico
          sem conteudo.
        - Nao invente informacoes. Quando faltar dado relevante, escreva "A preencher".
        - Organize o texto para facilitar revisao tecnica, juridica e administrativa.
        - Mantenha consistencia entre objeto, justificativa, quantidade, unidade e prazo.
        - Nao produza uma lista seca de topicos. Desenvolva paragrafos objetivos em cada secao.
        - Use os dados institucionais apenas quando fizer sentido. Nao repita cabecalho,
          brasao, endereco ou rodape no corpo do texto, pois o sistema ja aplica papel timbrado.
        - Quando citar responsavel, autoridade, orgao ou municipio, use exatamente os dados
          institucionais informados.

        Estrutura obrigatoria do Termo de Referencia:
        1. Objeto
        2. Justificativa
        3. Especificacoes
        4. Quantitativos
        5. Condicoes de execucao
        6. Prazo
        7. Gestao e fiscalizacao
        8. Criterios de medicao e pagamento
        9. Obrigacoes da contratada
        10. Obrigacoes da contratante
        11. Sancoes
        12. Criterio de julgamento
        13. Estimativa de valor
        14. Fundamentacao legal

        Saida esperada:
        - Titulo do documento.
        - Secoes numeradas exatamente na ordem acima.
        - Paragrafos completos e tecnicamente consistentes.
        - Campos pendentes claramente marcados como "A preencher".
        - Quando houver lacunas juridicas, tecnicas ou financeiras, sinalize no proprio item
          correspondente, sem criar uma secao extra fora da estrutura obrigatoria.
        """
    )


def _normalizar_dados(processo: ProcessoPromptInput) -> DadosProcessoPrompt:
    return DadosProcessoPrompt(
        objeto=_valor(processo.objeto),
        secretaria=_valor(processo.secretaria),
        justificativa=_valor(processo.justificativa),
        quantidade=processo.quantidade,
        unidade_medida=_valor_opcional(processo.unidade_medida),
        modalidade=_valor_opcional(processo.modalidade),
        prazo_execucao=_valor_opcional(processo.prazo_execucao),
        observacoes=_valor_opcional(processo.observacoes),
        tipo_documento=_valor(processo.tipo_documento),
        itens=_normalizar_itens(processo),
    )


def _formatar_dados(dados: DadosProcessoPrompt) -> str:
    linhas = [
        ("Objeto", dados.objeto),
        ("Secretaria", dados.secretaria),
        ("Justificativa", dados.justificativa),
        ("Itens", _formatar_itens(dados)),
        ("Modalidade", dados.modalidade or "A preencher"),
        ("Prazo de execucao", dados.prazo_execucao or "A preencher"),
        ("Observacoes", dados.observacoes or "A preencher"),
    ]
    return "\n".join(f"- {rotulo}: {valor}" for rotulo, valor in linhas)


def _normalizar_institucional(institucional) -> DadosInstitucionaisPrompt | None:
    if institucional is None:
        return None
    return DadosInstitucionaisPrompt(
        nome_orgao=_valor(getattr(institucional, "nome_orgao", None)),
        nome_municipio=_valor_opcional(getattr(institucional, "nome_municipio", None)),
        uf=_valor_opcional(getattr(institucional, "uf", None)),
        cnpj=_valor_opcional(getattr(institucional, "cnpj", None)),
        endereco=_valor_opcional(getattr(institucional, "endereco", None)),
        autoridade_nome=_valor_opcional(getattr(institucional, "autoridade_nome", None)),
        autoridade_cargo=_valor_opcional(getattr(institucional, "autoridade_cargo", None)),
        responsavel_tecnico=_valor_opcional(getattr(institucional, "responsavel_tecnico", None)),
    )


def _formatar_institucional(dados: DadosInstitucionaisPrompt | None) -> str:
    if dados is None:
        return "- Orgao: A preencher"
    municipio = dados.nome_municipio or "A preencher"
    if dados.uf:
        municipio = f"{municipio}/{dados.uf}"
    linhas = [
        ("Orgao", dados.nome_orgao),
        ("Municipio/UF", municipio),
        ("CNPJ", dados.cnpj or "A preencher"),
        ("Endereco", dados.endereco or "A preencher"),
        ("Autoridade", _formatar_nome_cargo(dados.autoridade_nome, dados.autoridade_cargo)),
        ("Responsavel tecnico", dados.responsavel_tecnico or "A preencher"),
    ]
    return "\n".join(f"- {rotulo}: {valor}" for rotulo, valor in linhas)


def _formatar_nome_cargo(nome: str | None, cargo: str | None) -> str:
    if nome and cargo:
        return f"{nome} - {cargo}"
    return nome or cargo or "A preencher"


def _normalizar_itens(processo: ProcessoPromptInput) -> list[DadosItemPrompt]:
    itens = getattr(processo, "itens", None) or []
    if itens:
        return [
            DadosItemPrompt(
                descricao=_valor(item.descricao),
                quantidade=item.quantidade,
                unidade_medida=_valor_opcional(item.unidade_medida),
                observacoes=_valor_opcional(item.observacoes),
            )
            for item in itens
        ]
    return [
        DadosItemPrompt(
            descricao=_valor(processo.objeto),
            quantidade=processo.quantidade,
            unidade_medida=_valor_opcional(processo.unidade_medida),
            observacoes=_valor_opcional(processo.observacoes),
        )
    ]


def _formatar_itens(dados: DadosProcessoPrompt) -> str:
    if not dados.itens:
        return _formatar_quantidade(dados.quantidade, dados.unidade_medida)
    linhas = []
    for index, item in enumerate(dados.itens, start=1):
        quantidade = _formatar_quantidade(item.quantidade, item.unidade_medida)
        observacoes = f"; observacoes: {item.observacoes}" if item.observacoes else ""
        linhas.append(f"{index}. {item.descricao} - {quantidade}{observacoes}")
    return "\n  " + "\n  ".join(linhas)


def _formatar_quantidade(
    quantidade: Decimal | int | str | None,
    unidade_medida: str | None,
) -> str:
    if quantidade in (None, ""):
        return "A preencher"
    unidade = unidade_medida or "A preencher"
    return f"{quantidade} {unidade}"


def _valor(value: str | None) -> str:
    if value is None or not str(value).strip():
        return "A preencher"
    return str(value).strip()


def _valor_opcional(value: str | None) -> str | None:
    if value is None or not str(value).strip():
        return None
    return str(value).strip()


def _limpar_prompt(prompt: str) -> str:
    return "\n".join(line.strip() for line in dedent(prompt).strip().splitlines())
