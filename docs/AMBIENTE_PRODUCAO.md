# Ambiente de producao do ARGOS

Este checklist concentra as variaveis que devem ser definidas fora do Git, no provedor de deploy ou no host de producao.

## Obrigatorias

```env
ENVIRONMENT=production
APP_NAME=ARGOS
DATABASE_URL=sqlite:////var/data/argos.db
FRONTEND_URL=https://sua-url-frontend
CORS_ORIGINS=https://sua-url-frontend
SECRET_KEY=gere-um-valor-forte
ADMIN_EMAIL=admin@seudominio.gov.br
ADMIN_PASSWORD=gere-uma-senha-forte
```

Em producao, a API recusa inicializacao se `SECRET_KEY` continuar como `change-me-in-production` ou se `ADMIN_PASSWORD` continuar como `argos123`.

## IA

```env
LLM_PROVIDER=openrouter
LLM_FALLBACK_PROVIDER=
LLM_TIMEOUT_SECONDS=45
OPENROUTER_API_KEY=sk-or-...
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_DEFAULT_MODEL=openrouter/free
OPENROUTER_HTTP_REFERER=https://sua-url-frontend
OPENROUTER_X_TITLE=ARGOS
```

Neste primeiro deploy, nao configure OpenAI. O campo `LLM_FALLBACK_PROVIDER` deve ficar vazio para que o backend use somente OpenRouter.

## E-mail

```env
SMTP_HOST=smtp.seudominio.gov.br
SMTP_PORT=587
SMTP_USER=usuario-smtp
SMTP_PASS=senha-smtp
SMTP_FROM=noreply@seudominio.gov.br
```

## Frontend

No static site do frontend:

```env
VITE_API_URL=https://sua-url-backend
```

## Local sem conflito com FiscalBot

O ambiente Docker local do ARGOS usa:

```text
Frontend: http://localhost:5175
API Docs: http://localhost:8002/docs
Health: http://localhost:8002/health
Postgres: localhost:5434
Redis: localhost:6381
```
