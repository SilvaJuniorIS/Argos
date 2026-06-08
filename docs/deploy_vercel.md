# Deploy do frontend na Vercel

## Ponto importante

A porta `5175` e usada apenas pelo Vite em desenvolvimento local. A Vercel nao sobe o servidor `npm run dev` nem expoe `localhost:5175`; ela executa `npm run build` e publica a pasta `dist` em uma URL HTTPS propria.

## Configuracao recomendada

No projeto da Vercel:

- Root Directory: `frontend/argos-web`
- Build Command: `npm run build`
- Output Directory: `dist`
- Environment Variable:
  - `VITE_API_URL=https://url-publica-da-api`

## API

O frontend chama a API usando `VITE_API_URL`. Em desenvolvimento local, o fallback continua sendo `http://localhost:8002`.

Se o backend estiver no Railway, Render, Fly.io ou outro host, use a URL publica desse backend em `VITE_API_URL`.

## Rotas React

O arquivo `frontend/argos-web/vercel.json` direciona rotas do app React para `index.html`, evitando erro 404 ao abrir URLs como:

- `/argos`
- `/argos/processos/novo`
- `/argos/processos/1`
- `/argos/documentos/1`
- `/argos/institucional`
