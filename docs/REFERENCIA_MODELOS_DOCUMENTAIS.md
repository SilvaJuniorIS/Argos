# Referencia de Modelos Documentais

Base analisada:

- `ETP.docx`
- `TR.docx`
- `Minuta Edital.docx`

Os documentos foram usados como referencia para padronizar a evolucao do ARGOS. O objetivo nao e copiar texto fixo, mas preservar estrutura, fluxo logico, campos obrigatorios e particularidades por tipo de objeto.

## Padroes Gerais

- Os documentos usam linguagem formal, objetiva e administrativa.
- Os titulos principais aparecem em caixa alta.
- Ha numeracao hierarquica recorrente em clausulas e subitens.
- Os itens do objeto costumam aparecer em tabelas.
- Para materiais graficos, as especificacoes devem preservar material, acabamento, dimensoes, arte/layout, unidade e quantidade.
- Quando o objeto exigir aprovacao visual, deve constar que a contratada enviara layout/arte final para aprovacao previa.
- Quando nao houver amostra fisica, o documento deve diferenciar amostra/catalogo de layout para aprovacao.
- Dados faltantes devem ficar como `A preencher`, sem invencao pela IA.

## ETP

Estrutura-base recomendada:

1. Introducao
2. Area requisitante
3. Objeto
4. Justificativa / descricao da necessidade
5. Previsao no Plano de Aquisicao Anual
6. Requisitos da aquisicao/contratacao
7. Estimativas de quantidades
8. Levantamento de mercado
9. Estimativa de valor
10. Descricao da solucao como um todo
11. Justificativa para parcelamento ou nao da solucao
12. Demonstrativo dos resultados pretendidos
13. Providencias previas
14. Contratacoes correlatas e/ou interdependentes
15. Impactos ambientais
16. Conclusao - viabilidade da contratacao
17. Lista de anexos

Particularidades observadas:

- Pode haver varias tabelas por grupo, unidade, equipamento ou local.
- As tabelas de quantitativos usam colunas como `Item`, `Descricao` e `Consumo Estimado`.
- As tabelas de estimativa de valor usam colunas como `ITEM`, `ESPECIFICACOES`, `QTDE`, `VALOR UNT.` e `VALOR TOTAL`.
- Para material grafico, a descricao tecnica inclui dimensoes em cm, material, acabamento e qualidade de impressao.

## TR

Estrutura-base recomendada:

1. Objeto
2. Area requisitante
3. Justificativa / fundamentacao da contratacao
4. Descricao da necessidade
5. Especificacoes e quantitativo
6. Requisitos para a aquisicao/contratacao
7. Subcontratacao
8. Exigencia de amostra e/ou catalogo
9. Obrigacoes do contratante
10. Obrigacoes do contratado
11. Modelo de execucao do objeto / prazos, condicoes e local
12. Modelo de gestao da ata de registro de preco/contrato
13. Do fiscal
14. Do gestor da ata/contrato
15. Pagamento
16. Forma e criterios de selecao do fornecedor
17. Forma de fornecimento
18. Exigencias de habilitacao
19. Estimativas do valor da contratacao
20. Adequacao orcamentaria

Particularidades observadas:

- O TR concentra especificacoes tecnicas, quantitativos, requisitos de execucao, obrigacoes e habilitacao.
- Para objetos com arte visual, deve haver regra de aprovacao previa de layout/arte final.
- A subcontratacao pode ser vedada expressamente quando a natureza do objeto exigir execucao direta.
- A exigencia de amostra pode ser dispensada, mas substituida por envio de layout/arte.
- Deve separar fiscal e gestor, quando essas funcoes forem informadas.

## Edital

Estrutura-base futura:

- Folha-resumo com edital, processo, pregao, contratante, valor, sessao, criterio, modo de disputa e tratamento ME/EPP.
- Corpo do edital com objeto, participacao, proposta, lances, julgamento, habilitacao, recursos, sancoes, impugnacao e disposicoes gerais.
- Anexos: TR, modelo de proposta, declaracoes, minuta contratual e termo de ciencia/notificacao.

Particularidades observadas:

- O edital incorpora ou referencia o TR.
- Ha campos de fornecedor, proposta comercial, dados bancarios e representante.
- A minuta contratual possui clausulas proprias: objeto, vigencia, execucao, subcontratacao, preco, pagamento, reajuste, obrigacoes, sancoes, extincao, dotacao, publicacao e foro.

## Evolucao Recomendada no ARGOS

- Criar templates estruturados por tipo documental em vez de depender apenas de texto livre.
- Gerar secoes em JSON e montar DOCX com estilos fixos.
- Permitir grupos de itens por unidade/local/equipamento.
- Adicionar campos de valor unitario, valor total, dotacao orcamentaria, fiscal, gestor, prazo de entrega, local de entrega e exigencia de layout/amostra.
- Criar tipo documental `EDITAL` em etapa futura, usando o TR gerado como anexo/base.
