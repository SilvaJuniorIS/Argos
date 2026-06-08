# Manual do ARGOS

## 1. Objetivo

O ARGOS apoia equipes publicas na elaboracao de documentos da fase preparatoria de compras e licitacoes.

Nesta versao, o sistema entrega:

- cadastro de processos licitatorios;
- cadastro de itens, quantidades, justificativas e dados administrativos;
- geracao assistida de ETP, TR e Minuta de Edital;
- revisao humana do texto gerado no navegador;
- configuracao de dados institucionais do orgao;
- exportacao em DOCX com cabecalho institucional;
- API documentada via Swagger.

## 2. Como acessar

Com o ambiente local iniciado, acesse:

- App: `http://localhost:5175/argos`
- Novo processo: `http://localhost:5175/argos/processos/novo`
- Institucional: `http://localhost:5175/argos/institucional`
- API: `http://localhost:8002/docs`
- Status da API: `http://localhost:8002/health`

## 3. Fluxo de uso

1. Acesse o painel do ARGOS.
2. Crie um novo processo.
3. Preencha objeto, justificativa, unidade requisitante, secretaria e itens.
4. Escolha o documento: ETP, TR ou Minuta de Edital.
5. Gere a minuta com IA.
6. Revise o texto no editor.
7. Salve a revisao.
8. Exporte o DOCX institucional.

## 4. Dados institucionais

A tela `Institucional` guarda as informacoes usadas no cabecalho e na estrutura dos documentos:

- orgao;
- CNPJ;
- endereco;
- telefone;
- e-mail;
- site;
- unidade responsavel;
- autoridade competente;
- brasao ou logomarca, quando configurado.

Esses dados ajudam a padronizar a saida dos documentos e reduzem ajustes manuais depois da geracao.

## 5. IA

O backend usa OpenRouter como provedor inicial.

Configure a chave em `backend/.env`:

```env
LLM_PROVIDER=openrouter
LLM_FALLBACK_PROVIDER=
OPENROUTER_API_KEY=sk-or-sua-chave
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_DEFAULT_MODEL=openrouter/free
OPENROUTER_HTTP_REFERER=http://localhost:5175
OPENROUTER_X_TITLE=ARGOS
```

A chave deve ficar apenas no backend.

## 6. Validacao

Backend:

```powershell
cd backend
python -m pytest
```

Frontend:

```powershell
cd frontend\argos-web
npm run build
```

## 7. Escopo ativo

O foco atual do projeto e o ARGOS documental:

- processos licitatorios;
- geracao de ETP;
- geracao de TR;
- geracao de Minuta de Edital;
- revisao e exportacao DOCX;
- padronizacao institucional.
