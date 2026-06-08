# ARGOS

ARGOS e um produto da AtlasNex para apoiar equipes publicas na elaboracao inicial de documentos de contratacao com base na Lei 14.133/2021.

O produto organiza dados de processos licitatorios, gera minutas de Estudo Tecnico Preliminar (ETP) e Termo de Referencia (TR) com apoio de IA, permite revisao humana no navegador e exporta o resultado em DOCX.

## Problema que Resolve

Equipes de compras publicas frequentemente precisam produzir documentos preparatorios com prazos curtos, dados dispersos e grande exigencia de consistencia juridica, tecnica e administrativa.

O ARGOS reduz o trabalho inicial de estruturacao desses documentos ao:

- padronizar a coleta de informacoes do processo;
- organizar itens, quantidades e justificativas;
- gerar uma primeira minuta tecnicamente estruturada;
- acelerar a revisao interna;
- preservar uma trilha simples entre cadastro, geracao, revisao e exportacao.

## Publico-Alvo

- Secretarias municipais e estaduais;
- setores de compras, licitacoes e contratos;
- fiscais e gestores de contratos;
- equipes de planejamento da contratacao;
- consultorias que apoiam orgaos publicos;
- servidores responsaveis por ETP, TR e documentos preparatorios.

## Funcionalidades do MVP

- Dashboard inicial com totais, status e ultimos processos;
- cadastro de processo licitatorio;
- suporte a multiplos itens por processo;
- geracao de ETP com IA;
- geracao de Termo de Referencia com IA;
- prompt estruturado com base na Lei 14.133/2021;
- editor simples para revisao humana;
- salvamento de alteracoes;
- status do processo: `Rascunho`, `Gerado`, `Revisado`;
- copia do texto gerado;
- exportacao em DOCX com cabecalho institucional;
- API documentada automaticamente em `/docs`;
- estrutura pronta para deploy no Render.

## Aviso Importante

Os documentos gerados pelo ARGOS sao minutas de apoio.

Todo ETP, Termo de Referencia ou documento produzido pela ferramenta deve passar por revisao humana especializada antes de uso oficial, incluindo validacao tecnica, juridica, orcamentaria e administrativa pelo orgao responsavel.

O ARGOS nao substitui parecer juridico, controle interno, fiscalizacao tecnica ou decisao administrativa.

## Stack Utilizada

Backend:

- Python;
- FastAPI;
- SQLAlchemy;
- SQLite;
- Pydantic;
- LLM Gateway com OpenRouter;
- python-docx;
- Uvicorn;
- Pytest.

Frontend:

- React;
- Vite;
- TypeScript;
- Axios;
- React Router;
- CSS modular no projeto.

Deploy:

- Render Web Service para backend;
- Render Static Site para frontend;
- disco persistente para SQLite;
- `render.yaml` como Blueprint.

## Estrutura do Projeto

```text
backend/                 API FastAPI, models, schemas, services e testes
frontend/argos-web/  Aplicacao React + Vite do ARGOS
prompts/                 Prompts-base para ETP e TR
templates/               Modelos e referencias
exports/                 Arquivos exportados localmente
docs/                    Documentacao tecnica
render.yaml              Blueprint para Render
```

## Como Rodar Localmente

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload --host 0.0.0.0 --port 8002
```

URLs do backend:

- API: `http://localhost:8002`
- Documentacao: `http://localhost:8002/docs`
- Health check: `http://localhost:8002/health`

### Configurar IA

Edite `backend/.env` e informe:

```env
LLM_PROVIDER=openrouter
LLM_FALLBACK_PROVIDER=
LLM_TIMEOUT_SECONDS=45

OPENROUTER_API_KEY=sk-or-sua-chave
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_DEFAULT_MODEL=openrouter/free
OPENROUTER_HTTP_REFERER=http://localhost:5175
OPENROUTER_X_TITLE=ARGOS
```

O ARGOS usa um LLM Gateway interno. Neste primeiro momento, o provedor configurado e somente o OpenRouter. A OpenAI pode ser ativada no futuro como provedor principal ou fallback, mas nao e necessaria para o deploy inicial.

As chaves de IA devem ficar somente no backend. Nunca exponha `OPENROUTER_API_KEY` no frontend.

### Frontend

```bash
cd frontend\argos-web
npm ci
copy .env.example .env
npm run dev
```

Configure `frontend/argos-web/.env`:

```env
VITE_API_URL=http://localhost:8002
```

URL do app:

```text
http://localhost:5175/argos
```

## Testes e Build

Backend:

```bash
cd backend
python -m pytest
```

Frontend:

```bash
cd frontend\argos-web
npm run build
```

## Deploy no Render

O projeto inclui `render.yaml` na raiz para deploy via Blueprint.

### Backend no Render

Configuracao:

```text
Root Directory: backend
Build Command: pip install -r requirements.txt
Start Command: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Variaveis:

```env
APP_NAME=ARGOS
ENVIRONMENT=production
DATABASE_URL=sqlite:////var/data/argos.db
API_V1_PREFIX=/api/v1
FRONTEND_URL=https://sua-url-frontend.onrender.com
CORS_ORIGINS=https://sua-url-frontend.onrender.com
SECRET_KEY=gere-um-valor-seguro
AUTO_CREATE_LITE_TABLES=true
LLM_PROVIDER=openrouter
LLM_FALLBACK_PROVIDER=
LLM_TIMEOUT_SECONDS=45
OPENROUTER_API_KEY=sk-or-sua-chave
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_DEFAULT_MODEL=openrouter/free
OPENROUTER_HTTP_REFERER=https://sua-url-frontend.onrender.com
OPENROUTER_X_TITLE=ARGOS
```

Troca de provedor/modelo:

- OpenRouter principal: `LLM_PROVIDER=openrouter`
- Sem fallback: deixe `LLM_FALLBACK_PROVIDER` vazio
- Modelo padrao OpenRouter: `OPENROUTER_DEFAULT_MODEL=openrouter/free`

O roteamento por tipo de tarefa fica em `backend/app/services/llm_gateway/llm_config.py`. As minutas juridicas usam a tarefa `legal_draft`, que pode apontar para modelos mais fortes no OpenRouter sem alterar a regra de negocio.

### Frontend no Render

Configuracao:

```text
Root Directory: frontend/argos-web
Build Command: npm ci && npm run build
Publish Directory: dist
```

Variavel:

```env
VITE_API_URL=https://sua-url-backend.onrender.com
```

### Passo a Passo com Blueprint

1. Suba o projeto para um repositorio GitHub.
2. No Render, clique em **New > Blueprint**.
3. Selecione o repositorio.
4. Confirme os servicos `argos-api` e `argos-web`.
5. Configure `OPENROUTER_API_KEY` no backend.
6. Configure `FRONTEND_URL` e `CORS_ORIGINS` com a URL do frontend.
7. Configure `VITE_API_URL` no frontend com a URL do backend.
8. Configure `OPENROUTER_API_KEY` no backend.
9. Execute o deploy dos dois servicos.

Observacao: o MVP usa SQLite com disco persistente em `/var/data`. No Render, discos persistentes exigem Web Service pago. O blueprint usa `plan: starter` para preservar dados entre deploys.

## Rotas Principais da API

- `GET /health`
- `GET /api/v1/processos-licitatorios/dashboard`
- `GET /api/v1/processos-licitatorios/`
- `POST /api/v1/processos-licitatorios/`
- `GET /api/v1/processos-licitatorios/{id}`
- `POST /api/v1/documentos/gerar`
- `GET /api/v1/documentos/gerados/{id}`
- `PATCH /api/v1/documentos/gerados/{id}`
- `GET /api/v1/documentos/gerados/{id}/exportar-docx`

## Proximos Modulos Planejados

- cadastro completo de orgaos, secretarias e unidades requisitantes;
- biblioteca de modelos institucionais por orgao;
- historico de versoes dos documentos;
- trilha de auditoria da revisao;
- modo colaborativo para parecer tecnico/juridico;
- geracao de mapa de riscos;
- estimativa de valor com base em pesquisa de precos;
- exportacao em PDF;
- autenticacao e perfis de acesso para o ARGOS;
- deploy com PostgreSQL para uso multiusuario;
- painel administrativo para configuracao de prompts;
- painel administrativo para configuracao de provedores e modelos de IA;
- integracao com documentos e processos existentes.

## Status Atual

MVP funcional para demonstracao:

- cadastro de processo;
- geracao de ETP/TR;
- revisao no navegador;
- exportacao DOCX;
- dashboard inicial;
- deploy preparado para Render.
