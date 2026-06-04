# ARGOS - Estrutura para MVP

## Objetivo

Esta reorganizacao prepara o projeto para o MVP ARGOS sem descartar o sistema atual de acompanhamento de contratos.

O MVP Lite deve permitir:

1. Cadastro de processo.
2. Preenchimento de dados basicos.
3. Geracao assistida de ETP ou Termo de Referencia com IA.
4. Edicao do texto gerado.
5. Exportacao em DOCX.

## Estrutura

```text
backend/
  app/          API FastAPI atual
  migrations/   migracoes Alembic
  scripts/      rotinas administrativas
  tests/        testes automatizados
  storage/      arquivos usados pela API atual

frontend/
  fiscalbot-web/ aplicacao React + Vite atual

prompts/        prompts-base para ETP e TR
templates/      modelos de documentos DOCX
exports/        documentos exportados localmente
docs/           documentacao tecnica e planejamento
```

## Decisao Arquitetural

A menor arquitetura viavel e evoluir a API FastAPI existente dentro de `backend/app`, adicionando um modulo isolado para o ARGOS. O frontend atual fica preservado em `frontend/fiscalbot-web` e pode receber uma nova area de navegacao para processos, geracao de documentos e exportacao.

## Proximos Passos Tecnicos

1. Criar modelos SQLite/PostgreSQL para processo e documento gerado.
2. Criar endpoints REST para cadastro, listagem, detalhe e atualizacao de processos.
3. Criar servico de IA via LLM Gateway usando prompts de `prompts/`.
4. Criar exportador DOCX com `python-docx`.
5. Criar telas React para lista de processos, formulario, editor e download.
6. Adicionar testes de API para fluxo minimo.
7. Preparar deploy no Render apontando para `backend/`.
