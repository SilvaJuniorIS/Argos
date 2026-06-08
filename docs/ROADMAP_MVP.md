# Roadmap ate o MVP

## Diagnostico

O ARGOS ja esta perto de um MVP operacional. O projeto tem backend FastAPI,
autenticacao, perfis, escopo por secretaria, cadastro de contratos e atas, importacao de
planilha, alertas, envio por e-mail, fiscalizacao, documentos, auditoria, Docker e testes
automatizados.

O principal ponto de atencao antes do MVP e a coexistencia de dois modulos de contrato:

- `contratos`: modelo relacional mais completo, com secretaria, fornecedor, gestor, fiscal,
  alertas, documentos e fiscalizacao.
- `contracts`: modulo de importacao real, mais espelhado na planilha, com campos como
  `numero_contrato`, `fim_vigencia`, `alerta_30` e similares.

Isso ajudou a evoluir rapido, mas precisa ser consolidado antes do MVP. O usuario final nao
pode sentir que ha dois cadastros de contrato no sistema.

## O que ja esta MVPavel

- Login e controle basico de acesso.
- Dashboard.
- Cadastro e listagem de contratos e atas.
- Importacao de planilha real.
- Alertas de vencimento e reajuste.
- Envio de alertas por e-mail para responsaveis e secretaria.
- Fiscalizacao e ocorrencias.
- Upload, listagem e download de documentos.
- Auditoria tecnica.
- Ambiente Docker de teste real.
- Testes automatizados cobrindo os fluxos principais.

## Principais riscos antes do MVP

1. Duplicidade entre `contratos` e `contracts`.
2. Tela de edicao inconsistente: criacao usa `ContratoForm`, enquanto a rota de edicao usa
   `ContractForm`.
3. Importacao real provavelmente alimenta `contracts`, enquanto o restante operacional usa
   principalmente `contratos`.
4. Secretarias, fornecedores e usuarios ainda nao possuem uma UI administrativa completa.
5. SMTP depende de configuracao externa e precisa de teste real.
6. Documentacao esta parcialmente desatualizada e alguns arquivos tem problemas de encoding.
7. Auditoria existe no backend, mas falta tela operacional para consulta.
8. Falta validar a jornada feliz de ponta a ponta com dados reais.

## Proximos passos ate o MVP

### 1. Unificar o modulo de contratos

- Decidir qual tabela/modelo sera a fonte oficial do MVP.
- Recomendacao: usar `contratos` como dominio principal.
- Adaptar a importacao real para gravar no modelo oficial.
- Remover, esconder ou deixar como infraestrutura interna o fluxo duplicado.
- Garantir que dashboard, alertas, documentos e fiscalizacao leiam da mesma base.

### 2. Fechar a jornada principal

O MVP deve permitir executar sem intervencao tecnica:

- importar planilha real;
- revisar contratos importados;
- cadastrar e editar contrato ou ata manualmente;
- anexar documentos;
- gerar alertas;
- receber alerta por e-mail;
- registrar ocorrencia de fiscalizacao;
- resolver alerta ou ocorrencia.

### 3. Criar telas administrativas minimas

Telas necessarias:

- Secretarias: nome, sigla, e-mails de alerta e status ativo/inativo.
- Fornecedores: razao social, CNPJ e status ativo/inativo.
- Usuarios: nome, e-mail, perfil, secretaria e status ativo/inativo.

Essas telas reduzem dependencia de Swagger, seed ou acesso direto ao banco.

### 4. Ajustar importacao

- Garantir que a planilha real alimente a base oficial de contratos.
- Exibir relatorio claro de importacao:
  - importados;
  - atualizados;
  - ignorados;
  - erros.
- Permitir baixar relatorio de erros.
- Validar cabecalhos esperados.
- Tratar linhas parcialmente preenchidas.
- Mostrar exemplos de preenchimento no modelo de planilha.

### 5. Validar envio real de e-mail

- Configurar SMTP no `.env`.
- Criar endpoint ou botao administrativo para teste de e-mail.
- Registrar falhas de envio de forma visivel.
- Definir comportamento quando o envio falhar:
  - manter alerta como pendente;
  - registrar tentativa;
  - permitir reenvio manual.
- Testar envio para:
  - fiscal responsavel;
  - gestor responsavel;
  - e-mails institucionais da secretaria;
  - destinatarios duplicados.

### 6. Finalizar alertas

- Exibir se o alerta foi enviado por e-mail.
- Exibir ou registrar destinatarios.
- Testar agendamento diario via Celery Beat no Docker.
- Evitar duplicidade entre `alertas` e `notifications`.
- Confirmar janelas de vencimento:
  - 180 dias;
  - 90 dias;
  - 60 dias;
  - 30 dias;
  - 15 dias;
  - 7 dias;
  - 1 dia.
- Confirmar regras de reajuste anual.

### 7. Polir permissoes

Perfis esperados:

- Admin: acesso total.
- Gestor: contratos e operacoes da propria secretaria.
- Fiscal: visualizacao e fiscalizacao da propria secretaria.
- Auditor: leitura ampla e auditoria.

Validar:

- respostas `401` e `403` na API;
- comportamento visual no frontend;
- bloqueio de edicao fora do escopo;
- menus e botoes conforme perfil.

### 8. Criar tela de auditoria

Uma tela minima de auditoria deve permitir filtrar por:

- entidade;
- usuario;
- acao;
- periodo;
- identificador do registro.

Isso aumenta confianca institucional e facilita suporte durante o piloto.

### 9. Hardening tecnico

- Rodar migrations em banco limpo.
- Rodar migrations em banco ja existente.
- Corrigir lint geral do projeto aos poucos.
- Atualizar documentacao operacional.
- Corrigir textos com encoding quebrado.
- Conferir scripts de iniciar/parar.
- Validar backup e restore.
- Revisar secrets e `.env.example`.

### 10. Teste piloto com dados reais

Roteiro recomendado:

1. Importar uma planilha real pequena.
2. Conferir manualmente ao menos 10 contratos/atas.
3. Gerar alertas.
4. Enviar e-mails reais para caixa de teste.
5. Simular fiscal registrando ocorrencia.
6. Simular gestor resolvendo alerta.
7. Consultar auditoria.
8. Reiniciar Docker e confirmar persistencia dos dados.

## Ordem recomendada de execucao

1. Unificar `contratos` e `contracts`.
2. Ajustar importacao para gravar na base oficial.
3. Criar CRUD minimo de secretarias, fornecedores e usuarios.
4. Testar SMTP real e alertas agendados.
5. Fechar documentos e fiscalizacao no detalhe do contrato.
6. Criar auditoria visual.
7. Atualizar documentacao.
8. Executar piloto com dados reais.

## Definicao de MVP

O MVP pode ser considerado pronto quando uma secretaria conseguir, sem ajuda tecnica:

- importar ou cadastrar contratos e atas;
- ver dashboard confiavel;
- receber alertas por e-mail;
- anexar documentos;
- registrar fiscalizacao;
- resolver alertas;
- consultar historico/auditoria basica;
- operar tudo com perfis e escopo corretos.
