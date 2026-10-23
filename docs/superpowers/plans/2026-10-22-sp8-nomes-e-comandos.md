# SP8: Padronização dos comandos e nomes — plano de implementação

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Feature, bug e refactor terminam com os mesmos comandos (`/ws-commit-push`, `/ws-pr-homolog`, `/ws-pr-main`), e tudo o que o dev digita ou vê como nome de comando, subcomando, opção, branch ou pasta nova passa para o inglês, sem mudar o comportamento.

**Architecture:** É uma renomeação guiada por um teste de nomes proibidos que cresce a cada tarefa. Cada tarefa renomeia um grupo de nomes em todos os lugares do escopo: código, fontes dos comandos, cópias geradas, testes e documentação. Depois acrescenta os nomes antigos à lista proibida. Os comandos que o dev digita no fim do fluxo saem da extensão `ws` e viram skills comuns em `.claude/skills/ws-*`. Os hooks continuam na extensão; só os quatro com nome em português mudam (`bug-no-fix`, `bug-submit`, `refactor-record`, `refactor-submit`), e os de fim passam a seguir essas skills.

**Tech Stack:** bash (Git for Windows), Python 3 (stdlib), Spec Kit 1.2.0 (extensões `ws` e `refactor`, regeneradas por `tools/ws/ws speckit` com `uvx`), Claude Code skills.

**Spec:** `docs/superpowers/specs/2026-10-22-sp8-nomes-e-comandos-design.md` (repo de discovery). A tabela antigo → novo está nas seções 4.1 a 4.5 e na seção 8 do spec. O inventário de onde cada nome aparece está em `docs/discovery/nomes-em-portugues.md`. O código fica em `C:\src\wms-workspace`.

## Global Constraints

- **Base:** um worktree novo `C:\src\wms-workspace-sp8`, a partir do `origin/main` (`801331703` ou mais novo), na branch `harness/sp8-nomes`. Não mexa em `C:\src\wms-workspace`, que tem trabalho local.
- **Escopo:** só o que o dev digita ou vê:
  - comandos, skills, hooks e eventos;
  - subcomandos e opções de `tools/ws/ws`;
  - sufixos de branch criados pelos comandos;
  - pastas e arquivos novos de artefato.
- **Fora do escopo** (spec, seção 8, item 6):
  - nomes de arquivo de scripts e módulos;
  - funções e variáveis;
  - subcomandos e opções de scripts internos (`plano.py`, `build-map.py --raiz`, `importa-mapeamento.sh --banco`, os modos `--subida|--validar|--remover|--rodada` do `ws-refactor-start.sh`);
  - chaves de JSON;
  - chaves do `workspace.pr.ini`;
  - o Atlas inteiro: o `ws atlas` e as opções dele, as skills `/atlas-consultar` e `/atlas-atualizar`, os scripts de `tools/atlas/` e os arquivos de `docs/atlas/` (decisão do usuário, 2026-10-22);
  - variáveis de ambiente.
- **Ficam em português:**
  - a documentação e o texto de mensagens, PRs e Chat;
  - os valores gravados em documento: etapas (`entregue`, `convivencia`…), modos da chave (`antigo`, `paralelo`, `sombra`, `novo`), `com-chave`/`sem-chave`, `rascunho`/`revisado` e os estados de card;
  - o que já existe no origin com conteúdo: `docs/harness/*.md`, `docs/adr/*`, `docs/atlas/*`, os templates de `tools/speckit/refactor/templates/` e a branch `atlas/atualizacao`;
  - os marcadores `<!-- ws-revisao:<id> -->` e `<!-- ws-pr:subtrees -->`;
  - os prefixos de commit;
  - o prefixo `eap` de branch e de chave.
- **Spec Kit oficial:** os comandos do Spec Kit e da extensão oficial de bug não mudam.
- **Sem apelidos:** os nomes antigos somem.
- **Cópias geradas:** depois de mudar fonte em `tools/speckit/`, rode `tools/ws/ws speckit` (exige a árvore limpa: commit antes) e commite as cópias regeneradas. Nunca edite `.specify/` ou `.claude/skills/speckit-*` à mão.
- **Commits:** em português, sem atribuição ao Claude.
- **Testes:** `bash tools/ws/tests/run.sh <arquivo>` (cerca de 11 s por teste). A suíte inteira roda só na Task 7.
- **Constitution:** ela cita nomes de comando. Trocar só os nomes é mudança de texto, aprovada pelo PR. Versão: patch (`1.5.0` vira `1.5.1`), com a linha na "Governança".

## Review Focus

1. **Comando novo citado com o nome velho em outro comando:** um hook que manda "siga a skill X" com X inexistente quebra o fluxo em silêncio. O teste de nomes proibidos cobre as citações, e a Task 6 tem o teste `test_hooks_seguem_skills_que_existem`, que confere que toda skill citada num comando existe em `.claude/skills/`.
2. **Mensagem de commit errada numa branch de fatia:** é o caso mais propenso a erro da `/ws-commit-push`. Os testes da Task 6 cobrem cada linha da tabela do spec, seção 8, item 2.
3. **Branch aberta antes do SP8 que traz a `ws/sync`:** os nomes dos comandos mudam no meio do trabalho. A camada 2 ganha a entrada "Não achei o comando depois de atualizar" (Task 7), e o teste de referências da documentação confere a âncora.
4. **Skill `ws-*` disparada sem ser chamada:** a descrição de cada skill nova diz quando usar e quando não usar. O teste `test_skills_ws_tem_descricao_com_quando_usar` (Task 6) confere que a descrição tem as duas partes.
5. **PR antigo revisado de novo:** o marcador `ws-revisao` não pode mudar, senão os comentários duplicam. O teste `test_marcador_da_revisao_nao_muda` (Task 4) confere a constante.

---

### Task 1: Teste de nomes proibidos

**Files:**
- Create: `tools/ws/tests/test_nomes_antigos.sh`, `tools/ws/tests/nomes-antigos.txt`

**Interfaces:**
- Produces: o arquivo `nomes-antigos.txt`, com uma regex estendida por linha (`#` = comentário), e o teste `test_sem_nomes_antigos`. O teste roda `git grep -nE -f <arquivo>` na raiz do workspace, sobre:
  - `tools/` (menos `tools/ws/tests/nomes-antigos.txt`, o próprio teste e `tools/atlas/`, que está fora do escopo);
  - `.claude/`, `.specify/`, `AGENTS.md`, `README.md`, `docs/harness/` (menos `docs/harness/historico/`) e `workspace.pr.ini`.
  
  Ele falha listando `arquivo:linha` de cada ocorrência. As tarefas seguintes acrescentam as regex do seu grupo. Uma seção `# exceções` no fim do arquivo, com uma regex por linha, filtra as linhas permitidas (ex.: `ws-revisao:`, `atlas/atualizacao`, `plano-subida-template`, `desacoplamento-template`).

- [ ] **Step 1:** Escreva o teste com a lista vazia (só comentários e a seção de exceções). Acrescente `test_lista_de_nomes_tem_padroes_validos`, que roda `grep -E` com cada linha num texto vazio e falha se a regex for inválida.
- [ ] **Step 2:** Rode `bash tools/ws/tests/run.sh tools/ws/tests/test_nomes_antigos.sh`. Esperado: 2 ok. Para ver o teste falhar, acrescente uma regex temporária `ws pr plano` e confira a falha; depois retire.
- [ ] **Step 3:** Commit `harness: teste de nomes antigos (SP8)`.

---

### Task 2: `ws pr` em inglês

**Files:**
- Modify:
  - `tools/ws/pr/__main__.py` (subcomandos e texto de uso);
  - `tools/ws/lib/pr.sh`;
  - `tools/ws/lib/push.sh` (a última linha);
  - `tools/ws/pr/abrir.py` e `tools/ws/pr/revisao.py` (mensagens que citam o comando);
  - `tools/ws/tests/test_pr.sh`, `test_pr_revisao.sh`, `test_push.sh`, `test_speckit_*.sh`;
  - fontes `tools/speckit/ws/commands/*.md` e `.claude/skills/ws-revisar/SKILL.md`;
  - `docs/harness/1-4`, `AGENTS.md` e `README.md`;
  - `nomes-antigos.txt`.

**Interfaces:**
- Produces: `tools/ws/ws pr plan|open|review|comment`, com os mesmos argumentos de hoje (`plan <homolog|main> [--card N]`, `open <homolog|main> [--card N]`, `review <link>`, `comment <contexto> <achados>`). A mensagem final do `ws push` passa a ser `ws: para abrir os PRs: tools/ws/ws pr plan homolog`.

- [ ] **Step 1:** Acrescente a `nomes-antigos.txt` a linha `ws pr (plano|abrir|revisao|comentar)\b`. Rode `test_nomes_antigos.sh`. Esperado: FALHA, listando as ocorrências.
- [ ] **Step 2:** Troque os subcomandos no `__main__.py` (um subcomando antigo passa a dar erro de uso) e todas as citações no escopo da Task 1. Atualize os testes que chamam `ws pr plano` e as outras formas antigas.
- [ ] **Step 3:** Commit e rode `tools/ws/ws speckit`. Commite as cópias geradas.
- [ ] **Step 4:** Rode `test_nomes_antigos.sh`, `test_pr.sh`, `test_pr_revisao.sh`, `test_push.sh` e `test_speckit_refactor.sh`. Esperado: 0 falha.
- [ ] **Step 5:** Commit `harness: ws pr plan|open|review|comment (SP8)`.

---

### Task 3: `ws refactor slice`, opções, sufixos de branch e pastas novas

**Files:**
- Modify:
  - `tools/ws/lib/refactor.sh`, `tools/ws/lib/fatia.sh` e `tools/ws/ws` (texto de uso);
  - `tools/speckit/ws/scripts/bash/ws-refactor-start.sh` (só os sufixos de branch) e `tools/ws/pr/entrega.py` e `abrir.py` (`_ORIGENS`, a regex `-subida(-\d+)?$`);
  - `.gitattributes` (se cita `refactors/fatias.md`);
  - os testes `test_fatia.sh`, `test_refactor.sh`, `test_speckit_refactor.sh`, `test_pr.sh` e `test_harness.sh`;
  - as fontes dos comandos de refactor e ws que citam esses nomes e caminhos;
  - `docs/harness/1-4`, `AGENTS.md` e `README.md`;
  - `nomes-antigos.txt`.

**Interfaces:**
- **CLI do refactor:** `tools/ws/ws refactor slice <pending|status|create|type|approve|card|stage|plan|update|state|type-of|flag-of>`, com as opções `--title`, `--decoupling`, `--type`, `--depends-on`, `--slice`, `--state`, `--systems`, `--objects`, `--read-at`, `--note`, `--since` e `--reason`. Os valores posicionais em português (etapas, modos e tipos) não mudam.
- **Branches:**
  - os sufixos novos de `refactor/eap-<código>` são `-rollout[-k]`, `-validate[-k]`, `-remove-flag`, `-coexistence[-k]` (no `update convivencia`) e `-legacy[-k]` (no `update antigo`);
  - os modos internos do `ws-refactor-start.sh` continuam `--subida|--validar|--remover|--rodada`, mas geram os sufixos novos;
  - a promoção reconhece `-rollout(-\d+)?$`.
- **Pastas e arquivos novos:**
  - `refactors/slices.md` (antes `refactors/fatias.md`);
  - `refactors/slices/<código>/` com `rollout-plan.md`, `validation.md`, `retire-legacy.md` e `remove-flag.md`;
  - `refactors/decouplings/<nome>.md` (antes `refactors/desacoplamentos/`).
  
  Os cabeçalhos e o conteúdo do `slices.md` continuam em português.

- [ ] **Step 1:** Acrescente à lista as linhas:
  - `ws refactor fatia\b`;
  - `--(titulo|desacoplamento|tipo|depende|fatia|estado|sistemas|objetos|onde|nota|desde|motivo)\b`;
  - `refactors/(fatias|desacoplamentos)\b`, `plano-subida\.md`, `validacao\.md`, `desacoplar\.md`, `remover\.md`;
  - `eap-[^ ]*-(subida|validar|remover|convivencia|antigo)\b`.
  
  Na seção de exceções, ponha `plano-subida-template\.md` e `desacoplamento-template\.md`. Rode o teste. Esperado: FALHA.
- [ ] **Step 2:** Renomeie no código e em todas as citações. Nos testes, o resultado esperado de cada caso continua o mesmo; só mudam os nomes e caminhos. Mais estes testes:
  - **`test_slice_subcomando_antigo_falha`:** `tools/ws/ws refactor fatia pendentes` sai com erro de uso;
  - **`test_refactor_start_rollout_cria_branch_em_ingles`:** o modo `--subida` cria `refactor/eap-1-1-4-rollout`.
- [ ] **Step 3:** Commit, `tools/ws/ws speckit` e commit das cópias.
- [ ] **Step 4:** Rode `test_nomes_antigos.sh`, `test_fatia.sh`, `test_refactor.sh`, `test_speckit_refactor.sh`, `test_pr.sh` e `test_harness.sh`. Esperado: 0 falha.
- [ ] **Step 5:** Commit `harness: ws refactor slice e pastas novas em inglês (SP8)`.

---

### Task 4: Skill de revisão

**Files:**
- Move: `.claude/skills/ws-revisar/` para `.claude/skills/ws-pr-review/`.
  
  Mude o `name:` no frontmatter.
- Modify: `tools/ws/pr/revisao.py` (os caminhos `.ws/review/<id>/context.json`, `findings.json` e `tree/`; as chaves internas dos JSON ficam), as fontes dos comandos que citam a skill, os testes `test_harness.sh` e `test_pr_revisao.sh`, `docs/harness/1-4`, `AGENTS.md` e `nomes-antigos.txt`.

**Interfaces:**
- Produces: a skill `/ws-pr-review <link>`.

- [ ] **Step 1:** Acrescente à lista as linhas `\bws-revisar\b` e `\.ws/revisao\b`. Rode o teste. Esperado: FALHA.
- [ ] **Step 2:** Faça as mudanças. Mais estes testes:
  - **`test_marcador_da_revisao_nao_muda`:** `revisao.py` contém `ws-revisao:`;
  - **`test_review_grava_em_ws_review`:** o `context.json` em `.ws/review/<id>/`.
- [ ] **Step 3:** Commit, `tools/ws/ws speckit` e commit das cópias.
- [ ] **Step 4:** Rode `test_nomes_antigos.sh`, `test_pr_revisao.sh` e `test_harness.sh`. Esperado: 0 falha.
- [ ] **Step 5:** Commit `harness: skill ws-pr-review (SP8)`.

---

### Task 5: Extensão de refactor em inglês

**Files:**
- Rename e modify em `tools/speckit/refactor/commands/`:
  - `speckit.refactor.subida.md` para `.rollout.md`;
  - `validar` para `validate`;
  - `desacoplar` para `retire-legacy`;
  - `remover` para `remove-flag`.
  
  Atualize também `tools/speckit/refactor/extension.yml` (nomes e bump de minor), `tools/speckit/refactor/hooks.md` (eventos) e `tools/speckit/ws/extension.yml` (eventos nos hooks).
- Modify: as fontes que citam os comandos, os testes `test_speckit_refactor.sh`, `test_speckit_install.sh` e `test_fatia.sh`, `docs/harness/1-4`, `AGENTS.md`, a constitution (patch 1.5.1) e `nomes-antigos.txt`.

**Interfaces:**
- Produces: `/speckit-refactor-rollout`, `/speckit-refactor-validate`, `/speckit-refactor-retire-legacy` e `/speckit-refactor-remove-flag`. Os eventos são `before_`/`after_refactor_rollout`, `_validate`, `_retire_legacy` e `_remove_flag`. Os relatórios vão para `refactors/slices/<código>/{rollout-plan,validation,retire-legacy,remove-flag}.md` (Task 3).

- [ ] **Step 1:** Acrescente à lista as linhas `speckit[-.]refactor[-.](subida|validar|desacoplar|remover)\b` e `(before|after)_refactor_(subida|validar|desacoplar|remover)\b`. Rode o teste. Esperado: FALHA.
- [ ] **Step 2:** Faça as mudanças, mais o teste `test_speckit_registra_os_eventos_de_refactor_em_ingles`: depois do `ws speckit`, o `.specify/extensions.yml` tem os 8 eventos novos e nenhum antigo.
- [ ] **Step 3:** Commit, `tools/ws/ws speckit` e commit das cópias. Os comandos antigos somem de `.claude/skills/`.
- [ ] **Step 4:** Rode `test_nomes_antigos.sh`, `test_speckit_refactor.sh`, `test_speckit_install.sh` e `test_fatia.sh`. Esperado: 0 falha.
- [ ] **Step 5:** Commit `harness: extensão de refactor em inglês (SP8)`.

---

### Task 6: Fim de fluxo único e hooks da extensão `ws`

**Files:**
- Create:
  - `.claude/skills/ws-commit-push/SKILL.md` (a partir da fonte `speckit.ws.commit-push.md`, com a tabela de mensagens do spec, seção 8, item 2, e os avisos de depois do envio, seção 8, item 1);
  - `.claude/skills/ws-pr-homolog/SKILL.md` (a oferta dos PRs, tirada das três cópias atuais);
  - `.claude/skills/ws-pr-main/SKILL.md` (a partir de `speckit.ws.promover.md`).
- Rename e modify em `tools/speckit/ws/commands/`:
  - `bug-sem-correcao` para `bug-no-fix` e `bug-enviar` para `bug-submit`;
  - `refactor-registro` para `refactor-record` e `refactor-enviar` para `refactor-submit`.
  
  Os hooks `feature`, `converge`, `bug-start` e `refactor-start` ficam com o nome de hoje.
  
  Saem do `extension.yml` o `commit-push` e o `promover` (apague os dois `.md`). O `extension.yml` vai para a versão `1.8.0`.
- Modify: `tools/speckit/ws/scripts/bash/ws-commit-push.sh` (só a mensagem de erro que cita o comando), os testes `test_speckit_feature.sh`, `test_speckit_bug.sh`, `test_speckit_refactor.sh`, `test_speckit_install.sh` e `test_harness.sh`, e `nomes-antigos.txt`.

**Interfaces:**
- **Os hooks de fim** (`converge`, `bug-submit` e `refactor-submit`):
  1. conferem o resultado do jeito de hoje;
  2. seguem a skill `atlas-atualizar --gatilho converge`, como hoje;
  3. terminam com "siga a skill `ws-commit-push`".
- **A `ws-commit-push`:**
  1. propõe a mensagem pela tabela;
  2. faz o commit e o envio por `bash .specify/extensions/ws/scripts/bash/ws-commit-push.sh "<mensagem>"`;
  3. mostra os avisos do tipo;
  4. oferece "siga a skill `ws-pr-homolog`".
- **O `bug-no-fix`** oferece a `ws-pr-homolog`, que já trata a entrega sem repo.

- [ ] **Step 1:** Acrescente à lista as linhas `speckit[-.]ws[-.](commit-push|promover|bug-sem-correcao|bug-enviar|refactor-registro|refactor-enviar)\b`. Rode o teste. Esperado: FALHA.
- [ ] **Step 2: Testes** (grep no texto, no padrão de `test_speckit_refactor.sh`):
  - **`test_ws_commit_push_mensagem_por_branch`:** a skill contém cada linha da tabela do spec, seção 8, item 2, com o padrão de branch e o formato da mensagem;
  - **`test_ws_commit_push_avisos_por_tipo`:** a skill contém `git push -u origin`, `congelamento`, `/speckit-refactor-remove-flag` e `cópia do legado`;
  - **`test_hooks_de_fim_seguem_ws_commit_push`:** `converge`, `bug-submit` e `refactor-submit` contêm `ws-commit-push` e não contêm `ws pr open`;
  - **`test_oferta_dos_prs_so_na_ws_pr_homolog`:** só `ws-pr-homolog/SKILL.md` contém `ws pr open homolog`;
  - **`test_hooks_seguem_skills_que_existem`:** toda referência "skill `X`" nas fontes de `tools/speckit/` e em `.claude/skills/ws-*` aponta para um `.claude/skills/X/` existente;
  - **`test_skills_ws_tem_descricao_com_quando_usar`:** o `description` de cada `ws-*` contém "Use quando" e "Não use";
  - **`test_extension_ws_hooks_em_ingles`:** o `extension.yml` registra `before_specify` em `speckit.ws.feature`, `after_converge` em `speckit.ws.converge`, `after_bug_assess` em `speckit.ws.bug-no-fix`, `after_bug_test` em `speckit.ws.bug-submit`, os `after_refactor_*` de assess, rollout e validate em `refactor-record`, e os de verify, retire_legacy e remove_flag em `refactor-submit`; e não tem `commit-push` nem `promover`.
- [ ] **Step 3:** Faça as mudanças. Commit, `tools/ws/ws speckit` e commit das cópias. As skills `speckit-ws-commit-push` e `speckit-ws-promover` somem.
- [ ] **Step 4:** Rode `test_nomes_antigos.sh`, `test_speckit_feature.sh`, `test_speckit_bug.sh`, `test_speckit_refactor.sh`, `test_speckit_install.sh` e `test_harness.sh`. Esperado: 0 falha.
- [ ] **Step 5:** Commit `harness: fim de fluxo único e hooks em inglês (SP8)`.

---

### Task 7: Documentação, ADR e suíte inteira

**Files:**
- Modify:
  - `docs/harness/1-comecar.md`: os três fluxos terminam em `/ws-commit-push` → `/ws-pr-homolog` → `/ws-pr-main` → completar os PRs, e um quadro "Comandos que você digita" × "Comandos que rodam sozinhos";
  - `docs/harness/2-quando-da-errado.md`: entrada nova "Não achei o comando depois de atualizar", com a âncora `#nao-achei-o-comando`. Causa: a branch foi criada antes do SP8, ou trouxe a `ws/sync` pela metade. O que fazer: `tools/ws/ws sync && git merge --no-edit ws/sync`, e os nomes novos estão na camada 1;
  - `docs/harness/3-alem-do-basico.md` e `4-manter.md` (a tabela de peças e a lista de skills);
  - `README.md` e `AGENTS.md`;
  - `docs/adr/0001-workspace-git-subtree.md`: o adendo seguinte, com a regra de nomes (spec, seção 3) e a tabela antigo → novo (seções 4.1 a 4.5).
- Test: `tools/ws/tests/test_docs_referencias.sh`.

- [ ] **Step 1:** Acrescente o teste `test_docs_camada_2_tem_nao_achei_o_comando`. Rode. Esperado: FALHA.
- [ ] **Step 2:** Edite os documentos.
- [ ] **Step 3:** Rode a suíte inteira: `bash tools/ws/tests/run.sh` (longa, em segundo plano). Esperado: `0 falha(s)`. Anote o total.
- [ ] **Step 4:** Commit `harness: documentação e ADR da padronização dos comandos (SP8)`.

---

### Task 8: Deck v3

**Files:**
- Create, no repo de discovery, `docs/discovery/apresentacao-v3/`, copiando `roteiro.md`, `conteudo.md` e `deck/` de `apresentacao-v2/` (o v2 não muda). Depois mude em `apresentacao-v3/deck/project/slides/*.html`:
  - passos 8 a 10 da feature, `resumo`, `bug`, `refactor`, `desacoplamento`, `marcos`, `revisar*`, `cmd-ws`, `cmd-skills`, `erros-prs`, `onde`, `amanha`, `regras`, `novidades` e qualquer slide que cite um nome antigo;
  - o `roteiro.md`, a seção 11 do `conteudo.md` e uma linha "SP8" em `novidades`; a capa diz "Versão 3".

- [ ] **Step 1:** Rode `grep -nE -f <workspace>/tools/ws/tests/nomes-antigos.txt deck/project/slides/*.html` (sem a seção de exceções). Liste as ocorrências.
- [ ] **Step 2:** Troque os nomes e ajuste o texto onde o fluxo mudou: "todos os fluxos terminam igual". Rode o grep de novo. Esperado: nenhuma ocorrência.
- [ ] **Step 3:** No `deck.json`, mude o título para `Harness WMS — versão 3`, mantendo o resto. Crie um deck novo a partir do tipo Slides e publique todos os arquivos do v3 nele, como foi feito no v2. Faça o commit no repo de discovery `Apresentação v3: nomes do SP8`.

---

### Task 9: Validação real (com o usuário)

Sem código. Registrar em `docs/discovery/sp8-validacao.md`, no repo de discovery.

- [ ] **Step 1: Feature de teste** numa branch `ws-9xx-teste-sp8`. Rode `/speckit-specify` até o `/speckit-converge`. Confira que o hook encadeia `/ws-commit-push` com a mensagem `feat(…)` e depois oferece o `/ws-pr-homolog`. Com o OK do usuário, abra os PRs, confira e abandone.
- [ ] **Step 2: Bug de teste.** Rode `/speckit-bug-assess` até o `/speckit-bug-test`. Confira a mensagem `fix(<slug>)` proposta e pare antes do envio, ou envie e abandone com o OK do usuário.
- [ ] **Step 3: Refactor de teste.** Rode do `assess` ao `verify`. Confira a mensagem `refactor(<slug>)` e pare antes do envio.
- [ ] **Step 4: Revisão.** Rode o `/ws-pr-review` num PR de teste e confira o `.ws/review/<id>/context.json`.
- [ ] **Step 5: Limpeza.** Abandone os PRs e apague as branches de teste, como no SP7.
