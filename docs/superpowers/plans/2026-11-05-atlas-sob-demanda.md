# Atlas sob demanda: plano de implementação

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** O Atlas deixa de mapear no start; a página lida é conferida contra o diff dos arquivos que ela cita; o converge revisa só as afirmações tocadas (Sonnet, prompt enxuto); a execução manual do time do harness revisa o que entrou pelo `ws/sync` e preenche lacunas.

**Architecture:** Cada repo ganha `_discovery/afirmacoes.csv` (afirmação → docs → arquivos, legível por máquina), gerado uma vez a partir do `traceability-index.md` por um script de migração. Um módulo Python novo (`tools/atlas/afirmacoes.py`) responde "quais afirmações deste doc podem ter envelhecido" e "quais afirmações estes arquivos alterados tocam", usando a `arvore` do `atlas.estado` como "revisado até aqui". O `plano.py` perde o gatilho `start` e os motivos `contrato`, `intervalo` e `volume`; o converge e o manual passam a planejar por afirmações. Skills, hooks e docs mudam para o fluxo novo.

**Tech Stack:** bash (Git Bash no Windows), Python 3 só com a biblioteca padrão, git; testes em `tools/ws/tests` (`bash tools/ws/tests/run.sh <arquivos>`; `WS_TEST=<nome>` roda um teste).

**Spec:** `C:\src\00-harness_big_brown_field\docs\superpowers\specs\2026-11-05-atlas-sob-demanda-design.md`

## Global Constraints

- Implementação no workspace, numa worktree nova: `git -C /c/src/wms-workspace worktree add /c/src/wms-workspace-atlas -b harness/atlas-sob-demanda origin/main`. Não tocar no checkout `C:\src\wms-workspace` (tem trabalho do usuário).
- Commits e PR do workspace **sem** atribuição ao Claude; o `main` do workspace exige PR; push e PR só com confirmação do usuário.
- Respostas e textos de skill, mensagens do `ws` e docs em português do Brasil.
- Fonte da extensão `ws` em `tools/speckit/ws/commands/`; as cópias em `.specify/extensions/ws/` e `.claude/skills/speckit-ws-*` são regeneradas com `tools/ws/ws speckit`, nunca editadas à mão. As skills `atlas-atualizar` e `atlas-consultar` vivem só em `.claude/skills/`.
- Docs do harness (`docs/harness/1..4`), `AGENTS.md` e `docs_referencias.py` verdes no mesmo PR.
- Os repos de `repos/` são só leitura para o Atlas.
- Tokens nas estimativas são **tokens processados** (entrada + cache + saída), a medida do diagnóstico do 65594.
- No Windows: `MSYS_NO_PATHCONV=1` para `git show <ref>:<caminho>`; scripts Python escritos em arquivo, sem heredoc com barras invertidas.

## Formatos (decididos aqui; todas as tarefas usam)

- `docs/atlas/<repo>/_discovery/afirmacoes.csv`, cabeçalho `id,docs,arquivos`, uma linha por afirmação:
  - `docs`: caminhos relativos a `docs/atlas/<repo>/`, separados por `;` (ex.: `areas/checkout/rules-checkout.md;tech/integrations.md`);
  - `arquivos`: `<repo>:<caminho relativo ao repo>` separados por `;`; um item que a migração não resolveu leva `?` na frente (`?r1:CheckoutValidacaoService.cs`) e deixa a afirmação sempre suspeita;
  - evidência fora dos repos (`extract/`, `docs/atlas/banco/`) não entra.
- `docs/atlas/<repo>/_discovery/conferidas.csv`, cabeçalho `id,resultado,nota`, `resultado` ∈ `vale|nao-vale|mudou`. Existe só na branch da entrega; o converge consome e apaga.
- `docs/atlas/<repo>/_discovery/lacunas.csv`, cabeçalho `tipo,alvo,arquivos,data,origem`:
  - `tipo=area`: `alvo` é a área (ex.: `src/Services/AWX.Faturamento`), `arquivos` os arquivos que a entrega tocou (`;`);
  - `tipo=afirmacoes`: `alvo` são ids (`C-8;C-142`) que ficaram por revisar (subagente que parou);
  - `origem`: a branch.
- `.gitignore` ganha `!docs/atlas/*/_discovery/afirmacoes.csv`, `!docs/atlas/*/_discovery/conferidas.csv` e `!docs/atlas/*/_discovery/lacunas.csv`.
- CSV pelo módulo `csv` (RFC 4180), UTF-8, `newline=''` na leitura e `\n` na escrita.

## Review Focus

1. Arquivo citado apagado ou renomeado desde a `arvore`: a afirmação aparece como suspeita, sem erro (teste em Task 1).
2. Item `?` não resolvido: a afirmação é suspeita em toda conferência, mesmo sem mudança (Task 1).
3. `arvore` gravada ausente no clone e commit do split impossível de baixar: o `confere` avisa e trata todas as afirmações do doc como suspeitas, sem parar o agente (Task 3).
4. Repo sem `afirmacoes.csv`: o `confere` diz que o repo não tem rastreabilidade e que o código é a fonte; o converge transforma os arquivos alterados desse repo em lacuna `area`, sem subagente (Tasks 3 e 4).
5. Mudança ainda não commitada na branch conta no `confere` e no converge (Tasks 1 e 4).

---

### Task 1: Módulo `afirmacoes.py` e o formato

**Files:**
- Create: `tools/atlas/afirmacoes.py`
- Modify: `.gitignore` (as três exceções), `tools/ws/tests/test_harness.sh` (teste do `.gitignore` exige as três linhas)
- Modify: `.gitattributes` (cria se não existir): `docs/atlas/*/_discovery/lacunas.csv merge=union`, para dois converges que acrescentam lacunas no mesmo repo não conflitarem; o `afirmacoes.csv` conflita como texto normal, e quem mergeia resolve
- Test: `tools/ws/tests/test_atlas_afirmacoes.sh` (novo, usa `atlas_lib.sh`)

**Interfaces:**
- Consumes: de `tools/atlas/plano.py` (importado com `sys.path` na pasta do script): `git`, `le_estado`, `existe`, `arvore_do_split`, `arvore_da_arvore_de_trabalho`, `manifesto`.
- Produces:
  - `carrega(repo: str) -> list[dict] | None` — `None` sem arquivo; cada dict `{'id': str, 'docs': list[str], 'arquivos': list[tuple[str, str, bool]]}` (repo, caminho, resolvido).
  - `arvore_revisada(repo: str) -> tuple[str, str]` — (tree, '') ou ('', motivo), pela `arvore` do estado e, na falta, `arvore_do_split`.
  - `mudados(repo: str) -> set[str] | None` — caminhos relativos ao repo que diferem entre `arvore_revisada` e a árvore de trabalho do prefixo (inclui não commitado); `None` se não há base.
  - `suspeitas(repo: str, doc: str) -> list[tuple[str, list[str]]]` — (id, arquivos mudados ou `['?']`) das afirmações que usam `doc`; arquivos de outro repo comparados com o `mudados` daquele repo.
  - `tocadas(alterados: dict[str, set[str]]) -> dict[str, list[str]]` — para arquivos alterados por repo, as afirmações de **qualquer** repo que os citam, agrupadas pelo repo dono da afirmação.
  - CLI: `python tools/atlas/afirmacoes.py confere <repo> <doc>` (usada pela Task 3).

- [ ] **Step 1: Testes que falham** em `test_atlas_afirmacoes.sh`, sobre `fx_atlas` com um `afirmacoes.csv` escrito pelo teste em `docs/atlas/r1/_discovery/`:
  - `test_afirmacoes_doc_em_dia`: nada mudou → `confere r1 tech/x.md` imprime `em dia`.
  - `test_afirmacoes_arquivo_mudado_vira_suspeita`: `C-1` cita `r1:src/A.cs`; commit em `repos/r1/src/A.cs` na branch → saída contém `C-1` e `src/A.cs`; `C-2` (outro arquivo) ausente.
  - `test_afirmacoes_arquivo_apagado_vira_suspeita`: `git rm repos/r1/src/A.cs` → `C-1` suspeita, código de saída 0.
  - `test_afirmacoes_nao_resolvido_sempre_suspeita`: `C-3` com `?r1:Solto.cs` → suspeita sem mudança alguma.
  - `test_afirmacoes_nao_commitado_conta`: `echo x > repos/r1/src/A.cs` sem commit → `C-1` suspeita.
  - `test_afirmacoes_evidencia_em_outro_repo`: `C-4` de r1 cita `r2:src/B.cs`; mudança em r2 → `C-4` suspeita no `confere r1`.
  - `test_afirmacoes_tocadas_agrupa_pelo_dono`: `python afirmacoes.py tocadas` com `r2:src/B.cs` (via um modo CLI de teste `tocadas <repo>:<arquivo>...` que imprime `repo id` por linha) → `r1 C-4`.
- [ ] **Step 2:** `bash tools/ws/tests/run.sh tools/ws/tests/test_atlas_afirmacoes.sh` → falham (módulo inexistente).
- [ ] **Step 3: Implementar** `afirmacoes.py` com as interfaces acima e a CLI `confere` e `tocadas`. Saída do `confere`: `em dia: <doc>` ou uma linha por afirmação `C-n: arq1, arq2`; no topo, aviso de base ausente quando for o caso (Task 3 testa).
- [ ] **Step 4:** rodar → passam. Rodar também `test_harness.sh` (gitignore).
- [ ] **Step 5: Commit** `atlas: afirmacoes.csv e conferência por afirmação`.

### Task 2: Migração do `traceability-index.md` para `afirmacoes.csv`

**Files:**
- Create: `tools/atlas/migra-afirmacoes.py`
- Create (gerados, Step 6): `docs/atlas/<repo>/_discovery/afirmacoes.csv` dos 19 repos; `docs/atlas/<repo>/_discovery/lacunas.csv` onde o `project-readme.md` tinha o aviso de pendência
- Modify (gerado, Step 6): `docs/atlas/<repo>/project-readme.md` sem a linha `> **Atlas:** mapeamento pendente`
- Test: `tools/ws/tests/test_atlas_migra.sh` (novo)

**Interfaces:**
- Consumes: formato da Task 1.
- Produces: `python tools/atlas/migra-afirmacoes.py [--repos a,b]` grava os CSVs e imprime, por repo, `repo: N afirmações, M arquivos não resolvidos, K docs por curinga`.

Regras da migração (a tabela é a mesma nos 19 repos: `| Claim ID | Claim (short) | Evidence (...) | Confidence | Used in doc |`):
- **Arquivos:** os trechos entre crases da coluna Evidence; tira `:linhas`; expande os prefixos da legenda do cabeçalho (padrão `` `X/` = `caminho` ``, inclusive os que apontam para outro repo, como `` `picking.backend/…` = `repos/industria-logistica.wms.picking.backend` `` e `LW/`); `{a,b}` e `*` expandem contra `git ls-files` do repo; nome solto resolve se for único no repo pelo nome do arquivo; o resto vira `?`. Trechos que não parecem caminho (sem `/` nem extensão) são ignorados; `extract/` e `docs/atlas/` saem.
- **Docs:** união de (a) a coluna Used in doc — `README` → `project-readme.md`, curinga (`tech/*`) expande para os docs que casam, pasta (`areas/checkout`) para os docs dela, `(histórico)` e `register ...` não contam; nome que não resolve vale todos os docs do repo — e (b) os docs do repo que citam o id no texto (`\bC-\d+\b`).
- **Pendência antiga:** a linha `> **Atlas:** mapeamento pendente desde AAAA-MM-DD nas áreas: a, b.` vira uma linha `area` por área em `lacunas.csv` (`origem=migracao`) e sai do `project-readme.md`.

- [ ] **Step 1: Testes que falham** com um `traceability-index.md` de fixture (tabela de 4 linhas, legenda `` `CK/` = `src/Checkout/` ``, nome solto único, nome solto ambíguo, `tech/*`):
  - `test_migra_expande_prefixo_da_legenda` → `C-1` com `r1:src/Checkout/A.cs`.
  - `test_migra_nome_solto_unico_resolve_e_ambiguo_marca` → `r1:src/X/Unico.cs` e `?r1:Dup.cs`.
  - `test_migra_curinga_de_doc_expande` → `tech/*` vira `tech/a.md;tech/b.md`.
  - `test_migra_doc_citado_no_texto_entra` → doc que contém `(C-2)` aparece em `docs` de `C-2`.
  - `test_migra_pendencia_vira_lacuna` → `lacunas.csv` com `area,src/X,...,migracao` e o readme sem o aviso.
- [ ] **Step 2:** rodar → falham.
- [ ] **Step 3: Implementar** `migra-afirmacoes.py`.
- [ ] **Step 4:** rodar → passam.
- [ ] **Step 5: Commit** `atlas: migração do índice de rastreabilidade`.
- [ ] **Step 6: Rodar no Atlas real** (`python tools/atlas/migra-afirmacoes.py`), mostrar ao usuário a tabela por repo (afirmações, não resolvidos, curingas). Se algum repo passar de 20% de não resolvidos, abrir 10 exemplos e ajustar as regras (voltar ao Step 1 com um teste do caso) antes de seguir. Commit `atlas: afirmacoes.csv dos repos` (só `docs/atlas`).

### Task 3: Comandos `ws atlas confere`, `registra` e `lacuna`

**Files:**
- Modify: `tools/ws/lib/atlas.sh` (dispatcher `ws_atlas` e três funções novas)
- Modify: `tools/atlas/afirmacoes.py` (subcomandos `registra` e `lacuna`)
- Test: `tools/ws/tests/test_atlas_afirmacoes.sh`

**Interfaces:**
- Consumes: Task 1.
- Produces:
  - `ws atlas confere <repo> <doc>` → a saída da CLI `confere`; sem `afirmacoes.csv`: `ws: <repo> não tem rastreabilidade por afirmação; use o código como fonte`.
  - `ws atlas registra <repo> <C-id> <vale|nao-vale|mudou> [nota]` → acrescenta ou substitui a linha do id em `conferidas.csv`.
  - `ws atlas lacuna <repo> <area> <arquivo>...` → acrescenta a linha `area` em `lacunas.csv` com a data de hoje e `origem` = branch atual; não duplica `(area, origem)`.

- [ ] **Step 1: Testes que falham:**
  - `test_confere_sem_rastreabilidade_avisa`.
  - `test_confere_base_ausente_avisa_e_marca_tudo`: `atlas.estado` com `arvore` e `split` inexistentes e sem origin alcançável → aviso `não consegui achar o commit revisado de r1` e todas as afirmações do doc listadas; código 0.
  - `test_registra_grava_e_substitui`: duas chamadas para `C-1` → uma linha, a última.
  - `test_registra_recusa_resultado_invalido` → `assert_fail`.
  - `test_lacuna_nao_duplica`.
- [ ] **Step 2:** rodar → falham.
- [ ] **Step 3: Implementar.** Mensagem de uso: `uso: ws atlas <plano|incorpora|concluir|mapas|confere|registra|lacuna> [args]`.
- [ ] **Step 4:** rodar → passam.
- [ ] **Step 5: Commit** `ws atlas: confere, registra e lacuna`.

### Task 4: `plano.py` sem start e planejando por afirmações

**Files:**
- Modify: `tools/atlas/plano.py`, `tools/atlas/relevancia.ini`
- Test: `tools/ws/tests/test_atlas_plano.sh`

**Interfaces:**
- Consumes: Task 1 (`tocadas`, `carrega`, `arvore_revisada`); `conferidas.csv` e `lacunas.csv`.
- Produces: `.git/atlas-plano.json` com, por repo, `acao` ∈ `revisar|avancar|nada|do-zero|adiar`, `motivo`, `afirmacoes` (ids), `conferidas` (ids), `lacunas_novas` (áreas), `lacunas_abertas` (linhas de `lacunas.csv`, só no manual), `manter_arvore` (bool, só no converge), `arvore_atual`, `split_atual`, `tokens_estimados`; e no stdout só a tabela `repo | ação | afirmações | lacunas | tokens` mais a linha `plano completo em <caminho>`.

Regras:
- `--gatilho` aceita só `converge` e `manual`; `start` sai com `ws: erro: o gatilho start não existe mais; o Atlas não é atualizado no início (veja docs/harness/3-alem-do-basico.md)`.
- **converge:** arquivos alterados = diff de `merge-base(--base, HEAD)` até a árvore de trabalho, por prefixo, menos `[ignorar]` (como hoje). `afirmacoes` = `tocadas` desses arquivos (inclui de outros repos) ∪ ids de `conferidas.csv`; `lacunas_novas` = áreas (dois primeiros níveis) dos arquivos alterados que nenhuma afirmação cita, quando o repo não tem docs para elas. `revisar` se há afirmação; `avancar` se só há arquivos; `nada` sem arquivos. Repo sem `afirmacoes.csv`: `avancar`, com todas as áreas alteradas em `lacunas_novas`. `manter_arvore` = a tree do prefixo no merge-base é diferente de `arvore_revisada(repo)`.
- **manual:** base por repo = `arvore_revisada`; arquivos = diff até a árvore atual (como hoje, `adiar` em `fetch-falhou`, `do-zero` sem estado ou com `--do-zero`); `afirmacoes` = `tocadas`; `revisar` se há afirmação, senão `avancar`; `lacunas_abertas` = `lacunas.csv` do repo.
- Saem: `[contrato]`, `intervalo_dias`, `limiar_arquivos`, `limite_minimo`, `--repos`, `tokens_por_arquivo`, `tokens_minimo_repo`, `linhas_do_diff`. Ficam `[ignorar]`, `pr_max_repos`, `pr_max_dias`.
- `relevancia.ini` `[politica]` ganha (valores iniciais, recalibrados na Task 9): `tokens_revisao_base = 1500000`, `tokens_por_afirmacao = 150000`, `tokens_area = 20000000`, `tokens_do_zero = 25000000`, `teto_chamadas_revisao = 40`.
- Estimativa: `revisar` = base + n × por_afirmacao; cada lacuna aberta = `tokens_area`; `do-zero` = `tokens_do_zero`.

- [ ] **Step 1: Testes.** Apagar os de start, contrato, intervalo, volume e limite (`test_plano_mudanca_irrelevante_so_avanca` passa a usar `--gatilho manual`). Novos, falhando:
  - `test_plano_start_nao_existe_mais` → `assert_fail` com a mensagem acima.
  - `test_plano_converge_sem_afirmacao_tocada_nao_revisa` → `avancar`, `afirmacoes` vazio.
  - `test_plano_converge_revisa_so_as_afirmacoes_tocadas` → `revisar`, `afirmacoes == ['C-1']`.
  - `test_plano_converge_inclui_as_conferidas`.
  - `test_plano_converge_afirmacao_de_outro_repo` → mudança em r2 põe `C-4` em r1 como `revisar`.
  - `test_plano_converge_ignora_o_que_veio_da_ws_sync`: commit externo em r1 trazido por `ws sync` + merge na branch, e a entrega mexe em r2 → r1 `nada`.
  - `test_plano_converge_mantem_arvore_quando_a_base_nao_foi_revisada`: estado com `arvore` antiga, branch a partir de `ws/sync` à frente → `manter_arvore: true`.
  - `test_plano_converge_repo_sem_afirmacoes_vira_lacuna`.
  - `test_plano_manual_lista_lacunas_abertas_com_custo` → `tokens_estimados` inclui `20000000`.
  - `test_plano_imprime_so_a_tabela` → `$OUT` não contém `"repos":` e contém `plano completo em`.
- [ ] **Step 2:** rodar → falham.
- [ ] **Step 3: Implementar.**
- [ ] **Step 4:** `run.sh test_atlas_plano.sh test_atlas_afirmacoes.sh` → passam.
- [ ] **Step 5: Commit** `atlas: plano por afirmações, sem start`.

### Task 5: `concluir` e `grava-estado` no fluxo novo

**Files:**
- Modify: `tools/ws/lib/atlas.sh` (`ws_atlas_concluir`), `tools/atlas/plano.py` (`grava_estado`, remove `marca_pendencia` e `AVISO`)
- Test: `tools/ws/tests/test_atlas_concluir.sh`

**Interfaces:**
- Consumes: plano da Task 4.
- Produces: `ws atlas concluir --gatilho converge|manual [--falhas a,b]`.

Regras:
- converge: repo `revisar`/`avancar` sem falha → `arvore` = `arvore_atual` só se `manter_arvore` for falso; `data` = hoje se revisado. Repo com falha → `arvore` não avança e as `afirmacoes` dele viram uma linha `afirmacoes` em `lacunas.csv`. `lacunas_novas` de todo repo do plano viram linhas `area`. `conferidas.csv` dos repos do plano é apagado. Tudo no mesmo commit só de `docs/atlas`, como hoje.
- manual: como hoje (publica na `atlas/atualizacao` sobre a base remota); lacunas preenchidas (lista `--lacunas a,b` de áreas, passada pela skill) saem do `lacunas.csv`.
- Sai o aviso no `project-readme.md`; sai o gatilho `start` (`die` com a mesma mensagem da Task 4).

- [ ] **Step 1: Testes.** Ajustar os que usam `--gatilho start` para `manual` (a publicação continua igual); apagar `test_concluir_marca_e_tira_a_pendencia_no_readme`. Novos, falhando:
  - `test_concluir_converge_mantem_arvore_quando_pedido`.
  - `test_concluir_converge_falha_vira_lacuna_de_afirmacoes` → `lacunas.csv` com `afirmacoes,C-1,...` e estado sem avanço.
  - `test_concluir_converge_grava_lacunas_novas`.
  - `test_concluir_converge_apaga_conferidas` → `conferidas.csv` fora do `HEAD`.
  - `test_concluir_manual_tira_as_lacunas_preenchidas`.
  - `test_concluir_start_nao_existe_mais`.
- [ ] **Step 2:** rodar → falham.
- [ ] **Step 3: Implementar.**
- [ ] **Step 4:** `run.sh test_atlas_concluir.sh test_atlas_plano.sh` → passam.
- [ ] **Step 5: Commit** `ws atlas concluir: lacunas, conferidas e árvore revisada`.

### Task 6: `ws atlas mapas` sem plano, disparado pelo `ws start`

**Files:**
- Modify: `tools/ws/lib/atlas.sh` (`ws_atlas_mapas`), `tools/ws/lib/start.sh` (dispara os mapas em segundo plano)
- Test: `tools/ws/tests/test_atlas_mapas.sh`, `tools/ws/tests/test_start.sh`

**Interfaces:**
- Produces: `ws atlas mapas` sem argumentos reindexa os repos cujo split atual (`ws_current_split`) difere do gravado em `.ws/mapas/<repo>.split` (local, fora do git); grava o split de cada repo reindexado com sucesso. `--repos` e `--todos` como hoje (também gravam).
- Produces: o `ws start`, ao criar uma branch nova, dispara `ws atlas mapas` desacoplado (`nohup ... &`, saída em `.ws/mapas.log`) e segue sem esperar; `WS_MAPAS=0` desliga (os testes da suíte usam). Nenhuma skill chama os mapas: o agente não gasta tokens com eles (decisão do usuário, 2026-11-05).

- [ ] **Step 1: Testes que falham:** `test_mapas_sem_plano_reindexa_so_o_que_mudou` (com `WS_CBM` falso que registra chamadas: primeira rodada indexa r1 e r2, segunda nenhum, depois de `upstream_commit r1` + `ws sync` só r1); `test_mapas_falha_nao_grava_o_split`; `test_start_dispara_os_mapas_sem_esperar` (com `WS_CBM` falso que dorme 5 s e grava um marcador: o `ws start` volta antes do marcador, que aparece depois; `.ws/mapas.log` existe); `test_start_sem_mapas_com_ws_mapas_0`. Ajustar os testes que dependiam de `plano.py lista --mudou`.
- [ ] **Step 2:** rodar → falham.
- [ ] **Step 3: Implementar;** remover `lista --mudou` do `plano.py` se nada mais usar.
- [ ] **Step 4:** rodar `test_atlas_mapas.sh test_atlas_plano.sh` → passam.
- [ ] **Step 5: Commit** `ws atlas mapas: sem depender do plano`.

### Task 7: Prompts de revisão e de mapeamento

**Files:**
- Create: `tools/atlas/prompt-revisao.md`
- Modify: `tools/atlas/prompt-mapeamento.md`
- Test: `tools/ws/tests/test_harness.sh`

`prompt-revisao.md` (subagente por repo; usado pelo converge com Sonnet e pelo manual com o modelo da sessão). Placeholders `<REPO>`, `<AFIRMACOES>` (ids), `<CONFERIDAS>` (linhas do `conferidas.csv`), `<ARQUIVOS>`, `<LACUNAS_NOVAS>`, `<TETO>`. Instruções, sem mandar ler a skill `codebase-discovery`:
1. Ler só as linhas das afirmações listadas no `traceability-index.md` e no `afirmacoes.csv`, os trechos dos docs que as citam e os arquivos alterados.
2. Para cada afirmação: manter, corrigir (texto, evidência, linhas) ou marcar `[outdated]`; corrigir os trechos dos docs que a usam; atualizar a linha do `afirmacoes.csv`.
3. Comportamento novo da entrega: afirmação nova (`C-<próximo>`) no índice e no CSV, citada no doc certo; área sem doc → página mínima `areas/<area>/rules-<area>.md` só com o que a entrega mexeu.
4. `edges.csv` e `tech/integrations.md`: só as linhas afetadas.
5. Cabeçalho do `traceability-index.md`: só o estado atual (`Last updated` e uma linha de commit); apagar o histórico de incrementais se existir.
6. Segredos: só o local, nunca o valor.
7. Teto: ao passar de `<TETO>` chamadas, parar e relatar `PARCIAL` com os ids não revistos.
8. Relatório (até 120 palavras): ids revistos, novos, `[outdated]`, docs tocados, e `FALHOU` ou `PARCIAL` com motivo e ids.

`prompt-mapeamento.md` (execuções completas: lacunas e `do-zero`): troca o bloco "Aprofunde onde mexer" por "Lacunas: documente inteiras as áreas `<AREAS>` (da lista de lacunas)"; acrescenta às saídas obrigatórias o `afirmacoes.csv` no formato do plano e a regra do cabeçalho do índice.

- [ ] **Step 1: Testes que falham** em `test_harness.sh`: `test_prompt_revisao_nao_le_a_skill_inteira` (não contém `codebase-discovery/SKILL.md`; contém `<TETO>`, `PARCIAL`, `afirmacoes.csv`); `test_prompt_mapeamento_sem_aprofundar` (não contém `Aprofunde onde mexer`; contém `afirmacoes.csv`).
- [ ] **Step 2:** rodar → falham. **Step 3:** escrever os prompts. **Step 4:** rodar → passam.
- [ ] **Step 5: Commit** `atlas: prompt de revisão e mapeamento por lacunas`.

### Task 8: Skills, hooks, `ws start` e docs

**Files:**
- Modify: `.claude/skills/atlas-atualizar/SKILL.md`, `.claude/skills/atlas-consultar/SKILL.md`
- Modify: `tools/speckit/ws/commands/speckit.ws.{bug-start,feature,refactor-start,bug-submit,refactor-submit,converge}.md`; depois `tools/ws/ws speckit` para regenerar as cópias
- Modify: `tools/ws/lib/start.sh:94` (mensagem do `ws/sync` à frente do `main`)
- Modify: `AGENTS.md`, `docs/harness/1-*.md` (se citar o Atlas no start), `2-quando-da-errado.md`, `3-alem-do-basico.md`, `4-manter.md`
- Modify: `.claude/settings.json` (`Bash(tools/ws/ws atlas confere:*)` na allow list) e o teste correspondente em `test_harness.sh`
- Test: `test_harness.sh`, `test_speckit_install.sh`, `test_speckit_bug.sh`, `test_speckit_refactor.sh`, `test_start.sh`, `test_docs_referencias.sh`

Conteúdo:
- **atlas-atualizar:** gatilhos `converge` e `manual` (sem `start`, sem `--repos`).
  - converge: plano → para cada `revisar`, um subagente com `model: "sonnet"` e o `prompt-revisao.md` (teto do `relevancia.ini`), até 4 em paralelo; sem `revisar`, nenhum subagente; subagente que parar por limite de uso, não terminar ou relatar `FALHOU`/`PARCIAL` → `--falhas`, sem retomar e sem bloquear o envio; concluir; não pede confirmação.
  - manual (só o time do harness): `ws start atlas/manual-<data>` + `ws atlas incorpora`; plano; revisa **todas** as afirmações de `revisar` com o `prompt-revisao.md` no modelo da sessão; mostra as lacunas abertas com o custo e pergunta quais preencher; preenche com o `prompt-mapeamento.md` (`<AREAS>` = lacunas escolhidas); concluir `--gatilho manual --lacunas <áreas>`; abre o PR da `atlas/atualizacao`, que leva também a `ws/sync`; `ws atlas mapas`.
- **atlas-consultar:** antes de confiar num doc de `docs/atlas/<repo>/`, rodar `tools/ws/ws atlas confere <repo> <doc>`; suspeita → conferir no código só o que precisa e registrar com `ws atlas registra`; código sem página → `ws atlas lacuna`. O aviso de "mapeamento pendente" sai.
- **bug-start, refactor-start, feature:** sai o passo do Atlas (e o "repos prováveis" da feature); nada sobre mapas (o `ws start` dispara sozinho, Task 6).
- **bug-submit, refactor-submit, converge:** texto do passo do Atlas: revisa só as afirmações tocadas e as conferidas; sem nenhuma, nada roda.
- **start.sh:** a mensagem passa a ser `a ws/sync tem <n> commit(s) que não estão no main; o time do harness leva ao main com o /atlas-atualizar manual (PR da atlas/atualizacao)`.
- **Docs:** camada 3 (receita do Atlas: sob demanda, conferência, lacunas, manual), camada 4 ("PR da `ws/sync`" vira a execução manual; `relevancia.ini` novo; calibração), camada 2 (sintomas: "o `confere` marcou afirmações", "subagente do converge parou", "gatilho start não existe mais"; remove "O `/speckit-specify` demora no Atlas" e ajusta o teste que a exige), `AGENTS.md` (regra de consulta com `confere`).

- [ ] **Step 1: Testes que falham:** `test_hooks_de_inicio_nao_atualizam_o_atlas` (as três fontes de start sem `atlas-atualizar` e sem `ws atlas mapas`); `test_atlas_consultar_manda_conferir` (contém `ws atlas confere` e `ws atlas registra`); `test_atlas_atualizar_converge_usa_sonnet_e_nao_bloqueia` (contém `sonnet`, `prompt-revisao.md`, `--falhas`, sem `--gatilho start`); ajustar `test_speckit_install.sh:56` (a feature não contém mais `atlas-atualizar`) e o teste de `start.sh` da mensagem do `ws/sync`.
- [ ] **Step 2:** rodar → falham.
- [ ] **Step 3: Editar** fontes, skills, `start.sh`, settings e docs; `tools/ws/ws speckit`.
- [ ] **Step 4:** suíte inteira `bash tools/ws/tests/run.sh` → tudo verde, exceto `test_harness_do_awx_igual_ao_do_repo` se ainda falhar no `main` (registrar).
- [ ] **Step 5: Commit** `harness: fluxo do Atlas sob demanda nas skills e docs`.

### Task 9: Validação de ponta a ponta e calibração (com o usuário)

**Files:**
- Modify: `tools/atlas/relevancia.ini` (valores calibrados)
- Create: `C:\src\00-harness_big_brown_field\docs\discovery\atlas-sob-demanda-validacao.md` (repo do discovery, commit com `Co-Authored-By`)

- [ ] **Step 1:** Na worktree, um bug de teste num repo real (o mesmo tipo do 65594, no `servidor.backend`, branch descartável): start sem mapeamento (cronometrar até o agente começar o diagnóstico); `confere` numa página em dia e numa com suspeita forçada; `registra`.
- [ ] **Step 2:** Converge com zero afirmações tocadas (mudança num arquivo que nenhuma afirmação cita) → nenhum subagente.
- [ ] **Step 3:** Converge com 2 a 5 afirmações tocadas → um subagente Sonnet; medir tokens processados e tempo pelas transcrições (mesmo método do diagnóstico do 65594).
- [ ] **Step 4:** Execução manual sobre um `ws/sync` com mudança externa num repo: as afirmações tocadas são revistas, uma lacuna é escolhida e preenchida, a `atlas/atualizacao` é publicada sobre a `ws/sync`; depois, numa branch nova, o `confere` da página revista diz `em dia`.
- [ ] **Step 5:** Atualizar `tokens_revisao_base`, `tokens_por_afirmacao` e `tokens_area` com os números medidos; registrar tudo no doc de validação, com a comparação contra o 65594 (83% dos tokens no Atlas; 65 M no start; 6,5 M no converge).
- [ ] **Step 6:** Limpar as branches de teste; commit da calibração; mostrar o resultado ao usuário e pedir confirmação para push e PR do workspace (sem atribuição).
