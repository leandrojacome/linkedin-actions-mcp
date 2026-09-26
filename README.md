# LinkedIn Actions MCP

Servidor MCP local da CodeSpec focado somente nas ações que faltam ao MCP de leitura:

- publicar posts pela API oficial do LinkedIn;
- preparar e enviar candidaturas simplificadas usando uma sessão local do navegador.

## Limites importantes

A API pública do LinkedIn permite publicação quando o aplicativo possui os escopos necessários.
Não existe uma API pública geral para um candidato se inscrever em vagas de terceiros. Por isso,
a candidatura usa um navegador local persistente e nunca expõe a sessão por HTTP.

O servidor usa `stdio`, armazena o perfil do navegador apenas na máquina do usuário e não envia
cookies, tokens ou currículos para serviços intermediários.

## Desenvolvimento

```bash
uv sync --all-groups
uv run patchright install chromium
uv run pytest
uv run fastmcp dev src/linkedin_actions_mcp/server.py
```

Copie `.env.example` para `.env` somente se for usar a API oficial de publicação. Nunca envie o
arquivo `.env` ao Git.

## Ferramentas

### `publish_linkedin_post`

Cria uma prévia por padrão. Para publicar, informe `confirmed=true`. Requer
`LINKEDIN_ACCESS_TOKEN` e `LINKEDIN_AUTHOR_URN`.

### `apply_to_linkedin_job`

Abre a vaga no navegador local e anexa o currículo quando o formulário solicitar. Sem
`confirmed=true`, prepara o fluxo sem enviar. Se houver perguntas ou etapas incompletas, retorna
um bloqueio legível e não declara a candidatura como enviada.

## Segurança

- transporte local por `stdio`;
- validação do domínio da vaga e do arquivo PDF;
- segredos apenas por variáveis de ambiente;
- nenhuma credencial em logs;
- CI com lint, testes e auditoria de dependências;
- Dependabot semanal para dependências e GitHub Actions.

## Licença

Apache-2.0.

