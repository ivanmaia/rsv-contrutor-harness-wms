# SP8: Padronização dos comandos — plano de implementação

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Feature, bug e refactor terminam com os mesmos comandos (`/ws-commit-push`, `/ws-pr-homolog`, `/ws-pr-main`), e os comandos e skills que o dev vê na lista do `/` ficam em inglês, sem mudar o comportamento nem o CLI.

**Architecture:** É uma renomeação guiada por um teste de nomes proibidos que cresce a cada tarefa. Os comandos que o dev digita no fim do fluxo saem da extensão `ws` e viram skills comuns em `.claude/skills/ws-*`. Os hooks continuam na extensão; só os quatro com nome em português mudam, e os hooks de fim passam a seguir essas skills.

**Tech Stack:** bash (Git for Windows), Python 3 (stdlib), Spec Kit 1.2.0 (extensões `ws` e `refactor`, regeneradas por `tools/ws/ws speckit` com `uvx`), Claude Code skills.

**Spec:** `docs/superpowers/specs/2026-10-22-sp8-nomes-e-comandos-design.md` (repo de discovery), seções 4 e 8. O código fica em `C:\src\wms-workspace`.

## Global Constraints

- **Base:** um worktree novo `C:\src\wms-workspace-sp8`, a partir do `origin/main` mais novo, na branch `harness/sp8-nomes`. Não mexa em `C:\src\wms-workspace`.
- **Escopo:**
  - as skills `/ws-commit-push`, `/ws-pr-homolog`, `/ws-pr-main` e `/ws-pr-review`;
  - a extensão de refactor (`rollout`, `validate`, `retire-legacy`, `remove-flag`) e os eventos dela;
  - os 4 hooks: `bug-sem-correcao` vira `bug-no-fix`, `bug-enviar` vira `bug-submit`, `refactor-registro` vira `refactor-record` e `refactor-enviar` vira `refactor-submit`;
  - os sufixos de branch novos: `-rollout`, `-validate`, `-remove-flag`, `-coexistence` e `-legacy`;
  - as pastas e arquivos novos: `refactors/slices.md`, `refactors/slices/<código>/{rollout-plan,validation,retire-legacy,remove-flag}.md` e `refactors/decouplings/`.
- **Não muda:**
  - o CLI `tools/ws/ws` inteiro: os subcomandos, as opções, os valores e o `.ws/revisao/`;
  - o Atlas;
  - o Spec Kit oficial e a extensão de bug;
  - os hooks `feature`, `converge`, `bug-start` e `refactor-start`;
  - os nomes de scripts e funções;
  - os modos internos `--subida|--validar|--remover|--rodada` do `ws-refactor-start.sh`;
  - as chaves de JSON e do `workspace.pr.ini`;
  - os documentos, que seguem em português;
  - o que já existe no origin com conteúdo;
  - os marcadores `ws-revisao` e `ws-pr:subtrees`;
  - os prefixos de commit e o prefixo `eap`.
- **Sem apelidos.**
- **Cópias geradas:** depois de mudar fonte em `tools/speckit/`, rode `tools/ws/ws speckit` (árvore limpa: commit antes) e commite as cópias. Nunca edite `.specify/` ou `.claude/skills/speckit-*` à mão.
- **Commits:** em português, sem atribuição ao Claude.
- **Testes:**
  - cada tarefa roda só o `test_nomes_antigos.sh` e os testes do seu grupo (os nomes estão em cada tarefa);
  - a suíte inteira roda uma vez, na Task 6;
  - comando: `bash tools/ws/tests/run.sh <arquivo>`, com `WS_TEST=<nome>` para um teste só;
  - cerca de 11,5 s por teste.
- **Constitution:** troca só os nomes citados. A versão vai de `1.5.0` para `1.5.1`, com a linha na "Governança", e a aprovação é pelo PR.

## Review Focus

1. **Skill citada que não existe:** quebra o fluxo em silêncio. O teste `test_comandos_citam_skills_que_existem` (Task 5) confere que toda skill citada nas fontes de `tools/speckit/` e em `.claude/skills/ws-*` existe em `.claude/skills/`.
2. **Mensagem de commit errada numa branch de fatia:** o teste `test_ws_commit_push_mensagem_por_branch` (Task 5) confere cada linha da tabela do spec, seção 8, item 2.
3. **Branch aberta antes do SP8:** a entrada "Não achei o comando depois de atualizar" da camada 2 (Task 6) cobre o caso.
4. **Skill `ws-*` disparada sem ser chamada:** o teste `test_skills_ws_tem_descricao_com_quando_usar` (Task 5) confere que a descrição diz quando usar e quando não usar.
5. **PR revisado de novo:** o teste `test_marcador_da_revisao_nao_muda` (Task 4) confere que o marcador continua igual.

---

### Task 1: Teste de nomes proibidos

**Files:**
- Create: `tools/ws/tests/test_nomes_antigos.sh` e `tools/ws/tests/nomes-antigos.txt`

**Interfaces:**
- Produces: o arquivo `nomes-antigos.txt`, com uma regex estendida por linha (`#` = comentário) e uma seção `# exceções`, também com uma regex por linha, que filtra as linhas permitidas.
- Produces: o teste `test_sem_nomes_antigos`. Ele roda `git grep -nE` dos padrões e falha listando `arquivo:linha`. A busca cobre:
  - `tools/` (menos `tools/atlas/`, a lista e o próprio teste);
  - `.claude/` e `.specify/`;
  - `AGENTS.md` e `README.md`;
  - `docs/harness/` (menos `historico/`).
- Produces: o teste `test_lista_de_nomes_tem_padroes_validos`, que roda `grep -E` com cada linha e falha se alguma regex for inválida.

- [ ] **Step 1:** Escreva os dois testes com a lista vazia. As exceções iniciais são `ws-revisao:`, `atlas/atualizacao`, `plano-subida-template\.md` e `desacoplamento-template\.md`.
- [ ] **Step 2:** Rode `bash tools/ws/tests/run.sh tools/ws/tests/test_nomes_antigos.sh`. Esperado: 2 ok. Ponha uma regex temporária `ws-revisar`, veja o teste falhar e tire a regex.
- [ ] **Step 3:** Commit `harness: teste de nomes antigos (SP8)`.

---

### Task 2: Sufixos de branch e pastas novas em inglês

**Files:**
- Modify:
  - `tools/speckit/ws/scripts/bash/ws-refactor-start.sh`: só os sufixos. Os modos internos ficam;
  - `tools/ws/lib/fatia.sh`: o caminho de `slices.md`, as branches do `atualiza` e os caminhos `refactors/slices/<código>/`;
  - `tools/ws/pr/entrega.py` (`_ORIGENS`) e `tools/ws/pr/abrir.py` (a regex da subida passa a ser `-rollout(-\d+)?$`);
  - `.gitattributes`, se citar `refactors/fatias.md`;
  - as fontes de `tools/speckit/refactor/commands/*` e `tools/speckit/ws/commands/*` que citam esses caminhos;
  - os testes `test_fatia.sh`, `test_speckit_refactor.sh` e `test_pr.sh`;
  - `docs/harness/1-4` e `AGENTS.md`;
  - `nomes-antigos.txt`.

**Interfaces:**
- **Branches:**
  - os modos `--subida`, `--validar` e `--remover` do `ws-refactor-start.sh` criam `refactor/eap-<código>-rollout[-k]`, `-validate[-k]` e `-remove-flag`;
  - o `ws refactor fatia atualiza <código> convivencia|antigo` cria `-coexistence[-k]` e `-legacy[-k]`.
- **Arquivos:** `refactors/slices.md`, `refactors/slices/<código>/rollout-plan.md`, `validation.md`, `retire-legacy.md` e `remove-flag.md`, e `refactors/decouplings/<nome>.md`. O conteúdo e os cabeçalhos continuam em português.

- [ ] **Step 1:** Acrescente à lista `eap-[^ ]*-(subida|validar|remover|convivencia|antigo)\b`, `refactors/(fatias|desacoplamentos)\b`, `plano-subida\.md`, `validacao\.md`, `desacoplar\.md` e `remover\.md`. Rode `test_nomes_antigos.sh`. Esperado: FALHA.
- [ ] **Step 2:** Mude os caminhos e os sufixos. Nos testes existentes, só mudam os nomes e os caminhos esperados. Acrescente `test_refactor_start_subida_cria_branch_rollout`: o modo `--subida` cria `refactor/eap-1-1-4-rollout`.
- [ ] **Step 3:** Commit, `tools/ws/ws speckit` e commit das cópias.
- [ ] **Step 4:** Rode `test_nomes_antigos.sh`, `test_fatia.sh`, `test_speckit_refactor.sh` e `test_pr.sh`. Esperado: 0 falha.
- [ ] **Step 5:** Commit `harness: branches e pastas novas da fatia em inglês (SP8)`.

---

### Task 3: Extensão de refactor em inglês

**Files:**
- Rename e modify em `tools/speckit/refactor/commands/`:
  - `speckit.refactor.subida.md` para `.rollout.md`;
  - `validar` para `validate`;
  - `desacoplar` para `retire-legacy`;
  - `remover` para `remove-flag`.
- Modify:
  - `tools/speckit/refactor/extension.yml` (nomes e bump de minor) e `tools/speckit/refactor/hooks.md` (eventos);
  - `tools/speckit/ws/extension.yml` (os eventos em que os hooks se registram);
  - as fontes que citam esses comandos;
  - os testes `test_speckit_refactor.sh`, `test_speckit_install.sh` e `test_fatia.sh`;
  - `docs/harness/1-4`, `AGENTS.md` e a constitution (patch 1.5.1);
  - `nomes-antigos.txt`.

**Interfaces:**
- Produces: os comandos `/speckit-refactor-rollout`, `-validate`, `-retire-legacy` e `-remove-flag`, e os eventos `before_`/`after_refactor_rollout`, `_validate`, `_retire_legacy` e `_remove_flag`.

- [ ] **Step 1:** Acrescente à lista `speckit[-.]refactor[-.](subida|validar|desacoplar|remover)\b` e `(before|after)_refactor_(subida|validar|desacoplar|remover)\b`. Rode o teste. Esperado: FALHA.
- [ ] **Step 2:** Faça as mudanças. Acrescente `test_speckit_registra_os_eventos_de_refactor_em_ingles`: depois do `ws speckit`, o `.specify/extensions.yml` tem os 8 eventos novos e nenhum antigo.
- [ ] **Step 3:** Commit, `tools/ws/ws speckit` e commit das cópias.
- [ ] **Step 4:** Rode `test_nomes_antigos.sh`, `test_speckit_refactor.sh`, `test_speckit_install.sh` e `test_fatia.sh`. Esperado: 0 falha.
- [ ] **Step 5:** Commit `harness: extensão de refactor em inglês (SP8)`.

---

### Task 4: `/ws-pr-review`

**Files:**
- Move: `.claude/skills/ws-revisar/` para `.claude/skills/ws-pr-review/` (com o `name:` novo).
- Modify: as fontes e os documentos que citam `/ws-revisar`, `tools/ws/pr/revisao.py` (só mensagens que citem a skill), os testes `test_harness.sh` e `test_pr_revisao.sh`, e `nomes-antigos.txt`.

- [ ] **Step 1:** Acrescente à lista `\bws-revisar\b`. Rode o teste. Esperado: FALHA.
- [ ] **Step 2:** Faça as mudanças. Acrescente `test_marcador_da_revisao_nao_muda`: `revisao.py` contém `ws-revisao:`.
- [ ] **Step 3:** Rode `test_nomes_antigos.sh`, `test_harness.sh` e `test_pr_revisao.sh`. Esperado: 0 falha.
- [ ] **Step 4:** Commit `harness: skill ws-pr-review (SP8)`.

---

### Task 5: Fim de fluxo único e os 4 hooks

**Files:**
- Create:
  - `.claude/skills/ws-commit-push/SKILL.md`, a partir de `speckit.ws.commit-push.md`, com a tabela de mensagens do spec (seção 8, item 2) e os avisos de cada tipo (seção 8, item 1);
  - `.claude/skills/ws-pr-homolog/SKILL.md`, com a oferta tirada das três cópias atuais: `ws pr plano homolog`, o card e `ws pr abrir homolog --card`; na entrega sem repo, o PR do workspace direto para o `main`;
  - `.claude/skills/ws-pr-main/SKILL.md`, a partir de `speckit.ws.promover.md`.
- Rename e modify em `tools/speckit/ws/commands/`: `bug-sem-correcao` para `bug-no-fix`, `bug-enviar` para `bug-submit`, `refactor-registro` para `refactor-record` e `refactor-enviar` para `refactor-submit`. Apague `commit-push.md` e `promover.md`.
- Modify: `tools/speckit/ws/extension.yml` (versão 1.8.0), os testes `test_speckit_feature.sh`, `test_speckit_bug.sh`, `test_speckit_refactor.sh`, `test_speckit_install.sh` e `test_harness.sh`, e `nomes-antigos.txt`.

**Interfaces:**
- **Hooks de fim** (`converge`, `bug-submit` e `refactor-submit`): conferem o resultado como hoje, seguem a skill `atlas-atualizar --gatilho converge` como hoje e terminam com "siga a skill `ws-commit-push`".
- **`ws-commit-push`:** propõe a mensagem pela tabela, roda `bash .specify/extensions/ws/scripts/bash/ws-commit-push.sh "<mensagem>"`, mostra os avisos do tipo e termina com "siga a skill `ws-pr-homolog`".
- **`bug-no-fix`:** oferece a `ws-pr-homolog`.

- [ ] **Step 1:** Acrescente à lista `speckit[-.]ws[-.](commit-push|promover|bug-sem-correcao|bug-enviar|refactor-registro|refactor-enviar)\b`. Rode o teste. Esperado: FALHA.
- [ ] **Step 2: Testes**, por grep no texto, como em `test_speckit_refactor.sh`:
  - **`test_ws_commit_push_mensagem_por_branch`:** cada linha da tabela do spec, seção 8, item 2;
  - **`test_ws_commit_push_avisos_por_tipo`:** `git push -u origin`, `congelamento`, `/speckit-refactor-remove-flag` e `cópia do legado`;
  - **`test_hooks_de_fim_seguem_ws_commit_push`:** os três hooks de fim citam `ws-commit-push` e não contêm `ws pr abrir`;
  - **`test_oferta_dos_prs_so_na_ws_pr_homolog`:** só a `ws-pr-homolog` contém `ws pr abrir homolog`;
  - **`test_comandos_citam_skills_que_existem`;**
  - **`test_skills_ws_tem_descricao_com_quando_usar`:** o `description` de cada `ws-*` contém "Use quando" e "Não use";
  - **`test_extension_ws_registra_os_hooks`:**
    - `after_bug_assess` vai para `bug-no-fix` e `after_bug_test`, para `bug-submit`;
    - os `after_refactor_*` de assess, rollout e validate vão para `refactor-record`, e os de verify, retire_legacy e remove_flag, para `refactor-submit`;
    - não aparecem `commit-push` nem `promover`.
- [ ] **Step 3:** Faça as mudanças. Commit, `tools/ws/ws speckit` e commit das cópias.
- [ ] **Step 4:** Rode `test_nomes_antigos.sh`, `test_speckit_feature.sh`, `test_speckit_bug.sh`, `test_speckit_refactor.sh`, `test_speckit_install.sh` e `test_harness.sh`. Esperado: 0 falha.
- [ ] **Step 5:** Commit `harness: fim de fluxo único e hooks em inglês (SP8)`.

---

### Task 6: Documentação, ADR e suíte inteira

**Files:**
- Modify:
  - `docs/harness/1-comecar.md`: os três fluxos terminam em `/ws-commit-push` → `/ws-pr-homolog` → `/ws-pr-main` → completar, e entra um quadro "Comandos que você digita" × "Comandos que rodam sozinhos";
  - `docs/harness/2-quando-da-errado.md`: entrada nova "Não achei o comando depois de atualizar", com a âncora `#nao-achei-o-comando`. O que fazer: `tools/ws/ws sync && git merge --no-edit ws/sync`;
  - `docs/harness/3-alem-do-basico.md`, `4-manter.md`, `README.md` e `AGENTS.md`;
  - `docs/adr/0001-workspace-git-subtree.md`: o adendo seguinte, com a regra e a tabela antigo → novo.
- Test: `tools/ws/tests/test_docs_referencias.sh`.

- [ ] **Step 1:** Acrescente `test_docs_camada_2_tem_nao_achei_o_comando`. Rode. Esperado: FALHA.
- [ ] **Step 2:** Edite os documentos.
- [ ] **Step 3:** Rode a suíte inteira em segundo plano: `bash tools/ws/tests/run.sh`. Esperado: 0 falha.
- [ ] **Step 4:** Commit `harness: documentação e ADR da padronização dos comandos (SP8)`.

---

### Task 7: Deck v3

**Files:**
- Create, no repo de discovery, `docs/discovery/apresentacao-v3/`, copiando `roteiro.md`, `conteudo.md` e `deck/` de `apresentacao-v2/`. O v2 não muda.

- [ ] **Step 1:** Rode `grep -nE` com os padrões de `nomes-antigos.txt` (sem as exceções) em `apresentacao-v3/deck/project/slides/*.html`. Liste as ocorrências.
- [ ] **Step 2:** Troque os nomes e ajuste os slides em que o fluxo mudou, deixando claro que todos os fluxos terminam igual:
  - `passo-8` a `passo-10`, `resumo`, `bug`, `refactor`, `desacoplamento`, `marcos`, `revisar*`, `cmd-skills`, `onde`, `amanha` e `novidades` (com uma linha sobre o SP8);
  - a capa diz "Versão 3".
  
  Rode o grep de novo. Esperado: nada.
- [ ] **Step 3:** No `deck.json`, mude o título para `Harness WMS — versão 3`. Crie um deck novo a partir do tipo Slides e publique todos os arquivos. Faça o commit no repo de discovery: `Apresentação v3: comandos do SP8`.

---

### Task 8: Validação real (com o usuário)

Registrar em `docs/discovery/sp8-validacao.md`.

- [ ] **Step 1: Feature de teste** até o converge: o hook encadeia o `/ws-commit-push` com `feat(…)` e oferece o `/ws-pr-homolog`. Com o OK do usuário, abra os PRs, confira e abandone.
- [ ] **Step 2: Bug de teste** até o `/speckit-bug-test`: confira a mensagem `fix(<slug>)` e pare antes do envio.
- [ ] **Step 3: Refactor de teste** até o verify: confira a mensagem `refactor(<slug>)` e pare antes do envio.
- [ ] **Step 4: Revisão:** rode o `/ws-pr-review` num PR de teste.
- [ ] **Step 5: Limpeza**, como no SP7.
