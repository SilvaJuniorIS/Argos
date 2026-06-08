# ARGOS Web

Frontend React + Vite do ARGOS.

## Local

```bash
copy .env.example .env
npm ci
npm run dev
```

Configure:

```env
VITE_API_URL=http://localhost:8000
```

URL local:

```text
http://localhost:5174/argos
```

## Build

```bash
npm run build
```

## Render

Use como Static Site:

```text
Root Directory: frontend/argos-web
Build Command: npm ci && npm run build
Publish Directory: dist
```

Variavel obrigatoria:

```env
VITE_API_URL=https://sua-url-backend.onrender.com
```
