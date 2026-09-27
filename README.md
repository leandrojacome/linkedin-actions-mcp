# LinkedIn Actions MCP

Servidor MCP local da CodeSpec focado somente nas ações que faltam ao MCP de leitura:

- publicar posts de texto ou imagem pela API oficial do LinkedIn;
- preparar e enviar candidaturas simplificadas usando uma sessão local do navegador;
- listar, ler e responder solicitações da página de Serviços com confirmação explícita.

## Limites importantes

A API pública do LinkedIn permite publicação quando o aplicativo possui os escopos necessários.
Não existe uma API pública geral para um candidato se inscrever em vagas de terceiros. Por isso,
a candidatura usa um navegador local persistente e nunca expõe a sessão por HTTP.

O servidor usa `stdio`, armazena o perfil do navegador apenas na máquina do usuário e não envia
cookies, tokens ou currículos para serviços intermediários.

Para staging privado, também pode usar Streamable HTTP vinculado exclusivamente ao endereço da
tailnet. Não vincule o servidor a uma interface pública.

## Desenvolvimento

```bash
uv sync --all-groups
uv run patchright install chromium
uv run pytest
uv run fastmcp dev src/linkedin_actions_mcp/server.py
```

Copie `.env.example` para `.env` somente se for usar a API oficial de publicação. Nunca envie o
arquivo `.env` ao Git.

### Staging pela tailnet

Defina `LINKEDIN_TRANSPORT=http`, `LINKEDIN_HOST` com o IP Tailscale local e mantenha a porta fora
da internet pública. O endpoint Streamable HTTP será `/mcp`.

## Ferramentas

### `publish_linkedin_post`

Cria uma prévia por padrão. Para publicar, informe `confirmed=true`. Requer
`LINKEDIN_ACCESS_TOKEN` e `LINKEDIN_AUTHOR_URN`. Para imagem, informe `image_path` e,
opcionalmente, `image_alt_text`; o servidor inicializa o upload, envia o arquivo e cria o post
pela API oficial, sem navegador.

### `apply_to_linkedin_job`

Abre a vaga no navegador local e anexa o currículo quando o formulário solicitar. Sem
`confirmed=true`, prepara o fluxo sem enviar. Se houver perguntas ou etapas incompletas, retorna
um bloqueio legível e não declara a candidatura como enviada.

### Solicitações de serviços

`list_linkedin_service_requests` e `read_linkedin_service_request` são operações somente de
leitura. `submit_linkedin_service_proposal` retorna uma prévia por padrão e somente envia quando
`confirmed=true`. Configure `LINKEDIN_SERVICE_REQUESTS_URL` com a página de administração das
solicitações da conta. Como o LinkedIn não oferece API pública para essa área, essas ferramentas
usam o mesmo perfil local persistente do navegador e podem exigir manutenção de seletores quando
a interface do LinkedIn mudar.

## Segurança

- transporte local por `stdio`;
- validação do domínio da vaga e do arquivo PDF;
- validação do domínio das solicitações e das faixas de horas;
- confirmação explícita antes de candidatura ou proposta;
- segredos apenas por variáveis de ambiente;
- nenhuma credencial em logs;
- CI com lint, testes e auditoria de dependências;
- Dependabot semanal para dependências e GitHub Actions.

## Licença

Apache-2.0.
