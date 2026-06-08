# ARGOS - Estrutura para MVP

## Objetivo

Esta reorganizacao prepara o projeto para o MVP ARGOS, focado em inteligencia documental para a fase preparatoria de compras publicas.

O MVP Lite deve permitir:

1. Cadastro de processo.
2. Preenchimento de dados basicos.
3. Geracao assistida de ETP, Termo de Referencia ou Minuta de Edital com IA.
4. Edicao do texto gerado.
5. Exportacao em DOCX.

## Estrutura

```text
backend/
  app/          API FastAPI do ARGOS
  migrations/   migracoes Alembic
  scripts/      rotinas administrativas
  tests/        testes automatizados
  storage/      arquivos gerados e anexos locais

frontend/
  argos-web/ aplicacao React + Vite do ARGOS

prompts/        prompts-base para documentos preparatorios
templates/      modelos de documentos DOCX
exports/        documentos exportados localmente
docs/           documentacao tecnica e planejamento
```

## Decisao Arquitetural

A menor arquitetura viavel e concentrar a API FastAPI em `backend/app` nos fluxos do ARGOS: processos licitatorios, modelos institucionais, geracao assistida, revisao e exportacao de documentos.

## Proximos Passos Tecnicos

1. Criar modelos SQLite/PostgreSQL para processo e documento gerado.
2. Criar endpoints REST para cadastro, listagem, detalhe e atualizacao de processos.
3. Criar servico de IA via LLM Gateway usando prompts especializados.
4. Criar exportador DOCX com `python-docx`.
5. Criar telas React para lista de processos, formulario, editor e download.
6. Adicionar testes de API para fluxo minimo.
7. Preparar deploy no Render apontando para `backend/`.
