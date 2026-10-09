# Harness do AWX subordinado ao workspace: plano de implementação

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** o AWX volta a ter o Spec Kit e a constitution dele, sem alteração; o workspace passa a numerar as features como `ws-NNN` e escreve a subordinação só na raiz.

**Architecture:**
- Os caminhos de harness do AWX voltam a ser idênticos aos do commit do AWX sincronizado no workspace.
- O hook `ws-feature.sh` passa a usar o prefixo `ws-` em pastas, branches e citações.
- O `AGENTS.md`, o preset `multirepo`, a constitution do workspace e as skills ganham as regras de subordinação, e o Spec Kit é reinstalado para propagar o preset.
- No fim vem a validação de ponta a ponta num ambiente descartável.

**Tech Stack:** bash (Git Bash no Windows), git subtree, Spec Kit 1.0.12 (via `uvx`), runner de testes `tools/ws/tests/run.sh`.

**Spec:** `C:\src\00-harness_big_brown_field\docs\superpowers\specs\2026-10-07-sp2-adendo-harness-awx-subordinado-design.md`

**Onde:** workspace `C:\src\wms-workspace`, branch `sp3-atlas` (sem publicação). Todos os caminhos abaixo são relativos a ele, a menos que digam o contrário.

## Global Constraints

- Prefixo das features do workspace: `ws-`. Pasta `specs/ws-NNN-<nome>/`, branch `ws-NNN-<nome>`, revisão `ws-NNN-<nome>-rK`, com NNN de 3 dígitos.
- Caminho do AWX: `repos/industria-logistica.wms.awx.monorepo`. A constitution dele fica em `.specify/memory/constitution.md` (não em `docs/constitution.md`).
- Caminhos do harness do AWX que precisam ficar idênticos ao repo dele: `.specify`, `.claude`, `specs`, `CLAUDE.md`, `AGENTS.md`, `docs/constitution.md` e `src/Integrations/AWX.IntegracaoLegadoWMS/AGENTS.md`.
- A trava do `ws push` (bloquear `.specify/`, `specs/` e `.claude/skills/speckit-*` dentro de repos) não muda.
- Nada é publicado: sem `git push` para o Azure DevOps. A validação de ponta a ponta usa só espelhos locais.
- Textos em português do Brasil. Commits terminam com `Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>`.
- Testes: rodar **um arquivo de teste por vez** (`bash tools/ws/tests/run.sh tools/ws/tests/<arquivo>.sh`), nunca a suíte inteira de uma vez, porque a máquina reiniciou três vezes durante a suíte completa.
- Em Python embutido no bash, não use barras invertidas dentro de heredoc. Para texto com `\`, use o Edit/Write.

## Review Focus

- **Citação "a 004" quando só existe uma spec `004-…` sem prefixo** (uma cópia antiga, ou uma spec do AWX lida por engano): precisa dar erro "não achei a feature ws-004". Não pode abrir revisão nem criar feature nova. Teste na Task 2.
- **Branches `NNN-*` do AWX no origin do workspace ou locais:** não podem empurrar a numeração `ws-`. Teste na Task 2.
- **Branch atual `ws-NNN-<nome>` sem spec** (specify interrompido): continua nela, como hoje. Teste adaptado na Task 2.
- **Reinstalação do Spec Kit sobrescrevendo o preset:** o template de plan instalado em `.specify/presets/multirepo/templates/` precisa ter a linha nova. Teste na Task 3.
- **Restauração do AWX deixando sobra do SP2,** por exemplo um `docs/constitution.md` que não existe no repo: o teste da Task 1 compara a árvore inteira desses caminhos.

---

### Task 1: AWX volta a ser como o time mantém

**Files:**
- Modify (restauração): `repos/industria-logistica.wms.awx.monorepo/{.specify,.claude,specs,CLAUDE.md,AGENTS.md,src/Integrations/AWX.IntegracaoLegadoWMS/AGENTS.md}`
- Delete: `repos/industria-logistica.wms.awx.monorepo/docs/constitution.md`, se não existir no repo do AWX
- Delete: `specs/001-picking-b2c-consumer/`, `specs/002-sku-multiplo-codigo-barra/`, `specs/003-nf-faturamento-b2c/` (cópias na raiz)
- Test: `tools/ws/tests/test_harness.sh`

**Interfaces:**
- Produces: árvore do AWX igual à do último commit squash dele; `specs/` da raiz sem pastas `NNN-*`.

- [ ] **Step 1: Escrever os testes**

Acrescente ao fim de `tools/ws/tests/test_harness.sh`:

```bash
# Adendo SP2 (2026-10-07): o harness do AWX fica como no repo dele.
test_harness_do_awx_igual_ao_do_repo() {
  local p=repos/industria-logistica.wms.awx.monorepo sq
  sq=$(git -C "$WS_RAIZ" log -1 --format=%H --grep="git-subtree-dir: $p\$")
  [ -n "$sq" ] || fail "não achei o commit squash do AWX"
  git -C "$WS_RAIZ" diff --quiet "$sq" "HEAD:$p" -- .specify .claude specs CLAUDE.md AGENTS.md \
    docs/constitution.md src/Integrations/AWX.IntegracaoLegadoWMS/AGENTS.md \
    || fail "o harness do AWX difere do repo: $(git -C "$WS_RAIZ" diff --stat "$sq" "HEAD:$p" -- .specify .claude specs CLAUDE.md AGENTS.md docs/constitution.md | tail -1)"
}

test_specs_da_raiz_sem_copias_sem_prefixo() {
  [ -z "$(git -C "$WS_RAIZ" ls-files 'specs/[0-9][0-9][0-9]-*')" ] || fail "specs/NNN-* sem prefixo na raiz"
}
```

O teste compara o `HEAD` commitado. Por isso a Task 1 só fica verde depois do commit do Step 4.

- [ ] **Step 2: Rodar e ver falhar**

Run: `bash tools/ws/tests/run.sh tools/ws/tests/test_harness.sh`
Expected: FALHA nos dois testes novos (`o harness do AWX difere do repo` e `specs/NNN-* sem prefixo na raiz`).

- [ ] **Step 3: Restaurar**

```bash
p=repos/industria-logistica.wms.awx.monorepo
sq=$(git log -1 --format=%H --grep="git-subtree-dir: $p\$")
git rm -r -q --ignore-unmatch -- "$p/.specify" "$p/.claude" "$p/specs" "$p/CLAUDE.md" "$p/AGENTS.md" \
  "$p/docs/constitution.md" "$p/src/Integrations/AWX.IntegracaoLegadoWMS/AGENTS.md"
# Pastas: a árvore do commit squash vai para o prefixo do AWX.
for c in .specify .claude specs; do
  git cat-file -e "$sq:$c" 2>/dev/null && git read-tree --prefix="$p/$c/" -u "$sq:$c"
done
# Arquivos: pelo blob, byte a byte (preserva CRLF e BOM).
for f in CLAUDE.md AGENTS.md docs/constitution.md src/Integrations/AWX.IntegracaoLegadoWMS/AGENTS.md; do
  if git cat-file -e "$sq:$f" 2>/dev/null; then
    mkdir -p "$(dirname "$p/$f")"
    git cat-file blob "$sq:$f" > "$p/$f"
    git add "$p/$f"
  fi
done
git rm -r -q -- specs/001-picking-b2c-consumer specs/002-sku-multiplo-codigo-barra specs/003-nf-faturamento-b2c
git status --short | head
```

A conferência é o teste do Step 4.

- [ ] **Step 4: Commit e testes**

```bash
git commit -qm "harness: AWX mantém o Spec Kit e a constitution dele (adendo SP2 de 2026-10-07)

Desfaz a parte do AWX de b9f8effe6 e tira da raiz as cópias das specs 001 a 003.

Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>"
bash tools/ws/tests/run.sh tools/ws/tests/test_harness.sh
```
Expected: `7 ok, 0 falha(s)`. Se o teste do AWX ainda falhar, rode `git diff --stat "$sq" "HEAD:$p" -- .specify .claude specs CLAUDE.md AGENTS.md`, corrija o que sobrou e faça `git commit --amend --no-edit`.

---

### Task 2: numeração `ws-NNN` no hook

**Files:**
- Modify: `tools/speckit/ws/scripts/bash/ws-feature.sh`
- Test: `tools/ws/tests/test_speckit_feature.sh`

**Interfaces:**
- Produces: saída JSON do hook com `BRANCH_NAME=ws-NNN-<nome>[-rK]`, `FEATURE_NUM=ws-NNN`, `FEATURE_DIRECTORY=specs/ws-NNN-<nome>`. Os campos não mudam de nome.

- [ ] **Step 1: Adaptar os testes que existem**

```bash
f=tools/ws/tests/test_speckit_feature.sh
sed -i -E 's/(^|[^0-9a-z#])([0-9]{3})-([a-z])/\1ws-\2-\3/g' "$f"
sed -i -E 's/"FEATURE_NUM" "\$OUT"\)" "([0-9]{3})"/"FEATURE_NUM" "$OUT")" "ws-\1"/' "$f"
sed -i -E 's/a feature ([0-9]{3}) ainda não está no main/a feature ws-\1 ainda não está no main/; s/não achei a feature ([0-9]{3})/não achei a feature ws-\1/' "$f"
grep -nE '(^|[^-0-9a-z#])[0-9]{3}-[a-z]' "$f" | grep -v 'ws-' | head
```
Expected: o último `grep` sem saída. As citações em texto livre ("Altera a 002", "#005", "feat 005") continuam sem prefixo de propósito: no workspace elas querem dizer `ws-NNN`.

Confira à mão a linha do `json_get FEATURE_NUM` em `test_feature_nova_com_specs_vazio_usa_001`. Ela deve esperar `ws-001`. Se o `sed` não tiver pegado, troque `"001"` por `"ws-001"` nessa linha.

- [ ] **Step 2: Acrescentar os testes novos**

Ao fim de `tools/ws/tests/test_speckit_feature.sh`:

```bash
# Adendo SP2 (2026-10-07): specs e branches sem prefixo (do AWX ou cópias antigas) não contam.
test_specs_e_branches_sem_prefixo_nao_contam_na_numeracao() {
  fx_ready
  mk_spec 007-do-awx
  git branch 009-branch-do-awx
  git push -q origin main:refs/heads/011-outra-do-awx
  assert_ok feature --short-name "nova coisa" "Uma coisa nova"
  assert_eq "$(json_get BRANCH_NAME "$OUT")" "ws-001-nova-coisa"
}

test_citacao_com_prefixo_vira_revisao() {
  fx_ready
  mk_spec ws-004-checkout-aviso
  local d
  for d in "Altera a ws-004: texto" "Mudar specs/ws-004 para outro campo" "Ajuste em ws-004-checkout-aviso: campo"; do
    git checkout -q main
    git branch --list 'ws-004-checkout-aviso-r*' | xargs -r git branch -q -D
    assert_ok feature "$d"
    assert_eq "$(json_get BRANCH_NAME "$OUT")" "ws-004-checkout-aviso-r1" "$d"
    assert_eq "$(json_get FEATURE_NUM "$OUT")" "ws-004" "$d"
  done
}

test_numero_sem_prefixo_e_sempre_o_do_workspace() {
  fx_ready
  mk_spec 004-do-awx
  assert_fails feature "Altera a 004: qualquer coisa"
  assert_contains "$(json_get ERROR "$OUT")" "não achei a feature ws-004"
  assert_eq "$(git symbolic-ref --short HEAD)" "main"
}
```

- [ ] **Step 3: Rodar e ver falhar**

Run: `bash tools/ws/tests/run.sh tools/ws/tests/test_speckit_feature.sh`
Expected: a maioria FALHA (o hook ainda gera `NNN-`). Os testes de `commit_push` passam.

- [ ] **Step 4: Implementar**

Em `tools/speckit/ws/scripts/bash/ws-feature.sh`:

1. Cabeçalho (linhas 3 a 8): troque `NNN-<nome>` por `ws-NNN-<nome>` e `NNN-<nome>-r<k>` por `ws-NNN-<nome>-r<k>`. Acrescente a linha:
   `# Prefixo ws- (adendo SP2 de 2026-10-07): specs e branches NNN-* sem prefixo, como as do AWX, não contam.`
2. Depois de `WS_BASE=${WS_BASE:-main}`:
   ```bash
   P=ws-   # prefixo das features do workspace

   # ws-NNN-<nome>[-r<k>] -> ws-NNN
   feat_num() { local r=${1#"$P"}; echo "$P${r%%-*}"; }
   ```
3. `spec_names`: troque `grep -E '^[0-9]{3}-'` por `grep -E "^$P[0-9]{3}-"`.
4. `cited_nums`: no `grep -oE`, acrescente a alternativa `|(^|[^[:alnum:]])ws-[0-9]{3}([^0-9]|$)` antes de `|#[0-9]{3}`. O comentário ganha "ws-004", "specs/ws-004" e "ws-004-<nome>".
5. `matches`: troque as duas primeiras linhas por
   ```bash
   local rest=${1#"$P"}
   local num=${rest%%-*} slug=${rest#*-}
   ```
6. `feature_branches`: `grep -E "^$P[0-9]{3}-"`.
7. `next_num`:
   - `spec_names | cut -c4-6`;
   - nas duas buscas de branch, `grep -oE "^$P[0-9]{3}-" | cut -c4-6`;
   - o comentário passa a citar `ws-NNN-*`.
8. Bloco "Já na branch da própria feature":
   - `[[ "$curfeat" =~ ^ws-[0-9]{3}- ]]`;
   - `emit "$cur" "$(feat_num "$curfeat")" "specs/$curfeat" true ""`.
9. Bloco "Já numa branch … sem a spec":
   - `[[ "$cur" =~ ^ws-[0-9]{3}-[a-z0-9] ]]`;
   - `emit "$cur" "$(feat_num "$cur")" "specs/$cur" false ""`.
10. Mensagens:
    - `fail "a feature $(feat_num "$pend") ainda não está no main: …"` (o resto igual);
    - `fail "não achei a feature $P$n em specs/ do main nem em branches ${P}NNN-*"`.
11. `name="$P$(next_num)-$slug"`.
12. Última linha: `emit "$branch" "$(feat_num "$name")" "specs/$name" "$existing" ""`.

- [ ] **Step 5: Rodar e ver passar**

Run: `bash tools/ws/tests/run.sh tools/ws/tests/test_speckit_feature.sh`
Expected: `36 ok, 0 falha(s)`.

- [ ] **Step 6: Commit**

```bash
git add tools/speckit/ws/scripts/bash/ws-feature.sh tools/ws/tests/test_speckit_feature.sh
git commit -qm "harness: features do workspace numeradas ws-NNN (adendo SP2 de 2026-10-07)

Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>"
```

---

### Task 3: regras de subordinação e reinstalação do Spec Kit

**Files:**
- Modify: `AGENTS.md`, `docs/workspace.md`, `.specify/memory/constitution.md`
- Modify: `tools/speckit/multirepo/templates/plan-template.md`, `tools/speckit/ws/commands/speckit.ws.commit-push.md`
- Modify: `.claude/skills/atlas-consultar/SKILL.md`
- Regenerados pelo `ws speckit`: `.specify/presets/multirepo/**`, `.specify/extensions/ws/**`, `.claude/skills/speckit-*/SKILL.md`
- Test: `tools/ws/tests/test_harness.sh`

**Interfaces:**
- Consumes: hook com prefixo `ws-` (Task 2).

- [ ] **Step 1: Escrever o teste**

Ao fim de `tools/ws/tests/test_harness.sh`:

```bash
# Adendo SP2 (2026-10-07): subordinação escrita no workspace.
test_subordinacao_de_repo_com_spec_kit_proprio() {
  local a="$WS_RAIZ/AGENTS.md" f
  grep -qF 'skills `speckit-*` dentro de `repos/`' "$a" || fail "AGENTS.md sem a regra das skills speckit dos repos"
  grep -qF 'specs/ws-NNN-<nome>/' "$a" || fail "AGENTS.md sem o formato ws-NNN"
  grep -qF '.specify/memory/constitution.md` do repo' "$a" || fail "AGENTS.md sem a constitution do repo"
  for f in tools/speckit/multirepo/templates/plan-template.md .specify/presets/multirepo/templates/plan-template.md; do
    grep -qF 'Constitution do repo' "$WS_RAIZ/$f" || fail "$f sem a linha da constitution do repo"
  done
  ! grep -qF 'docs/constitution.md' "$WS_RAIZ/tools/speckit/multirepo/templates/plan-template.md" \
    || fail "plan-template ainda cita docs/constitution.md"
}
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `bash tools/ws/tests/run.sh tools/ws/tests/test_harness.sh`
Expected: FALHA em `test_subordinacao_de_repo_com_spec_kit_proprio` (`AGENTS.md sem a regra das skills speckit dos repos`).

- [ ] **Step 3: `AGENTS.md`**

- **Regra 1:** troque a lista final `` `docs/adr/` e `docs/constitution.md` `` por `` `docs/adr/` e a constitution do repo, se houver (`.specify/memory/constitution.md` ou `docs/constitution.md`) ``.
- **Regra 2:** passa a ser:
  ```markdown
  2. **Repo com fluxo ou Spec Kit próprio** (hoje o AWX):
     - o Spec Kit do repo é de quem trabalha no clone dele. No workspace vale o fluxo da raiz, inclusive para uma feature que toca só esse repo;
     - não use as skills `speckit-*` dentro de `repos/` (o Claude Code as mostra como `/repos/<repo>:speckit-*`), só as da raiz;
     - a `.specify/memory/constitution.md` do repo vale para o código dele. O plan confere essa constitution e a do workspace; se as duas conflitarem, pare e pergunte ao humano;
     - as specs do repo (`repos/<repo>/specs/`) são referência de negócio: leia e cite, nunca altere.
  ```
- **Regra 4:** acrescente ao fim: `Esses arquivos são do time dono do repo.`
- **Seção "Features com o Spec Kit":**
  - em "Iniciar", troque `cite o número dela ("a 004", "feature 004")` por `` cite o número dela ("a 004", "feature 004", "ws-004"; no workspace o número é sempre o de `specs/ws-NNN-*`) ``;
  - troque `` `specs/NNN-*` `` por `` `specs/ws-NNN-*` ``;
  - troque `` (`NNN-<nome>` ou `NNN-<nome>-r<k>`) `` por `` (`ws-NNN-<nome>` ou `ws-NNN-<nome>-r<k>`) ``;
  - em "Onde ficam", troque `` `specs/NNN-<nome>/`, só no workspace `` por `` `specs/ws-NNN-<nome>/`, só no workspace (o prefixo separa das specs dos repos, como `repos/<awx>/specs/NNN-*`) ``.

- [ ] **Step 4: Preset, comando e docs**

- **`tools/speckit/multirepo/templates/plan-template.md`:**
  - na lista de instruções, troque `` `docs/adr/` e `docs/constitution.md` `` por `` `docs/adr/` ``;
  - logo abaixo, acrescente:
    `- **Constitution do repo:** <caminho, se o repo tiver uma (ex.: .specify/memory/constitution.md no AWX), e os princípios dela que a mudança toca, com o resultado da conferência; conflito com a constitution do workspace vira pergunta ao humano. Ou "o repo não tem">`
- **`tools/speckit/ws/commands/speckit.ws.commit-push.md`:**
  - troque `` `feat(NNN): <título da feature> [specs/NNN-<nome>]` `` por `` `feat(ws-NNN): <título da feature> [specs/ws-NNN-<nome>]` ``;
  - troque `` `specs/NNN` `` por `` `specs/ws-NNN` ``.
- **`.specify/memory/constitution.md`:** no princípio I, acrescente o item
  `- Um repo com constitution própria (hoje o AWX) a mantém para o código dele; esta constitution vale para o que cruza repos e para o jeito de trabalhar no workspace.`
  Na Governança, troque `Versão 1.0.0, ratificada em 2026-09-29.` por `Versão 1.1.0, ratificada em 2026-09-29 e emendada em 2026-10-07 (constitution dos repos).`
- **`docs/workspace.md`, linha 29:**
  - troque `` `specs/NNN-<nome>/` `` por `` `specs/ws-NNN-<nome>/` ``;
  - troque `` `NNN-<nome>-r<k>` `` por `` `ws-NNN-<nome>-r<k>` ``;
  - depois de `("a 004", "feature 004")`, acrescente `` (no workspace o número é sempre o de `specs/ws-NNN-*`) ``.

  Logo abaixo do item, acrescente:
  `- **Repo com Spec Kit próprio (AWX):** o Spec Kit e a constitution dele ficam no repo, para quem trabalha no clone. No workspace vale o fluxo da raiz; a constitution do AWX é conferida no plan.`
- **`.claude/skills/atlas-consultar/SKILL.md`:** na tabela do nível 1, acrescente a linha:
  `` | Specs feitas pelo time do AWX no repo dele | `repos/industria-logistica.wms.awx.monorepo/specs/` (referência de negócio; não altere) | ``

- [ ] **Step 5: Reinstalar o Spec Kit e propagar o preset**

```bash
git add -A AGENTS.md docs/workspace.md .specify/memory/constitution.md tools/speckit .claude/skills/atlas-consultar
git commit -qm "wip: subordinação (antes da reinstalação)"   # o ws speckit exige árvore limpa
bash tools/ws/ws speckit
git status --short | head -30
```
Expected: `Spec Kit 1.0.12 instalado …`. Mudam `.specify/presets/multirepo/templates/plan-template.md`, `.claude/skills/speckit-ws-commit-push/SKILL.md` e, talvez, timestamps em registries. Confira com `git diff` que a `.specify/memory/constitution.md` não foi sobrescrita, porque o `init --force` a mantém.

Sem rede ou sem `uvx`, copie à mão:
- `tools/speckit/multirepo/templates/plan-template.md` para `.specify/presets/multirepo/templates/plan-template.md`;
- o texto do `speckit.ws.commit-push.md` para `.specify/extensions/ws/commands/speckit.ws.commit-push.md` e para o corpo de `.claude/skills/speckit-ws-commit-push/SKILL.md`, mantendo o frontmatter da skill.

Registre isso no relatório.

- [ ] **Step 6: Rodar os testes**

```bash
bash tools/ws/tests/run.sh tools/ws/tests/test_harness.sh
bash tools/ws/tests/run.sh tools/ws/tests/test_speckit_install.sh
```
Expected: `8 ok, 0 falha(s)` e `6 ok, 0 falha(s)`.

- [ ] **Step 7: Commit (junta o wip)**

```bash
git add -A .specify .claude
git commit -q --amend -m "harness: subordinação do Spec Kit e da constitution dos repos ao workspace (adendo SP2 de 2026-10-07)

AGENTS.md, constitution 1.1.0, plan com a constitution do repo, ws-NNN nos textos e Spec Kit reinstalado.

Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>"
```

---

### Task 4: suíte completa

- [ ] **Step 1: Rodar arquivo por arquivo**

```bash
for f in tools/ws/tests/test_*.sh; do echo "$(basename "$f"): $(bash tools/ws/tests/run.sh "$f" 2>&1 | grep 'falha(s)')"; done
```
Rode em blocos de até 5 arquivos por chamada, cada uma com até 10 minutos. Expected: todos com `0 falha(s)`, cerca de 184 testes. Uma falha volta para a task dona.

---

### Task 5: (OK) validação de ponta a ponta

Peça OK ao usuário antes: usa LLM, por volta de US$ 5 a 10.

**Ambiente:**
- Workspace `C:\src\wms-workspace-e2e4`.
- Origin bare `C:\src\wms-e2e4-origin.git`, com o `main` na ponta da `sp3-atlas`.
- AWX num espelho local `C:\src\wms-e2e4-awx.git` (clone bare do AWX). O `workspace.repos` aponta para ele.
- `pushInsteadOf` bloqueando `https://dev.azure.com/`.
- O `atlas.estado` dos outros 16 repos avançado até o commit atual, como no e2e3, para o Atlas não mapear nada além do AWX.

- [ ] **Step 1: Montar** (mesmos comandos do e2e3, em `docs/discovery/sp3-validacao.md`, seção do Step 7)
- [ ] **Step 2: Qual `/speckit-specify` roda**

```bash
claude -p "Leia repos/industria-logistica.wms.awx.monorepo/CLAUDE.md e liste os nomes exatos de todas as skills disponíveis que contenham speckit-specify." --permission-mode bypassPermissions
claude -p "/speckit-specify No checkout do AWX, registrar no log o identificador da caixa ao fechar o volume." --permission-mode bypassPermissions --output-format json
```

Esperado:
- a skill do AWX aparece só na forma `repos/industria-logistica.wms.awx.monorepo:speckit-specify`;
- a branch criada é `ws-001-…`;
- a spec fica em `specs/ws-001-…/spec.md`;
- o `git status` de `repos/…awx…/.specify` e de `repos/…awx…/specs` está limpo.

Se o comando rodar o fluxo do AWX, **pare** e leve o resultado ao usuário (spec, seção 5.3).
- [ ] **Step 3: Plan e envio**
  1. Retome a sessão com `/speckit-plan`. O plan deve ter a linha "Constitution do repo" do AWX, com `.specify/memory/constitution.md`.
  2. Faça à mão um commit trivial em `repos/…awx…/` (uma linha num `.md` de `docs/`) e rode `tools/ws/ws push`. A branch `ws-001-…` deve aparecer no espelho.
  3. Num clone do espelho, rode o script de feature do Spec Kit do AWX. Ele deve propor o número `004`, sem levar em conta a `ws-001`:
     ```bash
     pwsh .specify/scripts/powershell/create-new-feature.ps1 -Json -DryRun "teste"
     ```
     Se o script não tiver `-DryRun`, rode e descarte a branch criada.
- [ ] **Step 4: Registrar**
  - Os resultados, item a item, ok ou não ok, numa seção nova "Adendo AWX (2026-10-07)" em `C:\src\00-harness_big_brown_field\docs\discovery\sp2-validacao.md`.
  - O estado em `docs/discovery/estado-da-sessao.md`.

---

### Task 6: revisão final

- [ ] **Step 1:** revisão da diferença `1e75f4639..HEAD`, os commits deste plano, por um revisor do modelo mais capaz. Ele confere contra a spec e verifica:
  - o hook (as regex `ws-`, sem regressão nas citações antigas);
  - a restauração do AWX;
  - a coerência dos textos.
- [ ] **Step 2:** correção dos achados Critical e Important com TDD. Os achados menores ficam registrados no estado da sessão.
- [ ] **Step 3:** atualizar a spec do adendo para "implementado" e o `estado-da-sessao.md`. O ponto da seção 3.2 está resolvido: o core 1.0.12 resolve a pasta por `SPECIFY_FEATURE_DIRECTORY` e `.specify/feature.json`, sem exigir `NNN-`.
