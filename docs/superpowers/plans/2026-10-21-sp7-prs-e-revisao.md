# SP7: Abertura dos PRs e revisão de código — plano de implementação

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** O harness abre os PRs da entrega (subtrees e workspace) para o ramo de teste e, depois da homologação, para o `main`, posta no Google Chat e revisa o conjunto a partir do PR do workspace, publicando os achados escolhidos pelo revisor.

**Architecture:** Um subcomando novo do CLI, `tools/ws/ws pr`, implementado em Python (stdlib), como o `tools/atlas/`. Ele conversa com o Azure DevOps só pelo `az rest`, usa o git para descobrir a entrega e posta no webhook com `urllib`. As skills do Spec Kit (`commit-push`, `bug-enviar`, `refactor-enviar` e o comando novo `promover`) chamam o `ws pr`. A revisão é uma skill de Claude Code (`ws-revisar`): o `ws pr revisao` monta o contexto, o agente revisa e o `ws pr comentar` publica.

**Tech Stack:** bash (Git for Windows), Python 3 só com a stdlib, `az` CLI (`az rest`), REST do Azure DevOps `api-version=7.1`, webhook do Google Chat e Spec Kit (extensão `ws`).

**Spec:** `docs/superpowers/specs/2026-10-21-sp7-prs-e-revisao-design.md` (repo de discovery). O código vai em `C:\src\wms-workspace`.

## Global Constraints

- **Onde roda:** num worktree novo do workspace, a partir do `origin/main` (que já tem o SP6.2, PR 17222), na branch `harness/prs-e-revisao`. O clone do usuário em `C:\src\wms-workspace` está na `ws-002-chaves-centrais` com mudanças locais: não mexa nele.
- **Idioma:** português do Brasil em mensagens, textos de PR, mensagens do Chat e skills. As mensagens do CLI começam com `ws: ` e os erros com `ws: erro: `, como no `common.sh`.
- **Python:** só a stdlib. Rode sempre com `python -X utf8`. O `az` recebe o corpo por arquivo (`--body @arquivo`) em UTF-8, e a saída dele é lida como UTF-8.
- **Azure DevOps:** organização `https://dev.azure.com/ARECO` e projeto `AReCO`, lidos do `workspace.pr.ini`. Recurso do token no `az rest`: `499b84ac-1321-427f-aa17-267ca6975798`.
- **Acesso:** só o `az rest`. Nada de PAT no código. O comando do `az` vem de `WS_AZ` (padrão: o `az` do `PATH`; no Windows, `shutil.which("az")` acha o `az.cmd`).
- **Destinos:** `main` (`WS_DESTINO`) e o ramo de teste, que é `homolog` por padrão e `develop` no Fly (`repos/integracoes.core.plataforma.backoffice.frontend`). O ramo de teste do workspace é `homolog`.
- **Webhooks:** as URLs ficam versionadas no `workspace.pr.ini` (decisão do usuário).
- **Base da entrega:** a mesma do `ws push`, `ws_base_ref()...HEAD`, ou seja, o merge-base com a `ws/sync`. Os repos da entrega são os prefixos `repos/<repo>` alterados, como no `ws_changed_prefixes`.
- **Regra nova:** o PR do workspace é aberto junto com os das subtrees e completado por último.
- **Sem votos:** o harness não aprova, não reprova e não completa PRs, e não liga o auto-complete. Não escolhe revisores.
- **Sem attribution:** commits e PRs sem atribuição ao Claude (`.claude/settings.json` já desliga).
- **Testes:** no runner de sempre, `bash tools/ws/tests/run.sh`, sem rede. O `az` é o falso `tools/ws/tests/fake_az.py`, e o Chat grava em `WS_CHAT_SAIDA`.

## Review Focus

1. **Acentos nos títulos e nas descrições** (`feat(ws-007): Conferência de notas`): o texto chega intacto ao Azure DevOps e ao Chat, sem mojibake do cp1252 do Windows. Teste em `test_pr_abrir_preserva_acentos` (Task 2).
2. **Branch com barra** (`hotfix/x`, `refactor/eap-1-1-4-subida`): os refs e as URLs saem certos (`refs/heads/hotfix/x`, com `quote` na URL). Teste em `test_pr_abrir_branch_com_barra` (Task 2).
3. **Falha no meio da abertura** (o 2º PR falha): a mensagem diz o que foi aberto, e rodar de novo completa a abertura sem duplicar nada. Teste em `test_pr_abrir_falha_no_meio_e_retoma` (Task 2).
4. **Descrição longa** (muitos commits): a descrição respeita o limite de 4000 caracteres do Azure DevOps, cortando a lista de commits com "… e mais N commits". Teste em `test_pr_descricao_respeita_o_limite` (Task 2).
5. **Webhook com falha** (URL inválida ou fora do ar): os PRs ficam abertos, o comando sai com 0, avisa e imprime o texto para colar. Teste em `test_pr_chat_falha_mostra_o_texto` (Task 3).

---

## Estrutura de arquivos (workspace)

| Arquivo | Responsabilidade |
|---|---|
| `workspace.pr.ini` (raiz, novo) | Organização, projeto, webhooks e ramo de teste por repo |
| `tools/ws/pr/__main__.py` | CLI: `plano`, `abrir`, `revisao`, `comentar` |
| `tools/ws/pr/config.py` | Lê o `workspace.pr.ini` |
| `tools/ws/pr/azure.py` | Envoltório do `az rest` |
| `tools/ws/pr/entrega.py` | Descobre a entrega pelo git: branch, base, repos, origem, título, resumo e commits |
| `tools/ws/pr/textos.py` | Descrições, tabela das subtrees, avisos e mensagem do Chat |
| `tools/ws/pr/abrir.py` | `plano` e `abrir` (homolog e main), incluindo a recriação de branch e o Chat |
| `tools/ws/pr/revisao.py` | `revisao` (contexto e worktree) e `comentar` (publicação e deduplicação) |
| `tools/ws/lib/pr.sh` | `ws_pr`: chama o pacote Python |
| `tools/ws/ws` | Despacha o `pr` |
| `tools/ws/lib/push.sh` | Mensagem final do `ws push` |
| `tools/ws/tests/fake_az.py`, `tools/ws/tests/pr_lib.sh` | `az` falso com estado em JSON e helpers da fixture |
| `tools/ws/tests/test_pr.sh`, `tools/ws/tests/test_pr_revisao.sh` | Testes |
| `tools/speckit/ws/commands/speckit.ws.{commit-push,bug-enviar,refactor-enviar,bug-sem-correcao,promover}.md`, `tools/speckit/ws/extension.yml` | Oferta dos PRs e comando de promoção |
| `tools/speckit/refactor/commands/speckit.refactor.subida.md` | Promoção pela branch de subida |
| `.claude/skills/ws-revisar/SKILL.md` | Skill da revisão |
| `.claude/skills/speckit-ws-*` | Geradas pelo `tools/ws/ws speckit` |
| `AGENTS.md`, `docs/harness/{1-comecar,2-quando-da-errado,3-alem-do-basico,4-manter}.md`, `docs/adr/0001-workspace-git-subtree.md` | Regra nova e uso |

---

### Task 1: Configuração, `az` falso e `ws pr plano homolog`

**Files:**
- Create: `workspace.pr.ini`, `tools/ws/pr/__main__.py`, `tools/ws/pr/config.py`, `tools/ws/pr/azure.py`, `tools/ws/pr/entrega.py`, `tools/ws/pr/textos.py` (só `titulo`), `tools/ws/pr/abrir.py` (só `plano`), `tools/ws/lib/pr.sh`, `tools/ws/tests/fake_az.py`, `tools/ws/tests/pr_lib.sh`, `tools/ws/tests/test_pr.sh`
- Modify: `tools/ws/ws` (caso `pr` e texto do uso), `tools/ws/tests/test_harness.sh`

**Interfaces:**
- Produces:
  - `workspace.pr.ini`, lido pelo `configparser` com `optionxform = str`:
    ```ini
    # Configuração dos PRs do harness (SP7). As URLs dos webhooks ficam versionadas (decisão do usuário).
    [azure]
    organizacao = https://dev.azure.com/ARECO
    projeto = AReCO
    [chat]
    homolog =
    producao =
    [teste]
    # Ramo de teste por repo; "padrao" vale para os outros repos e para o workspace.
    padrao = homolog
    repos/integracoes.core.plataforma.backoffice.frontend = develop
    ```
  - `config.py`:
    - `Config(org: str, projeto: str, chat: dict[str, str], ramo_padrao: str, ramos: dict[str, str])`;
    - `le_config(raiz: Path) -> Config`, que falha com `ws: erro: não encontrei workspace.pr.ini` se o arquivo não existir;
    - `Config.ramo_teste(prefixo: str | None) -> str`, em que `None` é o workspace.
  - `azure.py`, `class Azure(org, projeto, cmd: list[str])`:
    - `logado() -> bool` (`az account show`);
    - `listar_prs(repo, origem, destino, status) -> list[dict]`, com `status` em `active`, `completed` ou `all`;
    - `criar_pr(repo, origem, destino, titulo, descricao) -> dict`;
    - `atualizar_descricao(repo, pr_id, descricao) -> None`;
    - `pr_por_id(pr_id) -> dict` (`GET {org}/{projeto}/_apis/git/pullrequests/{id}`);
    - `threads(repo, pr_id) -> list[dict]`;
    - `criar_thread(repo, pr_id, conteudo, caminho=None, linha=None) -> dict`;
    - `criar_ref(repo, branch, sha) -> None`.

    Todos os métodos chamam `az rest --method <M> --url <U> --resource 499b84ac-1321-427f-aa17-267ca6975798 [--headers Content-Type=application/json --body @<arquivo>] -o json`. As branches viram `refs/heads/<b>`, e os valores de query passam por `urllib.parse.quote`. Um erro do `az` vira a exceção `ErroAzure(mensagem)`. `Azure.de_config(cfg)` monta `cmd` a partir de `shlex.split(os.environ.get("WS_AZ", ""))` ou de `[shutil.which("az")]`.
  - `entrega.py`:
    - `Repo(prefixo: str, url: str, nome: str)`, em que `nome` é o último segmento da URL, sem `.git`;
    - `Entrega(raiz, branch, base, repos: list[Repo], ws_url, ws_nome, origem: str | None, titulo, resumo, commits: dict[str, list[str]])`, em que a chave `""` de `commits` é o workspace;
    - `le_entrega(raiz: Path) -> Entrega`. A base vem do `ws_base_ref()`: a `ws/sync` local, senão a `origin/ws/sync`, senão o `WS_DESTINO`. Os repos são os prefixos alterados em `base...HEAD`, cruzados com o `workspace.repos`, e um prefixo fora do manifesto falha como no `ws push`.
    - A `origem` é o primeiro diretório alterado em `base...HEAD`, nesta ordem de prioridade: `refactors/fatias/<código>/`, `specs/<pasta>/`, `bugs/<slug>/`, `refactors/<slug>/`.
    - O `resumo` é o primeiro parágrafo depois do título do `spec.md` (specs), do `assessment.md` (bugs e refactors) ou do `plano-subida.md` (fatias), com no máximo 600 caracteres.
  - `textos.py`: `titulo(entrega, destino_teste: bool) -> str`. É o assunto do commit mais recente de `base..HEAD` que casa com `^(feat|fix|refactor|docs)\(`, ou a branch quando nenhum casa, com o prefixo `[homolog] ` quando `destino_teste`. O prefixo é sempre a palavra `homolog`, mesmo no Fly, para padronizar o Chat (decisão minha).
  - `abrir.py`: `plano(raiz, destino: str) -> int`, com `destino` em `homolog` ou `main`, que imprime as linhas abaixo e devolve o código de saída.
  - CLI: `tools/ws/ws pr plano <homolog|main>`; a `ws_pr` roda `python -X utf8 "$WS_DIR_PR" "$@"`, com `cd` na raiz.

- [ ] **Step 1: Fixture e `az` falso**

O `tools/ws/tests/fake_az.py` aceita `account show` e `rest`. Ele guarda o estado em `$WS_FAKE_AZ_ESTADO` (JSON: `prs`, `threads`, `prox_id`) e implementa:
- `GET` e `POST .../_apis/git/repositories/{repo}/pullrequests`, com os filtros `searchCriteria.sourceRefName`, `targetRefName` e `status`;
- `PATCH .../pullrequests/{id}`;
- `GET .../_apis/git/pullrequests/{id}`;
- `GET` e `POST .../repositories/{repo}/pullRequests/{id}/threads`;
- `POST .../repositories/{repo}/refs`, que roda `git update-ref` em `$T/remotes/<repo>.git`, ou em `$T/origin.git` quando o repo é `origin`.

O PR criado ganha `pullRequestId`, `status: active` e `repository.webUrl = https://dev.azure.com/ARECO/AReCO/_git/<repo>`. Com o arquivo `$T/az-sem-login`, o `account show` sai com 1. Com `$T/az-falha-<repo>`, o `POST` de PR nesse repo sai com 1 uma vez e o arquivo é apagado. Cada chamada é anexada a `$T/az.log`.

O `tools/ws/tests/pr_lib.sh` define:
- `fx_pr`: roda o `fx_ready`, grava o `workspace.pr.ini` de teste (org e projeto iguais aos reais, `[chat] homolog = http://chat/homolog` e `producao = http://chat/producao`, `padrao = homolog` e `repos/r2 = develop`), commita e faz push no main. Também exporta `WS_AZ="python -X utf8 $WS_DIR/tests/fake_az.py"`, `WS_FAKE_AZ_ESTADO=$T/az.json` e `WS_CHAT_SAIDA=$T/chat.log`;
- `cria_ramo <repo|origin> <ramo>`, que cria o ramo a partir do main no bare;
- `fx_entrega`: roda `cria_ramo r1 homolog`, `cria_ramo r2 develop` e `cria_ramo origin homolog`, depois `ws start feat/a`, commita `repos/r1/src/app.txt` e `repos/r2/src/app.txt` com a mensagem `feat(ws-007): Conferência de notas [specs/ws-007-conferencia]`, cria `specs/ws-007-conferencia/spec.md` (`# Conferência de notas`, linha vazia, `Resumo da conferência.`) e roda `ws push`;
- `pr_estado <expr python>`, que imprime uma expressão sobre o JSON do estado (por exemplo, `len(e["prs"])`).

O teste de fixture `test_pr_fake_az_cria_e_lista` cria um PR por `az rest` falso e o lista.

- [ ] **Step 2: Testes do plano** (em `test_pr.sh`, que faz `source "$WS_DIR/tests/pr_lib.sh"`)

```bash
test_pr_plano_homolog_lista_subtrees_e_workspace() {
  fx_pr; fx_entrega
  assert_ok ws pr plano homolog
  assert_contains "$OUT" "ws: PR r1 feat/a -> homolog [novo]"
  assert_contains "$OUT" "ws: PR r2 feat/a -> develop [novo]"
  assert_contains "$OUT" "ws: PR origin feat/a -> homolog [novo]"
  assert_contains "$OUT" "ws: título: [homolog] feat(ws-007): Conferência de notas [specs/ws-007-conferencia]"
  assert_eq "$(pr_estado 'len(e["prs"])')" "0"
}
test_pr_plano_sem_login_nao_abre_nada() {
  fx_pr; fx_entrega; touch "$T/az-sem-login"
  assert_fails ws pr plano homolog
  assert_contains "$OUT" "ws: erro: o az não está autenticado: rode az login e tente de novo; nenhum PR foi aberto"
}
test_pr_plano_sem_ramo_de_teste_recusa_tudo() {
  fx_pr; cria_ramo r1 homolog; cria_ramo origin homolog   # r2 sem develop
  ws start feat/a >/dev/null; ws_commit repos/r1/src/app.txt v2; ws_commit repos/r2/src/app.txt v2; ws push >/dev/null
  assert_fails ws pr plano homolog
  assert_contains "$OUT" "ws: erro: sem o ramo de teste no origin: r2 (develop); o time do repo precisa criá-lo. Nenhum PR foi aberto"
  assert_contains "$OUT" "pullrequestcreate?sourceRef=feat/a&targetRef=homolog"
}
test_pr_plano_sem_repo_manda_direto_para_main() {
  fx_pr; cria_ramo origin homolog; ws start feat/a >/dev/null; ws_commit specs/x/spec.md "# x"
  assert_fails ws pr plano homolog
  assert_contains "$OUT" "a entrega não muda nenhum repo: não há o que homologar; abra o PR do workspace direto para o main com tools/ws/ws pr abrir main"
}
test_pr_plano_recusa_na_base() {
  fx_pr; assert_fails ws pr plano homolog; assert_contains "$OUT" "ws pr não roda no main"
}
```

Em `test_harness.sh`, acrescente `test_workspace_pr_ini_tem_azure_e_ramos`, que confere no `workspace.pr.ini` da raiz: `organizacao = https://dev.azure.com/ARECO`, `projeto = AReCO`, `padrao = homolog` e `repos/integracoes.core.plataforma.backoffice.frontend = develop`.

- [ ] **Step 3: Rode os testes e confirme que falham.** Comando: `bash tools/ws/tests/run.sh tools/ws/tests/test_pr.sh tools/ws/tests/test_harness.sh`. Esperado: FALHA por `uso: ws <add|...>` (o `pr` ainda não existe) e por falta do `workspace.pr.ini`.

- [ ] **Step 4: Implemente** a configuração, o `Azure`, o `le_entrega`, o `titulo`, o `plano` e o despacho `pr` no `tools/ws/ws`. O uso passa a ser `ws <add|start|sync|push|maintain|speckit|atlas|refactor|pr> [args]`.

A ordem do `plano` é esta:
1. A branch não pode ser a base nem o destino; se for, `ws pr não roda no <branch>; use a branch da entrega`.
2. Se o destino for `homolog` e a entrega não mudar nenhum repo, sai com a mensagem do teste.
3. `logado()`.
4. `git ls-remote <url> refs/heads/<ramo>` para cada repo e para o origin, coletando todos os ausentes antes de falhar.
5. `listar_prs(..., "active")` para marcar `[existe: !<id>]` ou `[novo]`.

- [ ] **Step 5: Rode os testes e confirme que passam.** Mesmo comando. Esperado: `0 falha(s)`.

- [ ] **Step 6: Commit** `harness: ws pr plano e configuração dos PRs (SP7)`.

---

### Task 2: `ws pr abrir homolog`

**Files:**
- Modify: `tools/ws/pr/abrir.py`, `tools/ws/pr/textos.py`, `tools/ws/tests/test_pr.sh`

**Interfaces:**
- Consumes: `Config`, `Azure`, `le_entrega`, `titulo` e `plano` (Task 1).
- Produces:
  - `abrir(raiz, destino) -> int`;
  - `textos.descricao_subtree(entrega, prefixo, pr_ws_url: str | None, destino_teste: bool) -> str`;
  - `textos.descricao_workspace(entrega, prs: list[tuple[str, str, int]], destino_teste: bool) -> str`, em que cada tupla é `(nome do repo, url do PR, id)`;
  - `textos.le_tabela(descricao: str) -> list[tuple[str, str, int]]`;
  - constantes `AVISO_ORDEM`, `AVISO_BRANCH` e `LIMITE = 4000`;
  - a tabela, em formato fixo:
    ```
    <!-- ws-pr:subtrees -->
    | Repo | PR |
    |---|---|
    | r1 | [!12](https://dev.azure.com/ARECO/AReCO/_git/r1/pullrequest/12) |
    <!-- /ws-pr:subtrees -->
    ```
  - `AVISO_ORDEM = "**Complete este PR só depois que todos os PRs acima estiverem completados.**"`;
  - `AVISO_BRANCH = "**Não apague a branch de origem ao completar: o PR para produção sai dela.**"`, só nos PRs para o ramo de teste.

  A descrição de uma subtree tem, nesta ordem:
  1. `Origem: <origem>` e o resumo;
  2. `PR do workspace: <url>`, quando já há a URL;
  3. `AVISO_BRANCH`, quando o destino é o ramo de teste;
  4. `Commits:`, com uma linha `- <assunto>` por commit de `base..HEAD -- repos/<repo>`.

  A descrição do workspace tem a origem e o resumo, a tabela, `AVISO_ORDEM` e, quando o destino é o ramo de teste, `AVISO_BRANCH`. Se o texto passa do `LIMITE`, a lista de commits é cortada e termina em `- … e mais N commits`.

- [ ] **Step 1: Testes**

```bash
test_pr_abrir_homolog_abre_subtrees_e_workspace_com_tabela() {
  fx_pr; fx_entrega
  assert_ok ws pr abrir homolog
  assert_eq "$(pr_estado 'len(e["prs"])')" "3"
  assert_eq "$(pr_estado '[p for p in e["prs"] if p["repo"]=="r2"][0]["targetRefName"]')" "refs/heads/develop"
  local ws_desc; ws_desc=$(pr_estado '[p for p in e["prs"] if p["repo"]=="origin"][0]["description"]')
  assert_contains "$ws_desc" "<!-- ws-pr:subtrees -->"
  assert_contains "$ws_desc" "| r1 | [!"
  assert_contains "$ws_desc" "Complete este PR só depois que todos os PRs acima estiverem completados."
  assert_contains "$ws_desc" "Não apague a branch de origem ao completar"
  assert_contains "$(pr_estado '[p for p in e["prs"] if p["repo"]=="r1"][0]["description"]')" "PR do workspace: https://dev.azure.com/ARECO/AReCO/_git/origin/pullrequest/"
  assert_ok git -C "$T/origin.git" show-ref --verify -q refs/heads/feat/a
}
test_pr_abrir_de_novo_so_atualiza() {
  fx_pr; fx_entrega; ws pr abrir homolog >/dev/null
  ws_commit repos/r1/src/app.txt v3 "feat(ws-007): ajuste"; ws push >/dev/null
  assert_ok ws pr abrir homolog
  assert_eq "$(pr_estado 'len(e["prs"])')" "3"
  assert_contains "$(pr_estado '[p for p in e["prs"] if p["repo"]=="r1"][0]["description"]')" "- feat(ws-007): ajuste"
}
test_pr_abrir_repo_novo_entra_na_tabela() { ... }          # 2º envio toca repos/r3 (manifesto com r3): 4 PRs, tabela com r3
test_pr_abrir_preserva_acentos() { ... }                   # título com "Conferência" igual no estado e no chat.log
test_pr_abrir_branch_com_barra() { ... }                   # ws start hotfix/x: sourceRefName == "refs/heads/hotfix/x"
test_pr_abrir_falha_no_meio_e_retoma() {
  fx_pr; fx_entrega; touch "$T/az-falha-r2"
  assert_fails ws pr abrir homolog
  assert_contains "$OUT" "ws: aberto r1"
  assert_contains "$OUT" "ws: erro: não consegui abrir o PR de r2"
  assert_ok ws pr abrir homolog
  assert_eq "$(pr_estado 'len(e["prs"])')" "3"
}
test_pr_descricao_respeita_o_limite() { ... }              # 300 commits em r1: len(description) <= 4000 e contém "… e mais"
```

Os testes marcados com `{ ... }` seguem o mesmo padrão. As asserções estão no comentário ao lado de cada um.

- [ ] **Step 2: Rode os testes e confirme que falham.** Comando: `WS_TEST=... bash tools/ws/tests/run.sh tools/ws/tests/test_pr.sh`. Esperado: FALHA (`abrir` inexistente).

- [ ] **Step 3: Implemente o `abrir`** nesta ordem:
  1. as checagens do `plano`, reaproveitando as funções dele;
  2. `git push -u origin <branch>`; se o origin recusar, falha com `push da branch <b> recusado; nenhum PR foi aberto`;
  3. para cada subtree, o PR ativo, que é atualizado, ou um PR novo. Imprime `ws: aberto <repo> <url>` ou `ws: atualizado <repo> <url>`;
  4. o PR do workspace, com a tabela;
  5. a descrição de cada subtree, atualizada com a URL do PR do workspace;
  6. por fim, `ws: próximo passo: quando a homologação aprovar, rode /speckit-ws-promover`.

Uma `ErroAzure` no passo 3 vira `não consegui abrir o PR de <repo>: <msg>; rode de novo para continuar`, com saída 1.

- [ ] **Step 4: Rode os testes e confirme que passam.** Comando: `bash tools/ws/tests/run.sh tools/ws/tests/test_pr.sh`.

- [ ] **Step 5: Commit** `harness: ws pr abrir para o ramo de teste (SP7)`.

---

### Task 3: Aviso no Google Chat

**Files:**
- Modify: `tools/ws/pr/textos.py`, `tools/ws/pr/abrir.py`, `tools/ws/tests/test_pr.sh`

**Interfaces:**
- Produces:
  - `textos.mensagem_chat(entrega, destino: str, autor: str, pr_ws: tuple[str, int], prs: list[tuple[str, str, int]]) -> str`;
  - `abrir.posta_chat(cfg, espaco: str, texto: str) -> bool`, com `espaco` em `homolog` ou `producao`.

  O texto da mensagem é este:
  ```
  *<título>*  (<homologação|produção>)
  Autor: <git config user.name>
  Workspace: <url|!id>
  Subtrees:
  • <repo>: <url|!id>
  Complete o PR do workspace por último.
  ```
  `posta_chat` faz um `POST` de `{"text": texto}` (`application/json; charset=UTF-8`) na URL do espaço, com timeout de 15 s. Com `WS_CHAT_SAIDA`, anexa o JSON ao arquivo em vez de postar.

- [ ] **Step 1: Testes**
  - `test_pr_chat_posta_uma_vez_no_espaco_de_homolog`: depois do `abrir homolog`, o `chat.log` tem 1 linha, com `"(homologação)"` e `/_git/origin/pullrequest/`. Um segundo `abrir homolog` não acrescenta linha.
  - `test_pr_chat_falha_mostra_o_texto`: com `WS_CHAT_SAIDA` vazio e `homolog = http://127.0.0.1:9/`, o `abrir` sai com 0, `OUT` contém `ws: aviso: não consegui postar no Google Chat (homolog); cole o texto abaixo no espaço:` e o título, e os 3 PRs existem.
  - `test_pr_chat_sem_url_mostra_o_texto`: com `homolog =` vazio, a mesma mensagem, com a causa `sem URL em workspace.pr.ini`.
- [ ] **Step 2: Rode os testes e confirme que falham.**
- [ ] **Step 3: Implemente.** O Chat recebe a mensagem só quando o `abrir` criou pelo menos um PR do workspace naquele destino. O espaço é `homolog` para o ramo de teste e `producao` para o `main`.
- [ ] **Step 4: Rode os testes e confirme que passam.**
- [ ] **Step 5: Commit** `harness: aviso dos PRs no Google Chat (SP7)`.

---

### Task 4: Promoção, `ws pr plano|abrir main`

**Files:**
- Modify: `tools/ws/pr/abrir.py`, `tools/ws/tests/test_pr.sh`, `tools/ws/tests/pr_lib.sh` (`completa_pr`, `apaga_branch`)

**Interfaces:**
- Consumes: tudo da Task 2 e da Task 3.
- Produces:
  - `pr_lib.sh`: `completa_pr <repo> <id>`, que marca o PR como `completed` e grava `lastMergeSourceCommit.commitId` com o head da branch de origem no bare; `apaga_branch <repo|origin> <branch>`.
  - `abrir.recria_branches(entrega, cfg, az) -> list[str]`: para cada repo e para o workspace sem a branch no origin, procura em `listar_prs(repo, branch, ramo_teste, "completed")` o PR mais recente e chama `criar_ref(repo, branch, lastMergeSourceCommit.commitId)`. Imprime `ws: recriada a branch <b> em <repo> a partir do PR !<id>`. Sem o PR completado, falha com `a branch <b> não existe mais em <repo> e não achei o PR completado para o ramo de teste; nenhum PR foi aberto`.

- [ ] **Step 1: Testes**
  - `test_pr_plano_main_avisa_pr_de_teste_aberto`: depois do `abrir homolog`, `ws pr plano main` contém `ws: aviso: PR para o ramo de teste ainda aberto: r1 !1` e lista `ws: PR r1 feat/a -> main [novo]`.
  - `test_pr_abrir_main_abre_e_posta_em_producao`: depois de completar os 3 PRs de teste, `ws pr abrir main` deixa 6 PRs. Os 3 novos têm `targetRefName refs/heads/main`, a descrição do workspace **não** contém `Não apague a branch`, e a última linha do `chat.log` contém `(produção)`.
  - `test_pr_abrir_main_recria_branch_apagada`: com o PR de teste do r1 completado e `apaga_branch r1 feat/a`, `abrir main` recria `feat/a` no `r1.git` no commit do PR e abre o PR.
  - `test_pr_abrir_main_sem_pr_completado_para`: com `apaga_branch r1 feat/a` e sem PR completado, a saída é 1, a mensagem é a do contrato acima e o número de PRs não muda.
  - `test_pr_abrir_main_na_branch_de_subida`: o workspace está numa branch `refactor/eap-1-1-4-subida`, que faz merge de duas branches de card. Cada card mudou um repo e já tem os PRs de teste. O `ws pr abrir main` roda `ws push` (a branch de subida passa a existir em `r1.git` e em `r2.git`) e abre 3 PRs para `main` a partir de `refactor/eap-1-1-4-subida`.
  - `test_pr_abrir_main_so_workspace`: a entrega só muda `bugs/x/`, e `abrir main` abre 1 PR, do workspace, sem tabela de subtrees e sem `AVISO_ORDEM`.
- [ ] **Step 2: Rode os testes e confirme que falham.**
- [ ] **Step 3: Implemente.**
  - O `plano main` acrescenta os avisos de `listar_prs(..., ramo_teste, "active")`.
  - O `abrir main` segue esta ordem:
    1. as checagens;
    2. `recria_branches`;
    3. `bash tools/ws/ws push`, que envia a branch de subida e os commits locais mais novos (sem repo alterado, é um no-op);
    4. o `abrir` comum com destino `WS_DESTINO`;
    5. o Chat em `producao`.
  - Na entrega sem repo, a descrição do workspace leva só a origem e o resumo.
- [ ] **Step 4: Rode os testes e confirme que passam.**
- [ ] **Step 5: Commit** `harness: promoção dos PRs para o main (SP7)`.

---

### Task 5: `ws pr revisao` e `ws pr comentar`

**Files:**
- Create: `tools/ws/pr/revisao.py`, `tools/ws/tests/test_pr_revisao.sh`
- Modify: `tools/ws/pr/__main__.py`

**Interfaces:**
- Consumes: `Azure`, `le_tabela` e `le_config`.
- Produces:
  - `revisao(raiz, link: str) -> int`. O link segue o padrão `.../_git/<repo>/pullrequest/<id>`, e a função:
    1. lê o PR;
    2. confere que o repo é o workspace (o nome do origin); se não for, falha com `o link não é de um PR do workspace`;
    3. lê a tabela; sem ela, falha com `o PR !<id> não tem a tabela das subtrees: ele não veio do harness`;
    4. roda `git fetch origin <branch> ws/sync`;
    5. cria o worktree `.ws/revisao/<id>/arvore` (`git worktree add --detach`, recriado se já existir);
    6. grava `.ws/revisao/<id>/contexto.json` e `.ws/revisao/<id>/<repo>.diff` (o diff `origin/ws/sync...origin/<branch>`, com `-U3`, por prefixo, e `workspace.diff` com o que está fora de `repos/`);
    7. imprime o caminho do contexto.
  - O formato do `contexto.json`:
    ```json
    {"pr": {"id": 0, "url": "", "destino": "", "branch": ""}, "base": "<sha>", "origem": "specs/...",
     "arvore": ".ws/revisao/<id>/arvore",
     "repos": [{"prefixo": "repos/r1", "nome": "r1", "pr_id": 0, "pr_url": "", "diff": ".ws/revisao/<id>/r1.diff", "arquivos": ["src/app.txt"]}],
     "workspace": {"nome": "origin", "pr_id": 0, "diff": ".ws/revisao/<id>/workspace.diff", "arquivos": []},
     "publicados": ["<id do achado>"]}
    ```
  - `comentar(raiz, contexto: str, achados: str) -> int`. O arquivo `achados.json` é uma lista de `{"ponto": "conformidade|contratos|regras|defeitos|banco", "gravidade": "alta|média|baixa", "arquivo": "<caminho no workspace>" | null, "linha": int | null, "titulo": str, "texto": str, "repo": "<prefixo>" | null}`.
  - `id_achado(a) -> str`, os 12 primeiros caracteres do `sha1(ponto|arquivo|titulo)`.

  A publicação de cada achado funciona assim:
  - **Arquivo em `repos/<repo>/` com o repo na entrega:** vai no PR do repo, com o caminho sem o prefixo.
  - **Arquivo fora de `repos/`, ou repo fora da entrega:** vai no PR do workspace.
  - **Linha dentro de um hunk do lado direito do diff do PR:** vira uma thread com `threadContext` (`filePath "/<caminho>"`, `rightFileStart` e `rightFileEnd` na linha, `offset 1`).
  - **Sem linha, ou fora dos hunks:** vira uma thread geral, com `` `<caminho>:<linha>` `` no início.

  O conteúdo é `**[<ponto> · <gravidade>] <titulo>**\n\n<texto>\n\n_Revisão do harness_ <!-- ws-revisao:<id> -->`. Um achado cujo id já aparece numa thread do PR é pulado, com `ws: já publicado: <titulo>`.

- [ ] **Step 1: Testes** (`fx_pr`, `fx_entrega` e `ws pr abrir homolog`; o link é a `webUrl` do PR do workspace mais `/pullrequest/<id>`)
  - `test_revisao_monta_contexto_com_subtrees`: o `contexto.json` tem 2 repos, `arquivos == ["src/app.txt"]` no r1, o `origem` é `specs/ws-007-conferencia`, e o worktree tem `repos/r1/src/app.txt` com `v2`.
  - `test_revisao_recusa_pr_sem_tabela`: com um PR do workspace criado direto no fake, sem tabela, a mensagem é a do contrato.
  - `test_revisao_recusa_pr_de_subtree`: com o link do PR do r1, `o link não é de um PR do workspace`.
  - `test_revisao_diff_ignora_sincronizacao_de_outros`: um `upstream_commit r2 src/outro.txt x`, seguido de `ws sync` e de um novo `ws push` na feature, não põe `src/outro.txt` em `arquivos` do r2.
  - `test_comentar_mapeia_caminho_para_o_pr_da_subtree`: o achado `repos/r1/src/app.txt:1` vira uma thread no PR do r1 com `filePath == "/src/app.txt"` e a linha 1.
  - `test_comentar_fora_do_diff_vira_geral`: com a linha 99, a thread é sem `threadContext` e o conteúdo começa com `` `src/app.txt:99` ``.
  - `test_comentar_repo_fora_da_entrega_vai_no_workspace`: o achado com `repo: "repos/r3"` vai no PR do workspace.
  - `test_comentar_nao_repete`: rodar `comentar` duas vezes com o mesmo arquivo deixa o mesmo número de threads e mostra `ws: já publicado:`.
- [ ] **Step 2: Rode os testes e confirme que falham.**
- [ ] **Step 3: Implemente.** Acrescente `.ws/revisao/` à limpeza: o `revisao` remove o worktree anterior do mesmo id. O `.ws/` já está no `.gitignore`.
- [ ] **Step 4: Rode os testes e confirme que passam.** Comando: `bash tools/ws/tests/run.sh tools/ws/tests/test_pr_revisao.sh`.
- [ ] **Step 5: Commit** `harness: contexto e publicação da revisão (SP7)`.

---

### Task 6: Skill `ws-revisar`

**Files:**
- Create: `.claude/skills/ws-revisar/SKILL.md`
- Modify: `tools/ws/tests/test_harness.sh`

**Interfaces:**
- Consumes: `ws pr revisao`, `ws pr comentar` e o formato do `achados.json` (Task 5).
- Produces: a skill `/ws-revisar <link do PR do workspace>`.

O frontmatter tem `name: ws-revisar` e uma `description` que cita "revisar PR do workspace". O corpo, em português e com o mesmo cabeçalho de idioma das skills `speckit-ws-*`, tem estes passos:
1. Rode `tools/ws/ws pr revisao <link>` e leia o contexto.
2. Leia a origem (`spec.md` e `tasks.md`, ou o `assessment.md`, ou o `plano-subida.md`), a constitution, o `AGENTS.md` e o `docs/convencoes.md` de cada repo da entrega.
3. Despache, em paralelo, **um subagente por ponto**, sobre a árvore do worktree e os diffs:
   - **conformidade;**
   - **contratos**, usando a skill `atlas-consultar` e as arestas de `docs/sistemas/` para achar os consumidores, inclusive em repos fora da entrega;
   - **regras;**
   - **defeitos e testes;**
   - **banco**, cobrindo arquivos `.sql` e migrações. Cada script precisa declarar a ordem de execução e ter um rollback correspondente.

   Cada subagente devolve achados no formato do `achados.json`.
4. Junte os achados, tire os repetidos e os que estão em `publicados`, e ordene por gravidade.
5. Mostre a lista numerada (`ponto · gravidade · repo/PR · arquivo:linha · título` e o texto).
6. Pergunte quais números publicar e se o revisor quer editar algum texto. Sem escolha, não publique nada.
7. Grave os escolhidos em `.ws/revisao/<id>/achados.json` e rode `tools/ws/ws pr comentar <contexto> <achados>`.
8. Mostre a saída. O harness não aprova nem reprova o PR: a decisão é do revisor.

- [ ] **Step 1: Teste.** Em `test_harness.sh`, `test_skill_ws_revisar_cobre_os_cinco_pontos` confere que `.claude/skills/ws-revisar/SKILL.md` contém `tools/ws/ws pr revisao`, `tools/ws/ws pr comentar`, `conformidade`, `contratos`, `regras`, `defeitos`, `banco`, `rollback`, `ordem de execução`, `Sem escolha, não publique nada` e `não aprova nem reprova`.
- [ ] **Step 2: Rode o teste e confirme que falha.**
- [ ] **Step 3: Escreva a skill.**
- [ ] **Step 4: Rode o teste e confirme que passa.**
- [ ] **Step 5: Commit** `harness: skill ws-revisar (SP7)`.

---

### Task 7: Oferta dos PRs nos comandos do Spec Kit e comando `promover`

**Files:**
- Modify:
  - `tools/speckit/ws/commands/speckit.ws.commit-push.md` (passo 7);
  - `speckit.ws.bug-enviar.md` (passo 5);
  - `speckit.ws.refactor-enviar.md` (passo 5);
  - `speckit.ws.bug-sem-correcao.md` (fim);
  - `tools/speckit/refactor/commands/speckit.refactor.subida.md` (linha "sem chave, plano revisado");
  - `tools/speckit/ws/extension.yml` (comando novo e versão `1.7.0`);
  - `tools/ws/lib/push.sh` (última linha);
  - `tools/ws/tests/test_speckit_refactor.sh` (`test_enviar_sem_chave_deixa_o_pr_aberto_ate_a_janela`);
  - `tools/ws/tests/test_speckit_install.sh` (lista de comandos, se ela enumerar).
- Create: `tools/speckit/ws/commands/speckit.ws.promover.md`
- Regenerate: `.claude/skills/speckit-ws-*` com `tools/ws/ws speckit`.

**Interfaces:**
- Consumes: `ws pr plano` e `ws pr abrir` (Tasks 1 a 4).
- Produces: o comando `speckit.ws.promover`, só como comando, sem hook.

Texto comum da oferta, nos três comandos de envio:
1. Rode `tools/ws/ws pr plano homolog` e mostre a saída.
2. Se ele falhar, mostre a mensagem e os links e pare.
3. Pergunte se o dev quer abrir esses PRs e postar no espaço de homologação.
4. Com o sim, rode `tools/ws/ws pr abrir homolog` e mostre os links. Com o não, mostre os links `pullrequestcreate` e diga que os PRs ficam com ele.
5. Lembre que o PR do workspace é completado **por último** e que nenhuma branch de origem deve ser apagada.

Mudanças específicas:
- **`refactor-enviar`, card sem chave:** troque "o time integra a branch na `homolog`" e "Não abra o PR do workspace do card" pela oferta acima. Os PRs dos repos para `main` não são abertos no card: a promoção sai da branch de subida (`/speckit-ws-promover` nela, depois da janela aprovada na homologação).
- **`subida`:** "sem chave, plano revisado" passa a dizer: rode `/speckit-ws-promover` nesta branch para abrir os PRs para `main`. Na janela, complete-os na ordem do plano e o do workspace por último.
- **`bug-sem-correcao`:** ofereça `tools/ws/ws pr abrir main` para o PR do workspace, porque não há o que homologar.
- **`promover`:** rode `tools/ws/ws pr plano main` e mostre os avisos de PR de teste aberto. Pergunte se segue. Com o sim, rode `tools/ws/ws pr abrir main`. Mostre a recriação de branch, se houver, e os links.
- **`push.sh`:** troque a última linha por `log "para abrir os PRs: tools/ws/ws pr plano homolog"`.

- [ ] **Step 1: Testes** (grep no texto, como no SP6.2)
  - `test_enviar_oferece_os_prs_de_teste`: os três comandos de envio contêm `ws pr plano homolog`, `ws pr abrir homolog` e `por último`.
  - `test_enviar_sem_chave_abre_os_prs_de_teste_do_card`, que substitui o teste antigo: o `refactor-enviar` contém `/speckit-ws-promover` e `branch de subida`, e **não** contém `Não abra o PR do workspace do card`.
  - `test_promover_abre_main`: o `speckit.ws.promover.md` contém `ws pr plano main` e `ws pr abrir main`, e o `extension.yml` lista `speckit.ws.promover`.
  - `test_push_sugere_ws_pr`: no `test_push.sh`, o `OUT` do `ws push` contém `tools/ws/ws pr plano homolog`.
- [ ] **Step 2: Rode os testes e confirme que falham.**
- [ ] **Step 3: Edite os comandos, o `extension.yml` e o `push.sh`.** Faça o commit, depois rode `tools/ws/ws speckit` (que exige a árvore limpa e rede para o `uvx`) e commite as skills geradas.
- [ ] **Step 4: Rode a suíte inteira e confirme que passa.** Comando: `bash tools/ws/tests/run.sh`. Esperado: `0 falha(s)`.
- [ ] **Step 5: Commit** `harness: oferta dos PRs e promoção nos comandos do Spec Kit (SP7)`.

---

### Task 8: Documentação, `AGENTS.md` e ADR

**Files:**
- Modify:
  - `AGENTS.md` (linhas dos "PRs" nas seções de feature, bug e refactor);
  - `docs/harness/1-comecar.md` (passo 9 da feature, passo 7 do bug, passo 5 do refactor e a nova seção "Revisar um PR");
  - `docs/harness/2-quando-da-errado.md`: reescreva "Abri o PR do workspace antes dos PRs dos repos" e acrescente estas entradas, com o texto exato do erro e o que fazer:
    - `az` não autenticado;
    - sem ramo de teste;
    - branch apagada sem PR completado;
    - falha no Chat;
    - "o PR não veio do harness";
  - `docs/harness/3-alem-do-basico.md` (linhas 75, 178 e 193–201);
  - `docs/harness/4-manter.md` (o `workspace.pr.ini`: webhooks, ramo de teste por repo e o que fazer quando um time cria ou muda o ramo de teste);
  - `docs/adr/0001-workspace-git-subtree.md` (adendo 7: PRs abertos pelo harness, ramo de teste e regra "workspace por último").

O texto da regra é sempre o mesmo: "Os PRs saem pelo harness: para o ramo de teste no fim do envio e para o `main` com `/speckit-ws-promover`. O PR do workspace é aberto junto e completado por último."

- [ ] **Step 1: Teste.** Rode o `test_docs_referencias.sh` existente e acrescente `test_docs_sem_a_regra_antiga`, que confere que `AGENTS.md` e `docs/harness/[1-4]*.md` não contêm `Depois vem o PR do workspace` nem `com **todos** mergeados`.
- [ ] **Step 2: Rode o teste e confirme que falha.**
- [ ] **Step 3: Edite os documentos.**
- [ ] **Step 4: Rode a suíte inteira e confirme que passa.**
- [ ] **Step 5: Commit** `harness: documentação dos PRs e da revisão (SP7)`.

---

### Task 9: Validação real no Azure DevOps (com o usuário)

Não há código aqui. É o roteiro do SP1 e do SP2, registrado num `docs/discovery/sp7-validacao.md` do repo de discovery.

- [ ] **Step 1: Pré-requisitos (usuário).**
  - a branch `homolog` do workspace criada;
  - as duas URLs de webhook de teste, ou as reais, em `workspace.pr.ini`;
  - `az login` feito;
  - um repo de teste com `homolog`, por exemplo o `wms.picking.backend`.
- [ ] **Step 2: Entrega de teste.** Rode `ws start` numa branch `teste/sp7-<data>`, faça uma mudança trivial no repo de teste e em `specs/`, e rode `/speckit-ws-commit-push`. Com o sim, confira os 2 PRs para `homolog` no Azure DevOps, a tabela, os avisos e a mensagem no espaço de homologação.
- [ ] **Step 3: Revisão.** Rode `/ws-revisar <link>` e publique 1 achado de linha e 1 geral. Confira que eles aparecem no PR certo. Rode de novo e confira que nada se repete.
- [ ] **Step 4: Promoção.** Complete o PR do repo para `homolog` **apagando a branch** e rode `/speckit-ws-promover`. Confira a recriação da branch, os PRs para `main` e a mensagem no espaço de produção.
- [ ] **Step 5: Limpeza (usuário).** Abandone os PRs para `main` e apague as branches de teste. Anote o resultado e os tempos em `sp7-validacao.md`.
