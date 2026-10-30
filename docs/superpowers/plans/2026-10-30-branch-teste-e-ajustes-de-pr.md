# Branch de teste por repo e ajustes de PR na feature: plano de implementação

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** O PR de teste de cada repo sai sempre de `<branch>-teste` (feature + ramo de teste, com as resoluções de conflito), a `<branch>` fica só com a feature para o `main`, o `ws push` ganha guarda e `--sobrescrever`, e o dev ganha a skill `/ws-pr-resolve-comments`; a ws-002 é corrigida antes, à mão.

**Architecture:** Novo `tools/ws/lib/teste.sh` (`ws teste`, `ws teste continuar`, `ws teste abortar`) que faz os merges num clone blobless de cache por repo em `.ws/teste/<nome>/`, fora do histórico raso do workspace. O `ws push` passa a calcular o split explicitamente (`git subtree-ws split`), aplicar a guarda contra a ponta remota e, depois do envio, atualizar a `-teste` pelo mesmo cache. O `ws pr` (Python) usa a `-teste` como origem dos PRs de teste dos repos e ganha `comentarios` e `responder` para a skill nova.

**Tech Stack:** bash + git (Git for Windows, `tools/ws/vendor/git-subtree-ws`), Python 3 (`tools/ws/pr/`), az CLI (fake nos testes: `tools/ws/tests/fake_az.py`), skills do Claude Code em `.claude/skills/`.

**Spec:** `docs/superpowers/specs/2026-10-30-branch-teste-e-ajustes-de-pr-design.md` (neste repo de discovery).

**Onde:** o código fica no workspace `C:\src\wms-workspace` (origin `industria-logistica.wms.workspace`). Tasks 2 a 8 numa worktree nova `C:\src\wms-workspace-teste`, branch `harness/branch-teste`, saindo do `origin/main` (`4cae287f3` ou mais novo). A Task 1 roda na branch `ws-002-chaves-centrais` do usuário, em `C:\src\wms-workspace`. Testes: `bash tools/ws/tests/run.sh [arquivo]` (`WS_TEST=<nome>` roda um só). No Git Bash, `export MSYS_NO_PATHCONV=1` antes de `git show <ref>:<caminho>`.

## Global Constraints

- Sufixo da branch de teste no repo: `-teste` (`<branch>-teste`), sempre, para todo PR de repo para o ramo de teste.
- Ramo de teste por repo: `workspace.pr.ini`, seção `[teste]` (`padrao = homolog`; exceções por prefixo). O shell lê o mesmo arquivo que `tools/ws/pr/config.py`.
- O PR do workspace não muda: sai da branch da feature para a `homolog` do workspace e para o `main`.
- Nada é enviado com força sem `ws push --sobrescrever <repo>`; a força é sempre `--force-with-lease` contra a ponta registrada pela guarda.
- O ramo de teste e as resoluções de conflito nunca entram na branch da feature nem na `<branch>`.
- CLI, mensagens, commits, docs e configuração em português; o que o dev digita ou vê como skill fica em inglês (`/ws-pr-resolve-comments`), como no SP8. Mensagens de commit do `ws`: `ws: ...`. Sem atribuição do Claude nos commits e PRs do workspace (`.claude/settings.json`).
- Saída de erro do `ws`: `ws: erro: ...` (via `die`); aviso: `ws: aviso: ...`; guarda: `ws: GUARDA: ...`.
- Estado local em `.ws/` (já no `.gitignore`).
- `AGENTS.md`: proíbe `git subtree` à mão e `git push` para os repos; o `ws` é a única porta.

## Review Focus

- **Histórico raso do workspace:** o `ws` busca os repos com `--depth=1`, e os commits de fronteira ficam no `.git/shallow`. Um merge do ramo de teste feito no objeto do workspace acharia uma base comum errada ou nenhuma ("refusing to merge unrelated histories"). Por isso o merge roda no cache blobless de `.ws/teste/<nome>/`. Teste: `test_teste_merge_com_workspace_raso` (Task 3).
- **Rodar `ws teste` de novo sem nada novo:** não cria commit vazio nem falha no push. Teste: `test_teste_sem_novidade_nao_cria_commit` (Task 3).
- **`ws teste continuar` com marcador de conflito ainda no arquivo:** recusa e lista os arquivos. Teste: `test_teste_continuar_recusa_marcador` (Task 3).
- **`-teste` andou no origin entre a busca e o envio** (o botão do Azure, ou outro dev): o envio sem force é recusado e a mensagem manda rodar de novo, sem perder nada. Teste: `test_teste_recusa_quando_a_teste_andou` (Task 3).
- **Caminho com acento ou espaço na lista de conflito:** sai legível (`core.quotePath=false`). Teste: `test_teste_lista_conflito_com_acento` (Task 3).

---

### Task 1: Correção da ws-002 (manual, uma vez)

Spec 3.8. Sem código novo; cada passo de escrita pede confirmação do usuário antes. Repos: `repos/industria-logistica.wms.awx.monorepo`, `repos/industria-logistica.wms.servidor.backend`, `repos/integracoes.wms.servicos-linx-wms.monorepo`; branch `ws-002-chaves-centrais` nos três e no workspace (`C:\src\wms-workspace`). Ramos de teste: `homolog` (AWX, linx) e `release` (servidor.backend, conforme o PR 17267; conferir no `workspace.pr.ini` do `origin/main`, e se ele disser outra coisa, perguntar ao usuário).

**Files:**
- Create (neste repo de discovery): `docs/discovery/ws-002-correcao.md` (registro do que foi trazido, dos SHAs antes e depois e das confirmações)

- [ ] **Step 1: Conferir o estado.** Em `C:\src\wms-workspace`: `git switch ws-002-chaves-centrais`, `git status --porcelain` vazio (senão, pare e pergunte). Para cada repo, `az repos pr list --repository <nome> --source-branch ws-002-chaves-centrais --status active` (sem PR para o `main` ativo esperado; se houver, registre e pergunte antes de reescrever).
- [ ] **Step 2: Buscar o histórico de cada repo num cache fora do workspace** (scratchpad da sessão): `git init --bare` + `git fetch --filter=blob:none <url> +refs/heads/ws-002-chaves-centrais:refs/heads/f +refs/heads/<ramo de teste>:refs/heads/t +refs/heads/main:refs/heads/main`.
- [ ] **Step 3: Listar os candidatos:** `git log --no-merges --format='%h %an %ad %s' f ^t ^<split atual do workspace>`, onde o split é `git subtree-ws split --prefix=<prefixo> ws-002-chaves-centrais` (com `PATH="tools/ws/vendor:$PATH"`). Esperado, pelo feedback: AWX 1 commit de revisão de 28/10 + o ajuste de teste de 29/10 (`43c8333`, que fica de fora); servidor.backend 1 commit de 28/10; linx 2 commits de 28/10. Mostre a lista ao usuário e peça confirmação de quais entram.
- [ ] **Step 4: Trazer os confirmados para a feature** com o autor original: `git -C <cache> format-patch -1 <sha> --stdout | git am --directory=<prefixo> -3` no workspace, um por um, na ordem do histórico. Conflito no `am`: resolva com o usuário.
- [ ] **Step 5: Conferir a feature:** `git diff <split antigo>..<split novo>` (por repo) mostra só as mudanças dos commits trazidos.
- [ ] **Step 6: Reescrever cada `<branch>` no repo, com confirmação do usuário por repo:** `git push --force-with-lease=refs/heads/ws-002-chaves-centrais:<ponta lida no Step 2> <url> <split novo>:refs/heads/ws-002-chaves-centrais`.
- [ ] **Step 7: Verificar:** para cada repo, `git ls-remote <url> refs/heads/ws-002-chaves-centrais` = split novo; `git rev-list --count main..<split novo>` no cache (depois de um novo fetch) mostra só commits da feature (nenhum `Merged PR` da homolog). Registre em `docs/discovery/ws-002-correcao.md` e faça commit neste repo de discovery. Diga ao usuário que pode seguir com `/ws-pr-main` (o `recria_branches` do código atual não age, porque as branches existem).

### Task 2: Guarda e `--sobrescrever` no `ws push`

**Files:**
- Modify: `tools/ws/lib/push.sh` (`ws_push`)
- Create: `tools/ws/lib/teste.sh` (só `ws_ramo_teste` e `ws_nome_repo` nesta task)
- Test: `tools/ws/tests/test_push.sh`

**Interfaces:**
- Produces:
  - `ws_split <prefixo>` → imprime o SHA do split de `HEAD` (`PATH="$WS_LIB/../vendor:$PATH" git subtree-ws split --prefix=<prefixo> HEAD`), em `push.sh`.
  - `ws_ponta_remota <url> <branch>` → SHA de `refs/heads/<branch>` no repo, ou vazio; em `push.sh`.
  - `ws_ramo_teste <prefixo>` → ramo de teste lido de `workspace.pr.ini` `[teste]` (chave do prefixo, senão `padrao`, senão `homolog`); em `teste.sh`.
  - `ws_nome_repo <url>` → último segmento da URL sem `.git` (igual a `nome_da_url` do Python); em `teste.sh`.
  - Arquivo `.ws/guarda/<nome do repo>`: a ponta remota recusada pela guarda.
  - `ws push [--sobrescrever <repo>...]`, onde `<repo>` é o nome do repo ou o prefixo `repos/<nome>`.

- [ ] **Step 1: Testes que falham**, em `test_push.sh`, usando `fx_ready`, `ws start feat/a`, `ws push` e um commit direto no remoto na branch `feat/a` (helper novo `commit_na_branch <repo> <branch> <arquivo> <conteúdo>` em `lib.sh`, no molde de `upstream_commit`):
  - `test_push_guarda_para_quando_o_repo_tem_commit_fora`: depois do commit direto em `r1`/`feat/a` e de um novo commit no workspace em `repos/r1` e `repos/r2`, `ws push` falha; `OUT` contém `GUARDA: repos/r1` e o assunto do commit direto; a ponta de `r2`/`feat/a` não mudou (tudo ou nada); `.ws/guarda/r1` contém a ponta de `r1`/`feat/a`.
  - `test_push_sobrescrever_envia_com_lease`: na mesma situação, `ws push --sobrescrever r1` passa; `r1`/`feat/a` = split de `HEAD` (`wslib ws_split repos/r1`); `r2` também avançou.
  - `test_push_sobrescrever_recusa_se_o_repo_andou_de_novo`: guarda, outro commit direto em `r1`/`feat/a`, `ws push --sobrescrever r1` falha com `GUARDA: repos/r1` e o assunto do segundo commit; nada enviado.
  - `test_push_sobrescrever_sem_guarda_registrada_falha`: `ws push --sobrescrever r1` sem `.ws/guarda/r1` falha com `rode ws push primeiro`.
  - `test_ramo_teste_le_o_ini`: com `workspace.pr.ini` de `fx_pr` (`padrao = homolog`, `repos/r2 = develop`), `wslib ws_ramo_teste repos/r1` = `homolog` e `wslib ws_ramo_teste repos/r2` = `develop`; sem o arquivo, `homolog`.
- [ ] **Step 2: Rodar** `bash tools/ws/tests/run.sh tools/ws/tests/test_push.sh` → os 5 novos falham, os antigos passam.
- [ ] **Step 3: Implementar.** Em `ws_push`: ler as opções; para cada prefixo, depois das validações atuais, calcular `S=$(ws_split p)` e `R=$(ws_ponta_remota url br)`; se `R` não vazio e `R` ≠ `S` e `R` não é ancestral de `S` (buscar `R` com `ws_fetch_shallow` se faltar o objeto), é violação: imprimir `ws: GUARDA: <prefixo>: a branch <br> no repo tem commits que não estão no workspace:` + `git log --format='  %h %an %ad %s' --date=short R ^S` (limitado a 20) e gravar `R` em `.ws/guarda/<nome>`. Repo em `--sobrescrever` com `.ws/guarda/<nome>` = `R` atual não é violação e vai com `--force-with-lease=refs/heads/<br>:R`; com arquivo diferente, é violação de novo (atualiza o arquivo). Com violação: `die "push recusado; nada foi enviado. Traga a mudança para a feature, faça commit e rode ws push --sobrescrever <repos> (docs/harness/2-quando-da-errado.md)"`. O envio passa a ser `git -c http.version=HTTP/1.1 -c http.postBuffer=524288000 push <url> S:refs/heads/<br>` (o split já calculado; sai o `subtree-ws push`). Apagar `.ws/guarda/<nome>` depois do envio.
- [ ] **Step 4: Rodar** a suíte inteira `bash tools/ws/tests/run.sh` → tudo ok.
- [ ] **Step 5: Commit** `ws push: guarda contra commits só no repo e --sobrescrever`.

### Task 3: `ws teste`, `ws teste continuar`, `ws teste abortar`

**Files:**
- Modify: `tools/ws/lib/teste.sh`, `tools/ws/ws` (caso `teste` e texto de uso)
- Test: `tools/ws/tests/test_teste.sh` (novo), helper `cria_ramo` movido de `pr_lib.sh` para `lib.sh`

**Interfaces:**
- Consumes: `ws_split`, `ws_ponta_remota`, `ws_ramo_teste`, `ws_nome_repo` (Task 2); `ws_changed_prefixes`, `ws_url_of`, `current_branch`, `require_clean`.
- Produces:
  - `ws_teste_cache <url>` → caminho de `.ws/teste/<nome>/`: clone criado com `git init` + `remote add origin <url>` na primeira vez; a cada chamada, `git fetch --filter=blob:none origin` só dos refs pedidos.
  - `ws_teste_repo <prefixo> <url> <branch> [--sem-ramo]` → 0 enviado ou já em dia; 2 parou em conflito (merge em andamento no cache); morre nos outros erros. `--sem-ramo` faz só o merge da `<branch>` (usado pela Task 4).
  - `ws teste` / `ws teste continuar` / `ws teste abortar` (seção 3.2 da spec). Saída por repo: `ws: <prefixo>: <branch>-teste enviada` ou `ws: <prefixo>: <branch>-teste já em dia`.
  - Em conflito, a saída tem `ws: <prefixo>: conflito em .ws/teste/<nome>/`, e duas listas: `arquivos que a feature muda:` e `arquivos que a feature não muda:` (cada linha `  <caminho no repo>`), e termina com `resolva lá e rode tools/ws/ws teste continuar (ou tools/ws/ws teste abortar)`. Código de saída 3.
  - Mensagens de merge: `ws: traz <branch> para <branch>-teste` e `ws: traz <ramo> para <branch>-teste`.

- [ ] **Step 1: Testes que falham**, em `test_teste.sh` (fixture: `fx_ready`, `cria_ramo r1 homolog`, `ws start feat/a`, commit em `repos/r1/src/app.txt`, `ws push`):
  - `test_teste_cria_a_teste_sem_conflito`: `upstream` muda `README.md` na `homolog` de r1; `ws teste` passa; `r1`/`feat/a-teste` tem os dois pais (`feat/a` e `homolog` são ancestrais); `r1`/`feat/a` não mudou.
  - `test_teste_sem_novidade_nao_cria_commit`: segundo `ws teste` → `já em dia`, a ponta de `feat/a-teste` não muda.
  - `test_teste_exige_push_feito`: novo commit no workspace sem `ws push`; `ws teste` falha com `rode /ws-commit-push`.
  - `test_teste_conflito_lista_os_dois_grupos`: a `homolog` de r1 sai do `main` antigo e muda `src/app.txt` e `README.md`; depois do `cria_ramo`, o `main` de r1 muda `README.md` de outro jeito (`upstream_commit`) e o `ws start` traz isso; a feature muda `src/app.txt`. Assim `src/app.txt` conflita e a feature o muda, e `README.md` conflita sem a feature mudá-lo. `ws teste` sai com 3; `OUT` traz `src/app.txt` em `arquivos que a feature muda:` e `README.md` em `arquivos que a feature não muda:`; nada enviado.
  - `test_teste_continuar_envia`: depois do conflito, resolver em `.ws/teste/r1/` (escrever o conteúdo e `git add`), `ws teste continuar` passa e envia; `feat/a-teste` contém a resolução.
  - `test_teste_continuar_recusa_marcador`: resolver deixando `<<<<<<<` num arquivo e dar `git add`; `ws teste continuar` falha listando o arquivo.
  - `test_teste_abortar`: `ws teste abortar` descarta o merge; `ws teste continuar` em seguida falha com `nenhum conflito em andamento`.
  - `test_teste_outro_repo_segue_quando_um_conflita`: r1 conflita e r2 não; r2 recebe `feat/a-teste`; r1 não.
  - `test_teste_parte_da_teste_existente`: depois de uma `-teste` enviada, um commit direto em `r1`/`feat/a-teste` (botão do Azure) é preservado no próximo `ws teste`.
  - `test_teste_recusa_quando_a_teste_andou`: simule a corrida com um hook `pre-receive` no bare de r1 que recusa o primeiro push para `feat/a-teste` como `non-fast-forward`; `ws teste` falha com `a <branch>-teste mudou no repo; rode ws teste de novo`.
  - `test_teste_merge_com_workspace_raso`: fixture em que o `main` do r1 tem 3 commits antes da `homolog` divergir e o workspace só tem o `main` com `--depth=1` (o `ws add` normal já faz isso); `ws teste` faz o merge sem "unrelated histories".
  - `test_teste_lista_conflito_com_acento`: conflito em `src/conferência.txt`; a lista mostra o nome com acento, sem aspas nem escapes.
  - `test_teste_sem_ramo_de_teste_no_repo`: r1 sem `homolog`; `ws teste` falha com `o repo r1 não tem o ramo de teste homolog`.
- [ ] **Step 2: Rodar** `bash tools/ws/tests/run.sh tools/ws/tests/test_teste.sh` → todos falham (`uso: ws <...>`).
- [ ] **Step 3: Implementar** `teste.sh` e o caso `teste` no `tools/ws/ws`. Ordem por repo: `S=$(ws_split p)`; se `ws_ponta_remota url br` ≠ `S`, `die "<prefixo>: a <br> no repo não é a da feature; rode /ws-commit-push antes"`; no cache, buscar `br`, o ramo e `br-teste` (se existir); `checkout -B br-teste` a partir de `origin/br-teste` ou `origin/br`; `merge --no-ff -m "ws: traz <br> para <br>-teste" origin/br` (pular se ancestral); depois o mesmo com `origin/<ramo>` (a menos de `--sem-ramo`); se a ponta não mudou, `já em dia`; senão `push origin br-teste:refs/heads/br-teste` sem force. A classificação dos arquivos usa `git diff --name-only <base>...HEAD -- <prefixo>` no workspace (os da feature) contra `git diff --name-only --diff-filter=U` no cache. O estado do conflito em andamento fica em `.ws/teste/em-andamento` (linhas `prefixo url branch`), e `continuar` retoma pelo repo em conflito e segue para os que faltavam. Use `-c core.quotePath=false` em toda listagem.
- [ ] **Step 4: Rodar** a suíte inteira → tudo ok.
- [ ] **Step 5: Commit** `ws teste: branch de teste por repo com os merges num cache blobless`.

### Task 4: `ws push` mantém a `-teste` em dia

**Files:**
- Modify: `tools/ws/lib/push.sh`
- Test: `tools/ws/tests/test_teste.sh`

**Interfaces:**
- Consumes: `ws_teste_repo <prefixo> <url> <branch> --sem-ramo` (Task 3).

- [ ] **Step 1: Testes que falham:**
  - `test_push_atualiza_a_teste_existente`: com `feat/a-teste` em r1, um commit novo na feature e `ws push` → `feat/a-teste` contém o commit novo (o novo split é ancestral) e não traz commit novo da `homolog` (um commit posterior na `homolog` não é ancestral).
  - `test_push_nao_cria_teste`: sem `feat/a-teste` no repo, `ws push` não a cria.
  - `test_push_teste_reconflita`: a resolução da `-teste` escolheu a versão da `homolog` para `src/app.txt`, e o ajuste novo da feature muda as mesmas linhas; `ws push` envia `feat/a` e sai com erro contendo `<prefixo>: a feat/a foi enviada, mas a feat/a-teste conflitou; rode tools/ws/ws teste`; o cache fica sem merge em andamento.
- [ ] **Step 2: Rodar** → os 3 falham.
- [ ] **Step 3: Implementar:** no fim de `ws_push`, para cada prefixo enviado com `br-teste` existente no repo, `ws_teste_repo p url br --sem-ramo`; em conflito, abortar o merge no cache, juntar os prefixos e morrer no fim com a mensagem acima (os outros repos seguem).
- [ ] **Step 4: Rodar** a suíte inteira → tudo ok.
- [ ] **Step 5: Commit** `ws push: atualiza a branch de teste do repo`.

### Task 5: `ws pr` com a `-teste`

**Files:**
- Modify: `tools/ws/pr/abrir.py` (`itens_do_plano`, `links_manuais`, `_preparar`, `plano`, `recria_branches`, `abrir`), `tools/ws/pr/entrega.py` (só se precisar do nome da origem)
- Test: `tools/ws/tests/test_pr.sh`

**Interfaces:**
- Produces: `Item = namedtuple("Item", "prefixo nome url ramo origem")`; `origem` = `f"{ent.branch}-teste"` para repo no destino `homolog` e `ent.branch` nos outros casos; `_ws_teste(raiz)` roda `tools/ws/ws teste` como `_ws_push` roda o push.

- [ ] **Step 1: Testes que falham** (fixture `fx_pr` + `fx_entrega`):
  - `test_pr_abrir_homolog_usa_a_teste`: `ws pr abrir homolog` cria `feat/a-teste` em r1 e r2 e abre os PRs dos repos com origem `refs/heads/feat/a-teste`; o do workspace com origem `feat/a` (`pr_estado`).
  - `test_pr_abrir_homolog_para_no_conflito`: com conflito em r1, `abrir homolog` falha, mostra a saída do `ws teste` e nenhum PR é criado.
  - `test_pr_plano_homolog_mostra_a_origem`: `plano homolog` imprime `ws: PR r1 feat/a-teste -> homolog` e links com `sourceRef=feat/a-teste`.
  - `test_pr_plano_main_avisa_teste_aberto`: PR ativo `feat/a-teste` → `homolog` semeado; `plano main` avisa `PR para o ramo de teste ainda aberto: r1`.
  - `test_pr_transicao_mantem_pr_antigo`: PR ativo `feat/a` → `homolog` semeado em r1 (fluxo antigo); `abrir homolog` atualiza esse PR, avisa `r1 segue com o PR de teste antigo (feat/a)` e não abre outro.
  - `test_pr_main_nao_recria_a_partir_do_pr_de_teste`: `feat/a` apagada em r1 e PR completado `feat/a-teste` → `homolog` semeado; `abrir main` não chama `criar_ref` para r1 (o `ws push` recria a branch a partir da feature).
  - Ajustar os testes atuais de `abrir homolog` que esperam origem `feat/a` nos repos.
- [ ] **Step 2: Rodar** `bash tools/ws/tests/run.sh tools/ws/tests/test_pr.sh` → os novos falham.
- [ ] **Step 3: Implementar.** `abrir homolog` chama `_ws_teste` antes de qualquer PR (depois de `_preparar`), exceto para repos em transição (PR ativo de `ent.branch` para o ramo de teste: usam `origem = ent.branch`). `recria_branches` passa a cuidar só do workspace e, para repos, da subida sem PR de teste (o caso `-rollout` atual). O `ws pr revisao` não muda: ele acha os PRs dos repos pela tabela da descrição do PR do workspace, que o `abrir` já monta com os PRs da `-teste`, e o diff vem da branch da feature.
- [ ] **Step 4: Rodar** a suíte inteira → tudo ok.
- [ ] **Step 5: Commit** `ws pr: PRs de teste dos repos a partir da branch -teste`.

### Task 6: `ws pr comentarios` e `ws pr responder`

**Files:**
- Create: `tools/ws/pr/comentarios.py`
- Modify: `tools/ws/pr/__main__.py` (`USO` e roteamento), `tools/ws/pr/azure.py` (`listar_prs_da_origem`, `responder_thread`), `tools/ws/tests/fake_az.py` (rota `pullRequestThreadComments` POST e `repos pr list` sem `--target-branch`)
- Test: `tools/ws/tests/test_pr_comentarios.sh` (novo)

**Interfaces:**
- Produces:
  - `Azure.listar_prs_da_origem(repo, origem, status) -> list` (`repos pr list` sem `--target-branch`).
  - `Azure.responder_thread(repo, pr_id, thread_id, texto) -> dict` (`devops invoke --area git --resource pullRequestThreadComments`, POST, `{"content": texto, "parentCommentId": 1, "commentType": 1}`).
  - `ws pr comentarios [<link>]` → grava `.ws/comentarios/<branch com / trocada por _>/contexto.json` e imprime o caminho. Sem link: PRs ativos da branch atual com origem `<branch>` ou `<branch>-teste` em cada repo da entrega, mais o do workspace com origem `<branch>`. Com link: só aquele PR (de repo ou do workspace).
  - Formato do `contexto.json`: `{"branch", "threads": [{"repo", "prefixo", "pr_id", "pr_url", "destino", "na_teste": bool, "thread_id", "arquivo", "linha", "comentarios": [{"autor", "texto", "data"}]}]}`. `arquivo` no caminho do workspace (`repos/<prefixo>/<caminho no repo>`; no PR do workspace, o caminho como está); `linha` = `rightFileStart.line`; ambos `null` em thread geral.
  - Filtro: status `active`; primeiro comentário com `commentType` diferente de `system`; último comentário de alguém que não é o autor do PR (`createdBy.id`).
  - `ws pr responder <contexto.json> <respostas.json>`; `respostas.json` = `[{"pr_id", "repo", "thread_id", "texto"}]`. Cada texto ganha a marca `<!-- ws-resposta -->`; thread cujo último comentário já tem a marca é pulado (`ws: já respondido: ...`). Imprime `ws: respondido <repo> !<pr_id> #<thread_id>`.
- [ ] **Step 1: Testes que falham** (fixture `fx_pr` + `fx_entrega` + PRs e threads semeados no fake):
  - `test_comentarios_sem_link_junta_os_prs_da_branch`: threads em `r1` (`feat/a` → `main`), em `r1` (`feat/a-teste` → `homolog`, `na_teste` true) e no workspace; todos no JSON, com `arquivo` `repos/r1/src/app.txt` e a `linha`.
  - `test_comentarios_filtra_sistema_resolvido_e_respondido`: thread de sistema, thread `fixed` e thread cujo último comentário é do autor do PR ficam de fora.
  - `test_comentarios_com_link_de_repo`: só as threads daquele PR.
  - `test_responder_publica_e_nao_repete`: duas respostas → dois comentários no fake com a marca; rodar de novo → `já respondido` e nenhum comentário novo.
  - `test_responder_recusa_thread_fora_do_contexto`: `thread_id` que não está no `contexto.json` → erro, nada publicado.
- [ ] **Step 2: Rodar** → falham.
- [ ] **Step 3: Implementar** `comentarios.py` no molde de `revisao.py` (mesmo `_LINK`, mesma escrita UTF-8 com `newline="\n"`).
- [ ] **Step 4: Rodar** a suíte inteira → tudo ok.
- [ ] **Step 5: Commit** `ws pr: comentarios e responder para a skill do dev`.

### Task 7: Skills `/ws-pr-resolve-comments` e `/ws-pr-homolog`

**Files:**
- Create: `.claude/skills/ws-pr-resolve-comments/SKILL.md`
- Modify: `.claude/skills/ws-pr-homolog/SKILL.md`
- Test: `tools/ws/tests/test_docs_referencias.sh` (já roda sobre as skills; acrescentar o caso se ele não cobrir a pasta nova)

**Interfaces:**
- Consumes: `ws pr comentarios`, `ws pr responder` (Task 6); `ws teste` (Task 3); `/ws-commit-push`, `/speckit-converge`, `atlas-consultar`/`/atlas-atualizar`.

- [ ] **Step 1: Escrever a `/ws-pr-resolve-comments`** no molde da `/ws-pr-review` (frontmatter `name`/`description` com quando usar e quando não usar; bloco **Idioma**; `User Input`). Passos: (1) `tools/ws/ws pr comentarios [link]` e ler o JSON; sem threads, dizer e parar. (2) Ler a origem da entrega (spec/tasks, assessment ou rollout-plan), a constitution, o `AGENTS.md` e o código citado. (3) Para cada thread, propor `aplicar` ou `não aplicar` com o motivo; thread com `na_teste` sobre arquivo que a feature não muda → `resolver na -teste` (pelo `ws teste`), nunca na feature. (4) Mostrar a lista numerada e **esperar a confirmação do dev**, que pode mudar decisões. (5) Aplicar só o aceito, na branch da feature; `/speckit-converge` quando muda comportamento da spec; Atlas quando toca contrato. (6) `/ws-commit-push`; se o push falhar (guarda ou conflito da `-teste`), mostrar a orientação e parar sem responder. (7) Montar `respostas.json` (o que foi feito, com o SHA curto do commit do workspace, ou por que não), mostrar ao dev e rodar `ws pr responder`. (8) Lembrar que o "Resolved" é dele. Nunca usar os botões do Azure de aplicar sugestão.
- [ ] **Step 2: Ajustar a `/ws-pr-homolog`:** o passo 5 explica que o `abrir homolog` roda o `ws teste`; em conflito (saída com as duas listas), conduzir a resolução em `.ws/teste/<nome>/` (para os arquivos que a feature não muda, sugerir a versão do ramo de teste; o dev decide), rodar `tools/ws/ws teste continuar` e o `abrir homolog` de novo. O passo 6 passa a dizer que a `<branch>-teste` pode ser apagada ao completar; a branch da feature no repo e a do workspace não.
- [ ] **Step 3: Rodar** a suíte inteira → tudo ok.
- [ ] **Step 4: Commit** `skills: ws-pr-resolve-comments e conflito do ramo de teste na ws-pr-homolog`.

### Task 8: Regras e docs

**Files:**
- Modify: `AGENTS.md`, `docs/harness/1-comecar.md`, `docs/harness/2-quando-da-errado.md`, `docs/harness/3-alem-do-basico.md`, `docs/harness/4-manter.md`, `README.md` (o "Quero…"), `docs/adr/0001-workspace-git-subtree.md` (adendo 7)

- [ ] **Step 1: `AGENTS.md`:** regra "todo ajuste de PR de feature, bug ou refactor é feito na branch da feature e sai pelo `ws push`"; não usar os botões do Azure de aplicar sugestão nem de resolver conflito; o PR de teste de cada repo sai da `<branch>-teste`.
- [ ] **Step 2: Camada 1:** seção "Ajustes pedidos na revisão do PR" (`/ws-pr-resolve-comments`) e "O PR de teste conflitou com o ramo de teste" (`/ws-pr-homolog`, `ws teste`); linhas no "Quero…" do README.
- [ ] **Step 3: Camada 2:** uma entrada por mensagem nova, no formato Sintoma / Causa / O que fazer: `GUARDA: <prefixo>: a branch <br> no repo tem commits...` (saída por `--sobrescrever`); conflito do `ws teste`; `a <br> no repo não é a da feature`; `a <br>-teste mudou no repo`; `a <br> foi enviada, mas a <br>-teste conflitou`; `nenhum conflito em andamento`; repo sem ramo de teste. A entrada "Conflito no sync" não muda (é do `main`).
- [ ] **Step 4: Camadas 3 e 4:** `ws teste` e `ws push --sobrescrever` nas listas de comandos; a skill nova na lista de skills; o cache `.ws/teste/` no que a camada 4 diz sobre estado local.
- [ ] **Step 5: ADR 0001, adendo 7:** branch `-teste` por repo, cache blobless em `.ws/teste/`, guarda e `--sobrescrever`.
- [ ] **Step 6: Rodar** a suíte inteira (inclui `test_docs_referencias.sh` e `test_nomes_antigos.sh`) → tudo ok.
- [ ] **Step 7: Commit** `docs: branch de teste por repo e ajustes de PR na feature`.

### Task 9: Validação real, revisão e entrega

**Files:**
- Create (neste repo de discovery): `docs/discovery/branch-teste-validacao.md`
- Modify (neste repo de discovery): `docs/discovery/estado-da-sessao.md`

- [ ] **Step 1: Ponta a ponta no Azure** com o repo fixture `industria-logistica.wms.harness-test-dummy` (SP8), numa cópia descartável do workspace com a `harness/branch-teste`: os casos da seção 4 da spec, um por um, registrando comando, saída e veredito. Antes do primeiro push de uma `-teste` num repo real que não seja o fixture, peça confirmação ao usuário (nesta validação, só o fixture é necessário). Ao fim, abandone os PRs de teste e apague as branches pelo SHA.
- [ ] **Step 2: Revisão final** da `harness/branch-teste` (subagente, modelo mais capaz) contra a spec e este plano; corrija os Critical/Important com teste.
- [ ] **Step 3: Push** da `harness/branch-teste` e PR para o `main` do workspace (com a confirmação do usuário; o `main` exige PR).
- [ ] **Step 4: Atualizar** `docs/discovery/estado-da-sessao.md` e fazer commit neste repo.
