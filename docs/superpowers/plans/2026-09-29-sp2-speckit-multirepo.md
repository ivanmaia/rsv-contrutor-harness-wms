# SP2: Spec Kit multi-repo no workspace WMS — plano de implementação

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Objetivo:** instalar o Spec Kit 1.0.12 na raiz do workspace com a extensão local `ws` e o preset local `multirepo`, a constitution curta, o `AGENTS.md` com a hierarquia, o conhecimento do SP0 em `docs/sistemas/` e a nova guarda do `ws push`, e migrar a maquinaria de Spec Kit do AWX para a raiz.

**Arquitetura:**
- **Fontes:** a extensão e o preset ficam versionados em `tools/speckit/` e são instalados pelo novo comando `tools/ws/ws speckit`, que roda o Spec Kit via `uvx` com a versão fixada em `tools/speckit/VERSION`.
- **Hooks:** o `before_specify` chama `ws-feature.sh`, que cria a branch com `ws start` (feature nova ou revisão). O `after_converge` oferece `ws-push.sh`.
- **Preset:** acrescenta seções aos templates e envolve o comando `specify` com as regras do workspace.

**Stack:** bash (Git Bash), git ≥ 2.40, Spec Kit 1.0.12 via `uvx` (uv 0.11+), Python só nos testes (checar JSON). Os testes seguem o runner bash de `tools/ws/tests`.

**Spec:** `C:\src\00-harness_big_brown_field\docs\superpowers\specs\2026-09-28-sp2-speckit-multirepo-design.md` (aprovada em 2026-09-29). ADR: `C:\src\00-harness_big_brown_field\docs\adr\0001-workspace-git-subtree.md`. PoC: `C:\src\00-harness_big_brown_field\poc\sp2-speckit\README.md`.

**Onde:** no workspace `C:\src\wms-workspace` (`/c/src/wms-workspace` no Git Bash). Caminhos relativos à raiz do workspace, salvo indicação.

**Validação prévia:** o código e os testes deste plano foram rodados numa cópia descartável do `tools/` do workspace antes de o plano ser escrito:
- suíte offline: 86 ok, 0 falha, contando os testes novos;
- testes de rede do `ws speckit`: 6 ok com `WS_TEST_REDE=1`;
- `importa-discovery.sh` rodado contra o discovery real: 177 arquivos copiados e nenhum recusado.

## Restrições globais

- Spec Kit **1.0.12**, integração `claude`, `--script sh`, **sem** a extensão `git`. A versão fica fixada em `tools/speckit/VERSION`.
- Specs em `specs/NNN-<nome>/` na raiz, numa sequência única. Branch de feature nova: `NNN-<nome>`. Branch de revisão: `NNN-<nome>-r<k>`.
- Marcadores de task: `[repos/<repo>]` e `[workspace]`.
- **A guarda do `ws push` (adendo 4 à ADR 0001) bloqueia** adicionar, alterar ou trocar o tipo de: `.specify/` (em qualquer nível), `specs/` na raiz do repo e `.claude/skills/speckit-*`.
  - **Passam:** `CLAUDE.md`, `AGENTS.md`, o resto de `.claude/`, `.github/copilot-instructions.md` e `.github/agents/`.
  - **Remoção:** sempre permitida.
- O hook `after_converge` (`speckit.ws.push`) é **opcional** e pede confirmação. O push também pode ser feito à mão.
- PRs dos repos e do workspace são abertos e mergeados **à mão**.
- Mensagens, comentários e docs em português.
- **Ações externas que exigem OK explícito do usuário:** o `ws push` do AWX (Task 6) e o push de qualquer branch do workspace para o origin (Task 9).

## Foco da revisão

Entradas e condições que a spec implica e que mais podem dar errado. Cada uma tem teste na task indicada:

1. **O agente pular o hook `before_specify`** (hooks são instruções, não execução automática). Esperado: a validação manual pega; a guarda do `ws push` continua sendo a proteção dos repos. Task 8, itens 2 e 3 do checklist.
2. **Descrição com um número que não é feature** ("aceitar até 200 caixas"). Esperado: feature nova, não revisão. Task 2, `test_numero_na_descricao_que_nao_e_feature_cria_feature_nova`.
3. **`ws speckit` mexer em `AGENTS.md` ou `CLAUDE.md` já existentes.** Esperado: não mexer. Task 3, asserts em `test_speckit_instala_hooks_skills_e_preset`.
4. **Mover as specs do AWX para a raiz** é um rename para fora do prefixo. Esperado: o `ws push` envia a remoção para o AWX. Já coberto por `test_push_envia_arquivo_de_agente_movido_para_o_harness`, e conferido na Task 6, Step 6.
5. **Revisão de uma feature cuja branch `-r1` já existe no origin** e não localmente. Esperado: usa `-r2`. Task 2, `test_revisao_pula_branch_que_ja_existe_local_ou_no_origin`.

## Estrutura de arquivos

| Arquivo | Responsabilidade |
|---|---|
| `tools/ws/lib/push.sh` | Guarda nova (adendo 4) |
| `tools/speckit/VERSION` | Versão fixada do Spec Kit |
| `tools/speckit/ws/extension.yml` | Extensão `ws`: comandos e hooks |
| `tools/speckit/ws/commands/speckit.ws.feature.md`, `speckit.ws.push.md` | Instruções dos comandos para o agente |
| `tools/speckit/ws/scripts/bash/ws-feature.sh` | Hook `before_specify`: calcula feature ou revisão, roda `ws start` e devolve JSON |
| `tools/speckit/ws/scripts/bash/ws-push.sh` | Roda `ws push` |
| `tools/speckit/multirepo/preset.yml`, `templates/*`, `commands/speckit.specify.md` | Preset: seções nos templates e regras envolvendo o `specify` |
| `tools/ws/lib/speckit.sh`, `tools/ws/ws` | Comando `ws speckit` |
| `tools/sistemas/importa-discovery.sh` | Cópia única do discovery para `docs/sistemas/` |
| `tools/ws/tests/test_speckit_feature.sh`, `test_speckit_install.sh`, `test_importa_discovery.sh` | Testes novos |
| `.specify/`, `.claude/skills/speckit-*` | Gerados pelo `ws speckit` e versionados |
| `.specify/memory/constitution.md`, `AGENTS.md`, `docs/workspace.md`, `docs/adr/0001-*.md` | Conteúdo do harness |
| `docs/sistemas/` | Conhecimento do SP0 |
| `specs/001-*`, `specs/002-*`, `repos/industria-logistica.wms.awx.monorepo/…` | Migração do AWX |

**Tempo dos testes:** a suíte offline completa leva cerca de 15 min no Windows. Em cada task, rode só o arquivo dela. Os testes de rede do `ws speckit` levam cerca de 2 min cada e só rodam com `WS_TEST_REDE=1`.

---

### Task 1: Branch de trabalho e nova guarda do `ws push` (adendo 4)

**Arquivos:**
- Modificar: `tools/ws/lib/push.sh` (comentário e regex de `ws_guard_violations`)
- Testes: `tools/ws/tests/test_push.sh`

**Interfaces:**
- Consome: `ws_guard_violations <prefixo>` (já existe).
- Produz: a mesma função, com o conjunto novo de caminhos bloqueados. A Task 6 depende disso para enviar a alteração do `CLAUDE.md` do AWX.

- [ ] **Step 1: Criar a branch de trabalho do SP2**

```bash
cd /c/src/wms-workspace
git status --short   # esperado: vazio
tools/ws/ws start sp2-speckit
```

Esperado: `ws: branch sp2-speckit criada`.

- [ ] **Step 2: Mudar os testes da guarda em `tools/ws/tests/test_push.sh`**

Troque a função `test_guarda_recusa_cada_arquivo_de_harness` inteira por:

```bash
test_guarda_recusa_cada_arquivo_que_colide_com_o_harness() {
  fx_ready
  local f n=0
  for f in .specify/memory/constitution.md app/.specify/x specs/001/spec.md \
           .claude/skills/speckit-plan/SKILL.md sub/.claude/skills/SpecKit-x/SKILL.md; do
    n=$((n + 1))
    git checkout -q main
    git checkout -q -b "feat/g$n"
    ws_commit "repos/r1/$f" "x"
    assert_fails ws push
    assert_contains "$OUT" "GUARDA: repos/r1"
    assert_contains "$OUT" "$f"
  done
  assert_eq "$(git -C "$T/remotes/r1.git" for-each-ref --format=x refs/heads/feat | wc -l | tr -d ' ')" "0"
}

test_guarda_aceita_instrucoes_do_proprio_repo() {
  fx_ready
  ws start feat/a >/dev/null
  local f
  for f in CLAUDE.md sub/AGENTS.md .claude/rules/r.md .claude/agents/a.md \
           .claude/skills/qualidade-codigo/SKILL.md .github/copilot-instructions.md .github/agents/a.md; do
    ws_commit "repos/r1/$f" "x"
  done
  assert_ok ws push
  # ls-tree em vez de <ref>:<caminho>: o Git Bash converteria o ":" como lista de caminhos.
  assert_contains "$(git -C "$T/remotes/r1.git" ls-tree -r --name-only feat/a)" ".claude/rules/r.md"
}
```

Em `test_guarda_e_tudo_ou_nada`, troque `ws_commit repos/r2/CLAUDE.md "x"` por `ws_commit repos/r2/.specify/x "x"`.

Troque `test_guarda_recusa_arquivo_de_harness_trocado_por_symlink` inteira por:

```bash
test_guarda_recusa_arquivo_de_harness_trocado_por_symlink() {
  upstream_commit r1 .specify/memory/constitution.md "constitution antiga"
  fx_ready
  ws start feat/a >/dev/null
  local h
  h=$(echo "../fora" | git hash-object -w --stdin)
  git update-index --cacheinfo "120000,$h,repos/r1/.specify/memory/constitution.md"
  git commit -qm "troca a constitution por symlink"
  git checkout -q -- . 2>/dev/null || true
  git reset -q --hard
  assert_fails ws push
  assert_contains "$OUT" "GUARDA: repos/r1"
}
```

- [ ] **Step 3: Rodar e ver falhar**

Run: `bash tools/ws/tests/run.sh tools/ws/tests/test_push.sh`
Esperado: `17 ok, 1 falha(s)`. A falha é `test_guarda_aceita_instrucoes_do_proprio_repo`, com `GUARDA: repos/r1` citando `CLAUDE.md`. Os testes de recusa já passam, porque a guarda antiga bloqueia um conjunto maior.

- [ ] **Step 4: Mudar a guarda em `tools/ws/lib/push.sh`**

Troque o comentário acima de `ws_guard_violations` por:

```bash
# Arquivos que colidiriam com o harness e que a branch adiciona, altera, copia ou troca de tipo
# (ex.: por symlink) dentro do prefixo: .specify/, specs/ na raiz do repo e skills speckit-*
# (ADR 0001, adendo 4). CLAUDE.md, AGENTS.md e o resto de .claude/ e .github/ são instruções do
# próprio repo e passam. Um rename conta como A. Remoção é permitida.
```

E troque a linha do `grep -iE` dentro da função por:

```bash
    | grep -iE '(^|/)\.specify/|^specs/|(^|/)\.claude/skills/speckit-' \
```

- [ ] **Step 5: Rodar e ver passar**

Run: `bash tools/ws/tests/run.sh tools/ws/tests/test_push.sh`
Esperado: `18 ok, 0 falha(s)`.

- [ ] **Step 6: Commit**

```bash
git add tools/ws/lib/push.sh tools/ws/tests/test_push.sh
git commit -m "ws: guarda do push bloqueia só .specify/, specs/ e speckit-* (ADR 0001, adendo 4)"
```

---

### Task 2: Extensão `ws`: hooks `ws-feature.sh` e `ws-push.sh`

**Arquivos:**
- Criar: `tools/speckit/ws/extension.yml`, `tools/speckit/ws/commands/speckit.ws.feature.md`, `tools/speckit/ws/commands/speckit.ws.push.md`, `tools/speckit/ws/scripts/bash/ws-feature.sh`, `tools/speckit/ws/scripts/bash/ws-push.sh`
- Testes: `tools/ws/tests/test_speckit_feature.sh`

**Interfaces:**
- Consome: `tools/ws/ws start <branch>` e `tools/ws/ws push`. Nos testes, o `ws` é apontado pela variável `WS_BIN`.
- Produz:
  - `ws-feature.sh [--short-name "<nome>"] "<descrição>"`: imprime uma linha JSON `{"BRANCH_NAME","FEATURE_NUM","FEATURE_DIRECTORY","EXISTING":true|false,"ERROR"}` e sai com 0 se deu certo, 1 se falhou;
  - `ws-push.sh`: executa `ws push`;
  - os comandos `speckit.ws.feature` e `speckit.ws.push` e os hooks `before_specify` (obrigatório) e `after_converge` (opcional), usados pela Task 3.

- [ ] **Step 1: Escrever o teste que falha `tools/ws/tests/test_speckit_feature.sh`**

```bash
# Testes do hook ws-feature.sh e do ws-push.sh da extensão ws (spec SP2, 6.1).

FEATURE_SH="$WS_DIR/../speckit/ws/scripts/bash/ws-feature.sh"
PUSH_SH="$WS_DIR/../speckit/ws/scripts/bash/ws-push.sh"

# Roda o hook no workspace da fixture, com o ws de verdade.
feature() { WS_BIN="$WS_BIN" bash "$FEATURE_SH" "$@"; }

# Cria specs/<nome>/spec.md no main e envia ao origin.
mk_spec() {
  git checkout -q main
  ws_commit "specs/$1/spec.md" "# $1"
  git push -q origin main
}

# Valor de um campo do JSON de uma linha: json_get <campo> <json>
json_get() { printf '%s' "$2" | sed -E "s/.*\"$1\":(\"([^\"]*)\"|([a-z]+)).*/\2\3/"; }

test_feature_nova_com_specs_vazio_usa_001() {
  fx_ready
  assert_ok feature --short-name "cadastro de caixas" "Cadastrar caixas no picking"
  assert_eq "$(json_get BRANCH_NAME "$OUT")" "001-cadastro-de-caixas"
  assert_eq "$(json_get FEATURE_NUM "$OUT")" "001"
  assert_eq "$(json_get FEATURE_DIRECTORY "$OUT")" "specs/001-cadastro-de-caixas"
  assert_eq "$(json_get EXISTING "$OUT")" "false"
  assert_eq "$(json_get ERROR "$OUT")" ""
  assert_eq "$(git symbolic-ref --short HEAD)" "001-cadastro-de-caixas"
}

test_feature_nova_usa_o_proximo_numero() {
  fx_ready
  mk_spec 001-picking-b2c
  mk_spec 007-etiquetas
  assert_ok feature --short-name "nova coisa" "Uma coisa nova"
  assert_eq "$(json_get BRANCH_NAME "$OUT")" "008-nova-coisa"
}

test_feature_nova_sem_short_name_usa_a_descricao() {
  fx_ready
  assert_ok feature "Ajustar integração de expedição com transportadora"
  assert_eq "$(json_get BRANCH_NAME "$OUT")" "001-ajustar-integracao-de-expedicao"
}

test_feature_existente_pelo_numero_abre_revisao() {
  fx_ready
  mk_spec 002-sku-multiplo
  assert_ok feature --short-name "x" "Altera a 002: aceitar SKU sem código de barras"
  assert_eq "$(json_get BRANCH_NAME "$OUT")" "002-sku-multiplo-r1"
  assert_eq "$(json_get FEATURE_DIRECTORY "$OUT")" "specs/002-sku-multiplo"
  assert_eq "$(json_get EXISTING "$OUT")" "true"
}

test_feature_existente_pelo_nome_abre_revisao() {
  fx_ready
  mk_spec 002-sku-multiplo
  assert_ok feature "Mudar o sku-multiplo para aceitar SKU sem código"
  assert_eq "$(json_get BRANCH_NAME "$OUT")" "002-sku-multiplo-r1"
}

test_revisao_pula_branch_que_ja_existe_local_ou_no_origin() {
  fx_ready
  mk_spec 002-sku-multiplo
  git branch 002-sku-multiplo-r1
  git push -q origin main:refs/heads/002-sku-multiplo-r2
  assert_ok feature "Altera a 002"
  assert_eq "$(json_get BRANCH_NAME "$OUT")" "002-sku-multiplo-r3"
}

test_descricao_que_cita_duas_features_falha() {
  fx_ready
  mk_spec 001-a
  mk_spec 002-b
  assert_fails feature "Juntar a 001 com a 002"
  assert_contains "$(json_get ERROR "$OUT")" "mais de uma feature"
}

test_falha_do_ws_start_devolve_erro_e_nao_cria_pasta() {
  fx_ready
  echo x > sujo.txt
  assert_fails feature --short-name "algo" "Algo novo"
  assert_contains "$(json_get ERROR "$OUT")" "ws start 001-algo falhou"
  assert_contains "$(json_get ERROR "$OUT")" "mudanças não commitadas"
  assert_eq "$(json_get EXISTING "$OUT")" "false"
  [ ! -d specs ] || fail "não devia criar specs/"
}

test_descricao_vazia_falha() {
  fx_ready
  assert_fails feature
  assert_contains "$(json_get ERROR "$OUT")" "descrição da feature vazia"
}

test_saida_e_json_de_uma_linha_mesmo_com_aspas_no_erro() {
  fx_ready
  echo x > 'sujo "com aspas".txt'
  assert_fails feature --short-name "algo" "Algo"
  assert_eq "$(printf '%s\n' "$OUT" | wc -l | tr -d ' ')" "1"
  printf '%s' "$OUT" | python -c "import json,sys; json.load(sys.stdin)" || fail "JSON inválido: $OUT"
}

test_ws_push_sh_repassa_saida_e_codigo() {
  fx_ready
  assert_fails env WS_BIN="$WS_BIN" bash "$PUSH_SH"
  assert_contains "$OUT" "ws push não roda no main"
  ws start feat/a >/dev/null
  ws_commit repos/r1/src/app.txt "v2"
  assert_ok env WS_BIN="$WS_BIN" bash "$PUSH_SH"
  assert_contains "$OUT" "enviado repos/r1 -> feat/a"
}

test_numero_na_descricao_que_nao_e_feature_cria_feature_nova() {
  fx_ready
  mk_spec 001-picking-b2c
  assert_ok feature --short-name "caixas grandes" "Aceitar até 200 caixas por pedido"
  assert_eq "$(json_get BRANCH_NAME "$OUT")" "002-caixas-grandes"
  assert_eq "$(json_get EXISTING "$OUT")" "false"
}
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `bash tools/ws/tests/run.sh tools/ws/tests/test_speckit_feature.sh`
Esperado: `0 ok, 12 falha(s)`, com erros do tipo `No such file or directory` para `ws-feature.sh` e `ws-push.sh`.

- [ ] **Step 3: Escrever `tools/speckit/ws/scripts/bash/ws-feature.sh`**

```bash
#!/usr/bin/env bash
# Hook before_specify da extensão ws: cria a branch da feature com ws start (spec SP2, 4.1 e 4.2).
# Feature nova: branch NNN-<nome>. Feature já existente em specs/ (citada pelo número ou pelo nome):
# branch de revisão NNN-<nome>-r<k>, com k = próxima revisão livre, local e no origin.
# Uso: ws-feature.sh [--short-name "<nome curto>"] "<descrição>"
# Saída: uma linha JSON com BRANCH_NAME, FEATURE_NUM, FEATURE_DIRECTORY, EXISTING e ERROR.
set -uo pipefail

json_str() {
  local s=$1
  s=${s//\\/\\\\}
  s=${s//\"/\\\"}
  s=${s//$'\r'/}
  s=${s//$'\t'/ }
  s=${s//$'\n'/\\n}
  printf '"%s"' "$s"
}

# branch num pasta existente erro
emit() {
  printf '{"BRANCH_NAME":%s,"FEATURE_NUM":%s,"FEATURE_DIRECTORY":%s,"EXISTING":%s,"ERROR":%s}\n' \
    "$(json_str "$1")" "$(json_str "$2")" "$(json_str "$3")" "$4" "$(json_str "$5")"
}

fail() { emit "" "" "" false "$1"; exit 1; }

# texto -> até 4 palavras em minúsculas, sem acento, separadas por hífen
slugify() {
  # Troca uma a uma, byte a byte: o iconv do Git Bash translitera "ç" como "c?".
  printf '%s' "$1" | sed -e 's/á/a/g; s/à/a/g; s/â/a/g; s/ã/a/g; s/Á/a/g; s/À/a/g; s/Â/a/g; s/Ã/a/g' \
    -e 's/é/e/g; s/ê/e/g; s/É/e/g; s/Ê/e/g; s/í/i/g; s/Í/i/g' \
    -e 's/ó/o/g; s/ô/o/g; s/õ/o/g; s/Ó/o/g; s/Ô/o/g; s/Õ/o/g; s/ú/u/g; s/ü/u/g; s/Ú/u/g' \
    -e 's/ç/c/g; s/Ç/c/g' | tr '[:upper:]' '[:lower:]' \
    | tr -cs 'a-z0-9' ' ' | awk '{ n = (NF < 4 ? NF : 4); s = $1; for (i = 2; i <= n; i++) s = s "-" $i; print s }'
}

# Pastas specs/NNN-<nome> citadas na descrição, pelo número NNN ou pelo <nome>.
existing_features() {
  local lower d name num slug
  lower=$(printf '%s' "$desc" | tr '[:upper:]' '[:lower:]')
  for d in "$root"/specs/[0-9][0-9][0-9]-*/; do
    [ -d "$d" ] || continue
    name=$(basename "$d")
    num=${name%%-*}
    slug=${name#*-}
    if printf '%s' "$lower" | grep -Eq "(^|[^0-9])$num([^0-9]|$)" || [[ "$lower" == *"$slug"* ]]; then
      echo "$name"
    fi
  done
}

next_num() {
  local max=0 d n
  for d in "$root"/specs/[0-9][0-9][0-9]-*/; do
    [ -d "$d" ] || continue
    n=$(basename "$d")
    n=$((10#${n%%-*}))
    [ "$n" -le "$max" ] || max=$n
  done
  printf '%03d' $((max + 1))
}

branch_taken() {
  git show-ref --verify -q "refs/heads/$1" && return 0
  if git remote get-url origin >/dev/null 2>&1; then
    [ -z "$(git ls-remote origin "refs/heads/$1" 2>/dev/null)" ] || return 0
  fi
  return 1
}

short=""
while [ $# -gt 0 ]; do
  case "$1" in
    --short-name) short=${2:-}; shift 2 ;;
    --) shift; break ;;
    *) break ;;
  esac
done
desc="$*"
[ -n "$desc" ] || fail "descrição da feature vazia"
root=$(git rev-parse --show-toplevel 2>/dev/null) || fail "fora de um repo git"
cd "$root" || fail "não consegui entrar em $root"
ws_bin=${WS_BIN:-"$root/tools/ws/ws"}

found=$(existing_features)
if [ "$(printf '%s' "$found" | grep -c .)" -gt 1 ]; then
  fail "a descrição cita mais de uma feature existente: $(printf '%s' "$found" | tr '\n' ' ')"
fi

if [ -n "$found" ]; then
  name=$found
  existing=true
  k=1
  while branch_taken "$name-r$k"; do k=$((k + 1)); done
  branch="$name-r$k"
else
  existing=false
  slug=$(slugify "${short:-$desc}")
  [ -n "$slug" ] || fail "não consegui gerar um nome curto a partir de: ${short:-$desc}"
  name="$(next_num)-$slug"
  branch=$name
  ! branch_taken "$branch" || fail "a branch $branch já existe"
fi

out=$(bash "$ws_bin" start "$branch" 2>&1) || fail "ws start $branch falhou: $out"
emit "$branch" "${name%%-*}" "specs/$name" "$existing" ""
```

- [ ] **Step 4: Escrever `tools/speckit/ws/scripts/bash/ws-push.sh`**

```bash
#!/usr/bin/env bash
# Hook after_converge (opcional) e comando manual da extensão ws: envia a branch com ws push.
set -uo pipefail
root=$(git rev-parse --show-toplevel 2>/dev/null) || { echo "ws: erro: fora de um repo git" >&2; exit 1; }
cd "$root" || exit 1
exec bash "${WS_BIN:-$root/tools/ws/ws}" push
```

```bash
git add tools/speckit/ws/scripts/bash/*.sh
git update-index --chmod=+x tools/speckit/ws/scripts/bash/ws-feature.sh tools/speckit/ws/scripts/bash/ws-push.sh
```

- [ ] **Step 5: Rodar e ver passar**

Run: `bash tools/ws/tests/run.sh tools/ws/tests/test_speckit_feature.sh`
Esperado: `12 ok, 0 falha(s)`.

- [ ] **Step 6: Escrever o manifesto e os comandos da extensão**

`tools/speckit/ws/extension.yml`:

```yaml
schema_version: "1.0"

extension:
  id: ws
  name: "Workspace WMS multi-repo"
  version: "1.0.0"
  description: "Branch da feature com ws start e envio aos repos com ws push (spec SP2)"
  author: workspace-wms
  repository: https://dev.azure.com/ARECO/AReCO/_git/industria-logistica.wms.workspace
  license: Proprietary

requires:
  speckit_version: ">=1.0.12"

provides:
  commands:
    - name: speckit.ws.feature
      file: commands/speckit.ws.feature.md
      description: "Cria a branch da feature (nova ou revisão) com ws start"
    - name: speckit.ws.push
      file: commands/speckit.ws.push.md
      description: "Envia a branch da feature para os repos com ws push"

hooks:
  before_specify:
    command: speckit.ws.feature
    optional: false
    description: "Branch da feature com ws start"
  after_converge:
    command: speckit.ws.push
    optional: true
    prompt: "Enviar a branch para os repos com ws push? Rode antes /speckit-implement e /speckit-converge de novo se o converge acrescentou tarefas."
    description: "Envio da feature aos repos com ws push"

tags:
  - "workspace"
  - "multi-repo"
  - "git-subtree"
```

`tools/speckit/ws/commands/speckit.ws.feature.md`:

````markdown
---
description: "Cria a branch da feature (nova ou revisão) com ws start"
---

# Branch da feature no workspace

## User Input

```text
$ARGUMENTS
```

A entrada acima é a descrição da feature, a mesma que o `specify` recebeu.

1. Derive um nome curto de 2 a 4 palavras a partir da descrição, o mesmo que o `specify` usaria para a pasta.
2. Rode, na raiz do workspace:

   ```bash
   bash .specify/extensions/ws/scripts/bash/ws-feature.sh --short-name "<nome curto>" "<descrição>"
   ```

3. Leia a única linha JSON da saída:
   - **`ERROR` preenchido:** mostre o erro ao usuário e **pare**. Não crie pasta nem spec.
   - **`EXISTING` = `true`:** a descrição cita a feature de `FEATURE_DIRECTORY`. O `specify` deve editar essa spec (revisão de living spec), não criar outra.
   - **`EXISTING` = `false`:** é uma feature nova, em `FEATURE_DIRECTORY`.
4. Informe `BRANCH_NAME` e `FEATURE_DIRECTORY` e devolva o controle ao `specify`.
````

`tools/speckit/ws/commands/speckit.ws.push.md`:

````markdown
---
description: "Envia a branch da feature para os repos com ws push"
---

# Enviar a feature para os repos

## User Input

```text
$ARGUMENTS
```

1. **Tarefas pendentes:** se o último `/speckit-converge` acrescentou tarefas que ainda não foram implementadas no `tasks.md`, recomende rodar `/speckit-implement` e `/speckit-converge` de novo antes, e pergunte se o usuário quer seguir mesmo assim.
2. **Confirmação:** o push cria branches nos repos dos times. Confirme com o usuário antes de continuar.
3. **Envio:** rode, na raiz do workspace:

   ```bash
   bash .specify/extensions/ws/scripts/bash/ws-push.sh
   ```

   Mostre a saída.
4. **Se falhar:** mostre a mensagem do `ws` e pare. Não tente contornar a guarda nem rodar `git push` ou `git subtree` à mão.
5. **Se der certo:**
   - Liste os PRs a abrir no Azure DevOps, um por repo enviado. Cada PR cita `specs/NNN` e a revisão.
   - Lembre que os PRs são abertos e mergeados à mão, no fluxo de cada time.
   - Lembre que o PR do workspace é aberto depois que todos os PRs dos repos forem mergeados.
````

Esses três arquivos são testados na Task 3, na instalação real.

- [ ] **Step 7: Commit**

```bash
git add tools/speckit/ws tools/ws/tests/test_speckit_feature.sh
git commit -m "speckit: extensão ws com hooks de branch (ws start) e envio (ws push)"
```

---

### Task 3: Preset `multirepo` e comando `ws speckit`

**Arquivos:**
- Criar: `tools/speckit/VERSION`, `tools/speckit/multirepo/preset.yml`, `tools/speckit/multirepo/templates/spec-template.md`, `tools/speckit/multirepo/templates/plan-template.md`, `tools/speckit/multirepo/templates/tasks-template.md`, `tools/speckit/multirepo/commands/speckit.specify.md`, `tools/ws/lib/speckit.sh`
- Modificar: `tools/ws/ws` (novo comando `speckit`)
- Testes: `tools/ws/tests/test_speckit_install.sh`

**Interfaces:**
- Consome: a extensão da Task 2 (`tools/speckit/ws/`) e `ws_root`, `require_clean`, `log` e `die` de `common.sh`.
- Produz:
  - `ws_speckit`, chamada por `tools/ws/ws speckit`. Exige árvore limpa. Instala ou reinstala o Spec Kit, a extensão `ws`, a `agent-context` (com `context_files: [AGENTS.md]`) e o preset `multirepo`;
  - `WS_SPECKIT_SRC`: a pasta das fontes, com padrão `tools/speckit`, sobrescrevível nos testes.

- [ ] **Step 1: Escrever o teste que falha `tools/ws/tests/test_speckit_install.sh`**

```bash
# Testes do ws speckit (spec SP2, 6.3). Os que baixam o Spec Kit pela rede só rodam com
# WS_TEST_REDE=1; sem isso passam sem fazer nada e avisam na saída.

# Pula o teste quando a rede não foi liberada.
precisa_rede() {
  if [ "${WS_TEST_REDE:-}" != "1" ]; then
    echo "pulado: rode com WS_TEST_REDE=1"
    return 1
  fi
}

# Workspace da fixture com o Spec Kit instalado e commitado.
fx_speckit() {
  fx_ready
  ws_commit AGENTS.md "# regras do workspace"
  ws speckit >/dev/null
  git add -A
  git commit -qm "speckit"
}


test_speckit_sem_uvx_explica_como_instalar() {
  fx_ready
  local gitdir
  gitdir=$(dirname "$(command -v git)")
  assert_fails env PATH="$gitdir:/usr/bin" bash "$WS_BIN" speckit
  assert_contains "$OUT" "uvx não encontrado"
  [ ! -d .specify ] || fail "não devia criar .specify/"
}

test_speckit_com_versao_inexistente_nao_mexe_em_nada() {
  precisa_rede || return 0
  fx_ready
  assert_fails env WS_SPECKIT_SRC="$T/fake-speckit" bash -c "mkdir -p '$T/fake-speckit' && echo 0.0.0 > '$T/fake-speckit/VERSION' && bash '$WS_BIN' speckit"
  assert_contains "$OUT" "não consegui rodar o Spec Kit 0.0.0"
  [ ! -d .specify ] || fail "não devia criar .specify/"
}

test_speckit_instala_hooks_skills_e_preset() {
  precisa_rede || return 0
  fx_speckit
  local ext
  ext=$(cat .specify/extensions.yml)
  assert_contains "$ext" "before_specify:"
  assert_contains "$ext" "command: speckit.ws.feature"
  assert_contains "$ext" "after_converge:"
  assert_contains "$ext" "command: speckit.ws.push"
  [ -f .claude/skills/speckit-ws-feature/SKILL.md ] || fail "falta a skill speckit-ws-feature"
  [ -f .claude/skills/speckit-ws-push/SKILL.md ] || fail "falta a skill speckit-ws-push"
  assert_contains "$(cat .claude/skills/speckit-specify/SKILL.md)" "Regras do workspace multi-repo"
  assert_contains "$(cat .specify/extensions/agent-context/agent-context-config.yml)" "  - AGENTS.md"
  [ ! -d .specify/extensions/git ] || fail "a extensão git não devia estar instalada"
  assert_eq "$(cat AGENTS.md)" "# regras do workspace"
  assert_eq "$(cat CLAUDE.md)" "# harness"
  diff -r "$WS_DIR/../speckit/ws/scripts" .specify/extensions/ws/scripts || fail "scripts instalados divergem da fonte"
}

test_speckit_templates_resolvidos_tem_as_secoes_do_preset() {
  precisa_rede || return 0
  fx_speckit
  local spec plan tasks
  spec=$(bash .specify/scripts/bash/resolve-template.sh spec-template)
  plan=$(bash .specify/scripts/bash/resolve-template.sh plan-template)
  tasks=$(bash .specify/scripts/bash/resolve-template.sh tasks-template)
  assert_contains "$spec" "## Repos afetados *(obrigatório)*"
  assert_contains "$spec" "## Revisões"
  assert_contains "$plan" "## Plano por repo afetado"
  assert_contains "$tasks" "[workspace]"
  assert_contains "$tasks" "[repos/<repo>]"
}

test_speckit_de_novo_preserva_constitution_e_reinstala() {
  precisa_rede || return 0
  fx_speckit
  ws_commit .specify/memory/constitution.md "# Constitution do workspace"
  assert_ok ws speckit
  assert_eq "$(cat .specify/memory/constitution.md)" "# Constitution do workspace"
  assert_contains "$(cat .specify/extensions.yml)" "command: speckit.ws.feature"
  assert_contains "$(cat .specify/extensions/agent-context/agent-context-config.yml)" "  - AGENTS.md"
  assert_eq "$(grep -c '^  - AGENTS.md$' .specify/extensions/agent-context/agent-context-config.yml)" "1"
}

test_speckit_recusa_arvore_suja() {
  fx_ready
  echo x > sujo.txt
  assert_fails ws speckit
  assert_contains "$OUT" "mudanças não commitadas"
}
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `WS_TEST_REDE=1 bash tools/ws/tests/run.sh tools/ws/tests/test_speckit_install.sh`
Esperado: `0 ok, 6 falha(s)`, com `uso: ws <add|start|push|maintain>` porque o comando `speckit` ainda não existe.

- [ ] **Step 3: Escrever `tools/speckit/VERSION`**

```text
1.0.12
```

- [ ] **Step 4: Escrever o preset**

`tools/speckit/multirepo/preset.yml`:

```yaml
schema_version: "1.0"

preset:
  id: "multirepo"
  name: "Workspace WMS multi-repo"
  version: "1.0.0"
  description: "Repos afetados, plano e tasks por repo, e living spec por feature (spec SP2)"
  author: "workspace-wms"
  repository: "https://dev.azure.com/ARECO/AReCO/_git/industria-logistica.wms.workspace"
  license: "Proprietary"

requires:
  speckit_version: ">=1.0.12"

provides:
  templates:
    - type: "template"
      name: "spec-template"
      file: "templates/spec-template.md"
      description: "Seções Repos afetados e Revisões"
      strategy: "append"
    - type: "template"
      name: "plan-template"
      file: "templates/plan-template.md"
      description: "Plano por repo afetado"
      strategy: "append"
    - type: "template"
      name: "tasks-template"
      file: "templates/tasks-template.md"
      description: "Marcadores por repo e verificação por repo"
      strategy: "append"
    - type: "command"
      name: "speckit.specify"
      file: "commands/speckit.specify.md"
      description: "Regras do workspace: hook de branch, feature existente e Repos afetados"
      strategy: "wrap"

tags:
  - "workspace"
  - "multi-repo"
  - "living-spec"
```

`tools/speckit/multirepo/templates/spec-template.md` (é acrescentado ao template do núcleo, por isso começa com uma linha em branco):

```markdown

## Repos afetados *(obrigatório)*

<!--
  Um item por repo que muda, com o nome da pasta em repos/.
  Para contratos entre sistemas (endpoints HTTP, filas, tabelas, views ou procedures compartilhadas),
  consulte docs/sistemas/mapa-arquitetura.md e inclua também os repos consumidores afetados.
-->

- `repos/<repo>`: <o que muda neste repo>

## Revisões

<!-- Uma linha por revisão desta feature (living spec). A primeira versão não entra aqui. -->

| Data | Branch | Motivo |
|------|--------|--------|
```

`tools/speckit/multirepo/templates/plan-template.md`:

```markdown

## Plano por repo afetado

<!-- Repita a subseção para cada repo listado em "Repos afetados" da spec. -->

### `repos/<repo>`

- **Instruções do repo lidas:** <os que existirem entre CLAUDE.md, AGENTS.md, .github/copilot-instructions.md, docs/convencoes.md, docs/adr/ e docs/constitution.md>
- **Conhecimento de apoio:** `docs/sistemas/<repo>/`
- **Stack:** <linguagem, framework, versão>
- **Build e testes:** <comandos exatos, com as ferramentas do repo>
- **Mudanças:** <arquivos e componentes>
- **Contratos com outros sistemas:** <endpoints, filas e objetos de banco tocados, com os consumidores afetados segundo docs/sistemas/mapa-arquitetura.md; ou "nenhum">
```

`tools/speckit/multirepo/templates/tasks-template.md`:

```markdown

## Convenções multi-repo do workspace

- **Marcador de lugar:** cada tarefa leva, logo depois do ID, o marcador de onde a mudança acontece.
  - `[repos/<repo>]`: uma mudança dentro de um repo.
  - `[workspace]`: uma mudança fora de `repos/` (`docs/sistemas/`, `AGENTS.md`, ADR do harness, `tools/`).
- **Agrupamento:** as tarefas ficam agrupadas por repo, e cada grupo termina com a verificação daquele repo:
  - [ ] TNNN [repos/<repo>] Verificar build e testes do repo com as ferramentas dele (<comandos do plano>)
- **Envio:** as tarefas `[workspace]` vão só no PR do workspace. O `ws push` não as envia.
```

`tools/speckit/multirepo/commands/speckit.specify.md` (o Spec Kit troca `{CORE_TEMPLATE}` pelo comando do núcleo):

```markdown
---
description: "Specify com as regras do workspace WMS multi-repo"
---

## Regras do workspace multi-repo (preset multirepo)

Estas regras valem junto com as instruções abaixo e prevalecem sobre elas quando houver conflito.

1. **Hook de branch:** o hook `before_specify` (`speckit-ws-feature`) é obrigatório. Se o JSON dele trouxer `ERROR` preenchido, pare: não crie pasta nem spec.
2. **Pasta da feature:** use o `FEATURE_DIRECTORY` devolvido pelo hook como `SPECIFY_FEATURE_DIRECTORY`.
3. **Feature existente (`EXISTING` = `true`)** é uma revisão de living spec:
   - não copie o template de novo nem sobrescreva o `spec.md`;
   - edite o `spec.md` que já existe para refletir a mudança pedida;
   - atualize "Repos afetados";
   - acrescente em "Revisões" uma linha com a data de hoje, o `BRANCH_NAME` e o motivo;
   - grave `.specify/feature.json` apontando para essa pasta.
4. **Repos afetados** é obrigatório. Consulte `docs/sistemas/mapa-arquitetura.md` para achar os consumidores de contratos entre sistemas.

{CORE_TEMPLATE}
```

- [ ] **Step 5: Escrever `tools/ws/lib/speckit.sh`**

```bash
# ws speckit: instala ou atualiza o Spec Kit na raiz do workspace, com a extensão ws,
# a extensão agent-context e o preset multirepo (spec SP2, 6.3).
# A versão vem de tools/speckit/VERSION; o uvx roda o Spec Kit sem instalar nada global.

WS_SPECKIT_SRC=${WS_SPECKIT_SRC:-"$(cd "$(dirname "${BASH_SOURCE[0]}")/../../speckit" 2>/dev/null && pwd)"}

ws_speckit() {
  cd "$(ws_root)"
  require_clean
  [ -f "$WS_SPECKIT_SRC/VERSION" ] || die "não encontrei $WS_SPECKIT_SRC/VERSION"
  local ver got cfg
  ver=$(tr -d ' \r\n' < "$WS_SPECKIT_SRC/VERSION")
  command -v uvx >/dev/null 2>&1 \
    || die "uvx não encontrado. Instale o uv (https://docs.astral.sh/uv/getting-started/installation/; no Windows: winget install astral-sh.uv) e rode de novo"
  local -a spec=(uvx --from "git+https://github.com/github/spec-kit.git@v$ver" specify)

  # Confere a versão antes de mexer em qualquer arquivo.
  got=$("${spec[@]}" --version 2>/dev/null | awk '{ print $NF }' | tail -1) || true
  [ "$got" = "$ver" ] || die "não consegui rodar o Spec Kit $ver (obtido: ${got:-nada}); confira tools/speckit/VERSION"

  # init --force mantém uma .specify/memory/constitution.md que já existe.
  "${spec[@]}" init --here --force --non-interactive --integration claude --script sh >/dev/null \
    || die "specify init falhou"

  if [ -d .specify/extensions/ws ]; then
    "${spec[@]}" extension remove ws --force >/dev/null || die "não consegui remover a extensão ws"
  fi
  "${spec[@]}" extension add --dev "$WS_SPECKIT_SRC/ws" >/dev/null || die "não consegui instalar a extensão ws"

  if [ -d .specify/extensions/agent-context ]; then
    "${spec[@]}" extension remove agent-context --force --keep-config >/dev/null \
      || die "não consegui remover a extensão agent-context"
  fi
  "${spec[@]}" extension add agent-context >/dev/null || die "não consegui instalar a extensão agent-context"
  cfg=.specify/extensions/agent-context/agent-context-config.yml
  [ -f "$cfg" ] || die "não encontrei $cfg"
  sed -i 's/^context_files: \[\]$/context_files:\n  - AGENTS.md/' "$cfg"

  if [ -d .specify/presets/multirepo ]; then
    "${spec[@]}" preset remove multirepo >/dev/null || die "não consegui remover o preset multirepo"
  fi
  "${spec[@]}" preset add --dev "$WS_SPECKIT_SRC/multirepo" >/dev/null || die "não consegui instalar o preset multirepo"

  log "Spec Kit $ver instalado com a extensão ws, o agent-context e o preset multirepo"
  log "revise e faça commit de .specify/ e .claude/skills/"
}
```

- [ ] **Step 6: Acrescentar o comando no dispatcher `tools/ws/ws`**

O arquivo inteiro fica:

```bash
#!/usr/bin/env bash
# ws: fluxo do workspace multi-repo com git subtree --squash (ADR 0001).
# Uso: tools/ws/ws <add|start|push|maintain|speckit> [args]
set -euo pipefail
WS_LIB="$(cd "$(dirname "${BASH_SOURCE[0]}")/lib" && pwd)"
for f in "$WS_LIB"/*.sh; do source "$f"; done

cmd=${1:-}
[ $# -gt 0 ] && shift
case "$cmd" in
  add)      ws_add "$@" ;;
  start)    ws_start "$@" ;;
  push)     ws_push "$@" ;;
  maintain) ws_maintain "$@" ;;
  speckit)  ws_speckit "$@" ;;
  *)        die "uso: ws <add|start|push|maintain|speckit> [args]" ;;
esac
```

- [ ] **Step 7: Rodar e ver passar**

Run: `WS_TEST_REDE=1 bash tools/ws/tests/run.sh tools/ws/tests/test_speckit_install.sh`
Esperado: `6 ok, 0 falha(s)` (cerca de 10 min, porque cada teste baixa o Spec Kit pelo `uvx`, que usa cache).

Run: `bash tools/ws/tests/run.sh tools/ws/tests/test_speckit_install.sh`
Esperado: `6 ok, 0 falha(s)`, e os quatro testes de rede imprimem `pulado: rode com WS_TEST_REDE=1`.

Run: `bash tools/ws/tests/run.sh tools/ws/tests/test_manifest.sh`
Esperado: `10 ok, 0 falha(s)`. Confirma que `test_comando_desconhecido_mostra_uso` continua passando com a nova mensagem de uso.

- [ ] **Step 8: Commit**

```bash
git add tools/speckit/VERSION tools/speckit/multirepo tools/ws/lib/speckit.sh tools/ws/ws tools/ws/tests/test_speckit_install.sh
git commit -m "ws: comando speckit (Spec Kit fixado, extensão ws, agent-context e preset multirepo)"
```

---

### Task 4: Spec Kit instalado no workspace, constitution e `AGENTS.md`

**Arquivos:**
- Gerar: `.specify/`, `.claude/skills/speckit-*` (via `ws speckit`)
- Criar ou substituir: `.specify/memory/constitution.md`
- Substituir: `AGENTS.md`

**Interfaces:**
- Consome: `tools/ws/ws speckit` (Task 3).
- Produz:
  - as skills `/speckit-*`, `/speckit-ws-feature` e `/speckit-ws-push` no workspace;
  - a constitution e o `AGENTS.md` que as Tasks 6 e 8 usam.

- [ ] **Step 1: Instalar o Spec Kit no workspace**

```bash
cd /c/src/wms-workspace
tools/ws/ws speckit
git status --short | cut -c4- | cut -d/ -f1-3 | sort -u
```

Esperado: `ws: Spec Kit 1.0.12 instalado …`, com arquivos novos só em `.specify/` e `.claude/skills/`. `AGENTS.md` e `CLAUDE.md` ficam sem mudança.

- [ ] **Step 2: Conferir a instalação**

Run: `grep -A3 "before_specify:\|after_converge:" .specify/extensions.yml; ls .claude/skills | grep ws; ls .specify/extensions`
Esperado:
- os hooks `speckit.ws.feature` (`optional: false`) e `speckit.ws.push` (`optional: true`);
- as skills `speckit-ws-feature` e `speckit-ws-push`;
- as extensões `agent-context` e `ws`, sem a `git`.

- [ ] **Step 3: Escrever a constitution `.specify/memory/constitution.md`**

```markdown
# Constitution do workspace WMS

Vale para todos os repos em `repos/`. As regras de cada repo ficam nos arquivos de instrução dele e valem para o código daquele repo, subordinadas a esta constitution.

## Princípios

### I. Hierarquia
- A constitution e o `AGENTS.md` da raiz governam o que cruza repos e o jeito de trabalhar do agente.
- Dentro de `repos/<repo>/`, as instruções daquele repo valem para o código dele.
- Uma regra que vale para um único repo fica nele. Uma regra que vale para mais de um repo, ou que é sobre como o agente trabalha, fica no harness.
- Se uma regra do repo conflitar com esta constitution, o agente para e pergunta ao humano.

### II. Contratos entre sistemas
Mudar um endpoint HTTP, uma fila, ou uma tabela, view ou procedure compartilhada exige listar os consumidores afetados, com base em `docs/sistemas/mapa-arquitetura.md`, e incluí-los em "Repos afetados" da spec.

### III. Cada repo passa no próprio build e nos próprios testes
Com as ferramentas daquele repo. Uma feature só termina quando todos os repos afetados passam.

### IV. Decisão relevante vira ADR aprovado por humano
- No repo, se for só dele: `repos/<repo>/docs/adr/`.
- No harness, se cruzar repos ou tratar do harness: `docs/adr/`.

### V. Nada de segredo versionado
Segredos que já existem nos repos são só registrados. Nunca são copiados para specs, docs ou código novo.

### VI. Simplicidade
A menor mudança que atende a spec, sem refatoração fora do escopo.

## Governança

- Mudar esta constitution exige um PR no workspace aprovado por humano.
- Versão 1.0.0, ratificada em DATA_RATIFICACAO.
```

```bash
sed -i "s/DATA_RATIFICACAO/$(date +%F)/" .specify/memory/constitution.md
```

- [ ] **Step 4: Substituir o `AGENTS.md`**

```markdown
# Workspace WMS: instruções para agentes

Este repo é o workspace multi-repo do WMS (`docs/adr/0001-workspace-git-subtree.md`). O código de cada sistema fica em `repos/<repo>/`, um git subtree do repo no Azure DevOps. Todo o resto é o harness.
- **Uso humano:** `docs/workspace.md`.
- **Princípios:** `.specify/memory/constitution.md`.

## Hierarquia

- A constitution e este arquivo governam o que cruza repos e o jeito de trabalhar do agente.
- Dentro de `repos/<repo>/`, as instruções daquele repo valem para o código dele.
- Conflito entre uma regra do repo e a constitution: pare e pergunte ao humano.

## Regras

1. **Antes de mexer em `repos/<repo>/`, leia os arquivos de instrução dele que existirem:** `CLAUDE.md`, `AGENTS.md`, `.github/copilot-instructions.md`, `docs/convencoes.md`, `docs/adr/` e `docs/constitution.md`. Leia de forma explícita, sem contar com o carregamento automático.
2. **Fluxo do repo fora do workspace:** se uma instrução do repo descreve esse fluxo (por exemplo, usar o Spec Kit do próprio repo), no workspace vale o fluxo da raiz.
3. **Regra ou decisão nova:**
   - se vale só para um repo, grave no arquivo de instrução que ele já tem ou, se não houver nenhum, em `repos/<repo>/docs/convencoes.md`. ADR: `repos/<repo>/docs/adr/NNNN-<titulo>.md`;
   - o resto vai para o harness, na raiz.
4. **Proibido dentro de `repos/<repo>/`:** criar ou alterar `.specify/`, `specs/` na raiz do repo e `.claude/skills/speckit-*`. O `ws push` recusa a branch.
5. **Fluxo de trabalho:**
   - **feature:** o Spec Kit na raiz (seção abaixo);
   - **fora do Spec Kit:** `tools/ws/ws start <branch>`, commits, `tools/ws/ws push`, PR manual por repo;
   - **nunca:** `git push` para os repos, `git subtree` à mão ou `git pull` numa branch de trabalho.
6. **Os repos continuam independentes:** cada mudança em `repos/<repo>/` precisa passar no build e nos testes daquele repo, com as ferramentas dele.
7. **Conhecimento dos sistemas:**
   - `docs/sistemas/mapa-arquitetura.md`: quem fala com quem, por HTTP, filas e banco;
   - `docs/sistemas/<repo>/`: domínio, regras, arquitetura e integrações de cada repo.

## Features com o Spec Kit

- **Iniciar:** `/speckit-specify <descrição>`, para feature nova ou para mudar uma existente (cite o número ou o nome dela). O hook `speckit-ws-feature` cria a branch com `ws start`.
- **Seguir:** `/speckit-clarify` (se preciso), `/speckit-plan`, `/speckit-tasks`, `/speckit-analyze`, `/speckit-implement` e `/speckit-converge`.
- **Enviar:** depois do `converge`, o hook oferece `/speckit-ws-push`, que também pode ser rodado à mão. Só com confirmação do humano.
- **Onde ficam:** as specs ficam em `specs/NNN-<nome>/`, só no workspace. As tasks levam o marcador `[repos/<repo>]` ou `[workspace]`.
- **PRs:** abertos e mergeados à mão, um por repo. Depois vem o PR do workspace.
```

O `CLAUDE.md` continua sendo só `@AGENTS.md`.

- [ ] **Step 5: Conferir que um `ws speckit` de novo preserva o conteúdo**

```bash
git add -A && git commit -qm "wip: conteúdo do harness"
tools/ws/ws speckit
git status --short
```

Esperado: `git status` vazio. A reinstalação mantém a constitution e o `AGENTS.md` e regenera os mesmos arquivos. Se aparecer diferença, veja com `git diff`: só é aceitável uma reordenação sem efeito em `.specify/extensions.yml` ou nos registries, e ela entra no commit do Step 6.

- [ ] **Step 6: Commit**

```bash
git reset -q --soft HEAD~1
git add -A
git commit -m "harness: Spec Kit 1.0.12 instalado, constitution do workspace e AGENTS.md com a hierarquia"
```

---

### Task 5: `docs/sistemas/` a partir do discovery do SP0

**Arquivos:**
- Criar: `tools/sistemas/importa-discovery.sh`
- Testes: `tools/ws/tests/test_importa_discovery.sh`
- Gerar: `docs/sistemas/`

**Interfaces:**
- Consome: `C:\src\00-harness_big_brown_field\docs\discovery\` (somente leitura).
- Produz: `docs/sistemas/mapa-arquitetura.md`, os CSVs e `docs/sistemas/<repo>/`, citados no `AGENTS.md`, na constitution e nos templates do preset.

- [ ] **Step 1: Escrever o teste que falha `tools/ws/tests/test_importa_discovery.sh`**

```bash
# Testes do tools/sistemas/importa-discovery.sh (spec SP2, 6.4).

IMPORTA="$WS_DIR/../sistemas/importa-discovery.sh"

# Discovery falso em $T/disc: dois repos, um arquivo com segredo e pastas de trabalho.
fx_discovery() {
  local d="$T/disc"
  mkdir -p "$d/arquitetura" "$d/repos/a/domain" "$d/repos/a/tech" "$d/repos/a/_discovery" \
    "$d/repos/b/business" "$d/credentials"
  echo "# mapa" > "$d/arquitetura/mapa-arquitetura.md"
  echo "app,tipo" > "$d/arquitetura/filas.csv"
  echo "app,tipo,repo" > "$d/edges-consolidado.csv"
  echo "# glossário" > "$d/repos/a/domain/domain-glossary.md"
  echo "# arquitetura" > "$d/repos/a/tech/current-architecture.md"
  echo "# readme" > "$d/repos/a/project-readme.md"
  echo "app,tipo" > "$d/repos/a/_discovery/edges.csv"
  echo "# estado" > "$d/repos/a/_discovery/discovery-state.md"
  echo 'Server=x;User ID=sa;Password=segredo' > "$d/repos/b/business/conexao.md"
  echo "# fluxo" > "$d/repos/b/business/workflow.md"
  echo "senha" > "$d/credentials/DatabaseReadOnly.txt"
}

test_importa_copia_o_esperado() {
  fx_discovery
  assert_ok bash "$IMPORTA" "$T/disc"
  local s=docs/sistemas
  local f
  for f in mapa-arquitetura.md filas.csv edges-consolidado.csv a/domain/domain-glossary.md \
           a/tech/current-architecture.md a/project-readme.md a/edges.csv b/business/workflow.md; do
    [ -f "$s/$f" ] || fail "faltou $s/$f"
  done
  [ ! -e "$s/a/_discovery" ] || fail "não devia copiar _discovery/"
  [ ! -e "$s/a/discovery-state.md" ] || fail "não devia copiar discovery-state.md"
  [ ! -e "$s/credentials" ] || fail "não devia copiar credentials/"
  assert_contains "$OUT" "copiados: 8 arquivo(s)"
}

test_importa_recusa_e_lista_arquivo_com_segredo() {
  fx_discovery
  assert_ok bash "$IMPORTA" "$T/disc"
  [ ! -e docs/sistemas/b/business/conexao.md ] || fail "copiou arquivo com segredo"
  assert_contains "$OUT" "recusados por padrão de segredo (1):"
  assert_contains "$OUT" "repos/b/business/conexao.md"
}

test_importa_e_unica() {
  fx_discovery
  bash "$IMPORTA" "$T/disc" >/dev/null
  assert_fails bash "$IMPORTA" "$T/disc"
  assert_contains "$OUT" "já existe; a importação é única"
}

test_importa_recusa_pasta_errada() {
  mkdir -p "$T/errada"
  assert_fails bash "$IMPORTA" "$T/errada"
  assert_contains "$OUT" "não parece a pasta docs/discovery"
  [ ! -e docs/sistemas ] || fail "não devia criar docs/sistemas"
}
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `bash tools/ws/tests/run.sh tools/ws/tests/test_importa_discovery.sh`
Esperado: `0 ok, 4 falha(s)`, com `No such file or directory` para `importa-discovery.sh`.

- [ ] **Step 3: Escrever `tools/sistemas/importa-discovery.sh`**

```bash
#!/usr/bin/env bash
# Cópia única do conhecimento do discovery do SP0 para docs/sistemas/ (spec SP2, 6.4).
# Uso: tools/sistemas/importa-discovery.sh <pasta docs/discovery de origem>
# Copia arquitetura/*, os edges-*.csv da raiz e, de cada repos/<repo>/, domain/, business/, tech/,
# project-readme.md e _discovery/edges.csv. Recusa arquivos com padrão de segredo e lista os recusados.
set -euo pipefail

SEGREDO='(password|pwd)[[:space:]]*=|user id=[^;]*;[[:space:]]*password|BEGIN [A-Z ]*PRIVATE KEY'

src=${1:-}
[ -n "$src" ] || { echo "uso: importa-discovery.sh <pasta docs/discovery>" >&2; exit 2; }
[ -d "$src/repos" ] && [ -d "$src/arquitetura" ] \
  || { echo "erro: $src não parece a pasta docs/discovery (faltam repos/ ou arquitetura/)" >&2; exit 1; }
root=$(git rev-parse --show-toplevel)
dst="$root/docs/sistemas"
[ ! -e "$dst" ] || { echo "erro: $dst já existe; a importação é única" >&2; exit 1; }

copiados=0
recusados=()

# origem destino-relativo-a-docs/sistemas
copia() {
  if grep -qiE "$SEGREDO" "$1"; then
    recusados+=("${1#"$src"/}")
    return 0
  fi
  mkdir -p "$(dirname "$dst/$2")"
  cp "$1" "$dst/$2"
  copiados=$((copiados + 1))
}

mkdir -p "$dst"
for f in "$src"/arquitetura/* "$src"/edges-*.csv; do
  [ -f "$f" ] && copia "$f" "$(basename "$f")"
done
for r in "$src"/repos/*/; do
  repo=$(basename "$r")
  for sub in domain business tech; do
    [ -d "$r$sub" ] || continue
    while IFS= read -r -d '' f; do
      copia "$f" "$repo/${f#"$r"}"
    done < <(find "$r$sub" -type f -print0)
  done
  [ -f "${r}project-readme.md" ] && copia "${r}project-readme.md" "$repo/project-readme.md"
  [ -f "${r}_discovery/edges.csv" ] && copia "${r}_discovery/edges.csv" "$repo/edges.csv"
done

echo "copiados: $copiados arquivo(s) para docs/sistemas/"
if [ ${#recusados[@]} -gt 0 ]; then
  echo "recusados por padrão de segredo (${#recusados[@]}):"
  printf '  %s\n' "${recusados[@]}"
fi
```

```bash
git add tools/sistemas/importa-discovery.sh
git update-index --chmod=+x tools/sistemas/importa-discovery.sh
```

- [ ] **Step 4: Rodar e ver passar**

Run: `bash tools/ws/tests/run.sh tools/ws/tests/test_importa_discovery.sh`
Esperado: `4 ok, 0 falha(s)`.

- [ ] **Step 5: Importar o discovery real**

Run: `tools/sistemas/importa-discovery.sh /c/src/00-harness_big_brown_field/docs/discovery`
Esperado: `copiados: 177 arquivo(s) para docs/sistemas/`, sem linha de recusados. A contagem é a da validação prévia; se mudar, confira se o discovery mudou. Se houver recusados, **não** edite os arquivos para contornar o filtro: registre a lista na mensagem de commit e siga.

Run: `ls docs/sistemas | head; ls docs/sistemas | wc -l`
Esperado: `mapa-arquitetura.md`, os CSVs e 17 pastas de repo.

- [ ] **Step 6: Commit**

```bash
git add tools/sistemas tools/ws/tests/test_importa_discovery.sh docs/sistemas
git commit -m "harness: docs/sistemas com o conhecimento do discovery do SP0"
```

---

### Task 6: Migração do AWX (Spec Kit para a raiz; instruções ficam subordinadas)

**Pare antes do Step 6 e peça OK explícito do usuário.** O `ws push` cria uma branch no repo do time do AWX.

**Arquivos:**
- Mover: `repos/industria-logistica.wms.awx.monorepo/specs/001-picking-b2c-consumer` para `specs/001-picking-b2c-consumer`, e `…/specs/002-sku-multiplo-codigo-barra` para `specs/002-sku-multiplo-codigo-barra`
- Mover: `repos/industria-logistica.wms.awx.monorepo/.specify/memory/constitution.md` para `repos/industria-logistica.wms.awx.monorepo/docs/constitution.md`
- Remover: `repos/industria-logistica.wms.awx.monorepo/.specify/` e `repos/industria-logistica.wms.awx.monorepo/.claude/skills/speckit-*`
- Modificar: `repos/industria-logistica.wms.awx.monorepo/CLAUDE.md` (linha 7 e seção "Precedência")

**Interfaces:**
- Consome: a guarda da Task 1 (a alteração no `CLAUDE.md` do AWX passa a ser permitida) e `specs/` na raiz, onde a Task 2 numera as features.
- Produz: `specs/001` e `specs/002` na raiz, fazendo com que a próxima feature nova receba `003` (conferido na Task 8).

- [ ] **Step 1: Mover as specs e a constitution**

```bash
cd /c/src/wms-workspace
A=repos/industria-logistica.wms.awx.monorepo
mkdir -p specs "$A/docs"
git mv "$A/specs/001-picking-b2c-consumer" specs/
git mv "$A/specs/002-sku-multiplo-codigo-barra" specs/
git mv "$A/.specify/memory/constitution.md" "$A/docs/constitution.md"
git rm -rq "$A/.specify" "$A"/.claude/skills/speckit-*
ls "$A/.claude/skills"
```

Esperado: só `qualidade-codigo` em `.claude/skills`.

- [ ] **Step 2: Ajustar o `CLAUDE.md` do AWX**

Na linha 7, troque `@.specify/memory/constitution.md` por `@docs/constitution.md`.

Logo depois do parágrafo que termina em "onde as coisas estão e como rodá-las." (fim da seção "Precedência"), acrescente:

```markdown

No workspace WMS (`industria-logistica.wms.workspace`), a constitution e o `AGENTS.md` da raiz do workspace
valem antes desta lista para o que cruza repos, e as specs ficam em `specs/` na raiz do workspace.
```

- [ ] **Step 3: Procurar outras referências à maquinaria removida**

Run: `grep -rn "\.specify/\|speckit" repos/industria-logistica.wms.awx.monorepo --include=*.md | grep -v "^repos/industria-logistica.wms.awx.monorepo/docs/constitution.md"`
Esperado: nenhuma linha. Se aparecer alguma (fora da constitution, que fica como está), troque o caminho pelo novo equivalente: `docs/constitution.md` ou `specs/` na raiz do workspace.

- [ ] **Step 4: Conferir a guarda antes de enviar e fazer commit**

```bash
git add -A
git commit -m "harness: migra o Spec Kit do AWX para a raiz (specs 001 e 002, constitution em docs/)"
bash -c 'for f in tools/ws/lib/*.sh; do source $f; done; ws_guard_violations repos/industria-logistica.wms.awx.monorepo'
```

Esperado: o commit é criado, e a última linha não imprime nada.

- [ ] **Step 5: Pedir OK ao usuário e enviar o AWX**

Com o OK:

```bash
tools/ws/ws push
```

Esperado: `ws: enviado repos/industria-logistica.wms.awx.monorepo -> sp2-speckit`. Nenhum outro repo aparece.

- [ ] **Step 6: Conferir a branch no remoto do AWX**

```bash
git ls-remote https://dev.azure.com/ARECO/AReCO/_git/industria-logistica.wms.awx.monorepo refs/heads/sp2-speckit
git diff --stat main...sp2-speckit -- repos/industria-logistica.wms.awx.monorepo | tail -3
```

Esperado: a primeira linha mostra a branch. A segunda resume o que foi enviado: `CLAUDE.md`, `docs/constitution.md` novo e as remoções de `.specify/`, `.claude/skills/speckit-*` e `specs/`.

Diga ao usuário para abrir o PR `sp2-speckit` no AWX, à mão.

---

### Task 7: Docs do workspace e adendo 4 da ADR

**Arquivos:**
- Modificar: `C:\src\00-harness_big_brown_field\docs\adr\0001-workspace-git-subtree.md` (adendo 4) e a cópia `docs/adr/0001-workspace-git-subtree.md`
- Modificar: `docs/workspace.md`

**Interfaces:**
- Consome: as decisões das Tasks 1 a 6.
- Produz: a documentação que o humano lê.

- [ ] **Step 1: Escrever o adendo 4 na ADR da pasta de discovery**

Acrescente no fim da seção 4, depois do adendo 3:

```markdown

**Adendo 4 (SP2, 2026-09-29):** os repos mantêm as instruções de agente que já têm, subordinadas ao harness do workspace. A constitution e o `AGENTS.md` da raiz governam o que cruza repos; dentro de `repos/<repo>/`, valem as instruções daquele repo.
- **Na seção 2:** os arquivos de instrução de um repo são `CLAUDE.md`, `AGENTS.md`, `.github/copilot-instructions.md`, `docs/convencoes.md`, `docs/adr/` e `docs/constitution.md`. `docs/convencoes.md` só é criado quando o repo não tem nenhum dos outros.
- **Guarda do `ws push`:** bloqueia adicionar, alterar ou trocar o tipo apenas de `.specify/`, `specs/` na raiz do repo e `.claude/skills/speckit-*`, que colidiriam com o Spec Kit da raiz. O resto passa, e a remoção é permitida.
- **Seção 5:** só a maquinaria de Spec Kit do AWX sai do repo. As specs `001` e `002` vão para `specs/` na raiz, e a constitution do AWX vai para `docs/constitution.md` do próprio repo. O Fly e o servidor.backend não mudam.
- **Spec:** `docs/superpowers/specs/2026-09-28-sp2-speckit-multirepo-design.md`.
```

- [ ] **Step 2: Copiar a ADR para o workspace**

```bash
cp /c/src/00-harness_big_brown_field/docs/adr/0001-workspace-git-subtree.md docs/adr/
```

- [ ] **Step 3: Atualizar as regras em `docs/workspace.md`**

Troque o item que começa com "- Dentro de `repos/<repo>/`, não crie nem altere" por:

```markdown
- Dentro de `repos/<repo>/`, não crie nem altere `.specify/`, `specs/` (na raiz do repo) e `.claude/skills/speckit-*`: eles colidiriam com o Spec Kit da raiz. O `ws push` recusa a branch inteira. `CLAUDE.md`, `AGENTS.md`, o resto de `.claude/` e `.github/` são instruções do próprio repo e podem ser editados. Remover é permitido.
```

Troque o item que começa com "- Regra ou decisão que vale só para um repo" por:

```markdown
- Regra ou decisão que vale só para um repo: vai no arquivo de instrução que ele já tem (`CLAUDE.md`, `AGENTS.md`, `.github/copilot-instructions.md`, `docs/constitution.md`) ou, se não tiver nenhum, em `repos/<repo>/docs/convencoes.md`. ADRs em `repos/<repo>/docs/adr/`. O resto fica no harness, na raiz.
```

- [ ] **Step 4: Acrescentar ao `docs/workspace.md` as seções do Spec Kit**

Logo antes de `## Regras`:

```markdown
## Features com o Spec Kit

1. `/speckit-specify <descrição>`: o hook cria a branch com `ws start` e a spec em `specs/NNN-<nome>/`. Para mudar uma feature que já existe, cite o número ou o nome dela: a branch vira `NNN-<nome>-r<k>` e a spec é editada, não recriada.
2. `/speckit-clarify` (se preciso), `/speckit-plan`, `/speckit-tasks`, `/speckit-analyze`, `/speckit-implement` e `/speckit-converge`.
3. Depois do `converge`, o agente oferece `/speckit-ws-push` (também dá para rodar à mão, ou `tools/ws/ws push`).
4. Os PRs seguem o fluxo acima: um por repo, abertos e mergeados à mão, e depois o PR do workspace.

Specs em `specs/` ficam só no workspace. Conhecimento dos sistemas: `docs/sistemas/`.

## Spec Kit: instalar e atualizar

- A versão fica em `tools/speckit/VERSION`. O que o Spec Kit gera (`.specify/`, `.claude/skills/speckit-*`) é versionado, e quem só clona não precisa de mais nada.
- **Para atualizar:**
  1. troque o `VERSION`;
  2. rode `tools/ws/ws speckit` (precisa do `uv`: `winget install astral-sh.uv`);
  3. rode `WS_TEST_REDE=1 bash tools/ws/tests/run.sh tools/ws/tests/test_speckit_install.sh`;
  4. valide um `/speckit-specify` de ponta a ponta;
  5. abra um PR no workspace.
- A fonte da extensão `ws` e do preset `multirepo` fica em `tools/speckit/`. Nunca edite as cópias em `.specify/`: rode `ws speckit` de novo.
```

Na seção `## Testes do tools/ws`, acrescente a linha:

```markdown
WS_TEST_REDE=1 bash tools/ws/tests/run.sh tools/ws/tests/test_speckit_install.sh   # instala o Spec Kit de verdade (rede)
```

- [ ] **Step 5: Conferir as referências**

Run: `grep -o '/speckit-[a-z-]*' AGENTS.md docs/workspace.md | sort -u | cut -d: -f2 | sort -u; ls .claude/skills`
Esperado: todos os `/speckit-*` citados existem como pasta em `.claude/skills`.

- [ ] **Step 6: Commit**

```bash
git add docs/adr docs/workspace.md
git commit -m "docs: Spec Kit no workspace e adendo 4 da ADR 0001"
```

---

### Task 8: Validação de ponta a ponta com o agente (manual, com o usuário)

Os hooks do Spec Kit são instruções para o agente e não dá para testá-los em script. Esta task é um checklist que o usuário roda numa sessão própria do Claude Code. O executor prepara o ambiente e registra o resultado.

**Arquivos:** nenhum no workspace. O resultado vai para `C:\src\00-harness_big_brown_field\docs\discovery\sp2-validacao.md`.

- [ ] **Step 1: Preparar um origin e um clone descartáveis**

```bash
cd /c/src
git clone -q --bare /c/src/wms-workspace /c/src/wms-e2e-origin.git
git -C /c/src/wms-e2e-origin.git update-ref refs/heads/main refs/heads/sp2-speckit
git clone -q -c core.longpaths=true -c core.autocrlf=false /c/src/wms-e2e-origin.git /c/src/wms-workspace-e2e
git -C /c/src/wms-workspace-e2e log -1 --oneline
```

Esperado: o último commit do clone é o topo da `sp2-speckit`.
- **Por que o `main` descartável recebe a `sp2-speckit`:** o hook roda `ws start`, que volta para o `main`. Sem o SP2 no `main`, a branch da feature nasceria sem o Spec Kit.
- **Para onde vão os pushes:** os do `ws start` vão para o origin descartável.
- **Os repos reais:** são só lidos (`ls-remote`/`fetch`). O `ws push` **não** é rodado nesta validação.

- [ ] **Step 2: Pedir ao usuário para rodar o checklist**

Abrir o Claude Code em `C:\src\wms-workspace-e2e` e seguir:

1. `/speckit-specify` com uma feature de teste que toque dois repos, por exemplo: "Registrar no picking.backend e no servidor.backend a data de conferência de caixa".
2. **Conferir:** o agente rodou `speckit-ws-feature` antes de tudo, a branch é `003-…` e existe `specs/003-…/spec.md` com "Repos afetados" listando os dois repos.
3. **Conferir:** com a árvore suja (um arquivo qualquer não commitado), um novo `/speckit-specify` para e não cria spec.
4. `/speckit-plan` e `/speckit-tasks`. **Conferir:** há uma seção por repo no plano, e as tasks têm `[repos/…]` e a verificação por repo.
5. `/speckit-implement` e `/speckit-converge` numa mudança mínima. **Conferir:** no fim, o agente oferece `/speckit-ws-push` e pede confirmação. **Responder não.**
6. `/speckit-specify` citando "a 003" com uma mudança. **Conferir:** a branch é `003-…-r1`, o `spec.md` foi editado e não recriado, e "Revisões" ganhou uma linha.

- [ ] **Step 3: Registrar o resultado**

Escrever `C:\src\00-harness_big_brown_field\docs\discovery\sp2-validacao.md` com cada item: ok ou falhou, mais a observação do usuário. Para cada falha, abrir um item de correção no preset ou nos comandos e repetir o item depois de corrigir.

- [ ] **Step 4: Apagar o clone descartável**

```bash
cd /c/src && rm -rf wms-workspace-e2e wms-e2e-origin.git
```

---

### Task 9: Suíte completa e fechamento

- [ ] **Step 1: Suíte completa offline**

Run: `bash tools/ws/tests/run.sh`
Esperado: `87 ok, 0 falha(s)`, com os testes de rede pulados (cerca de 15 min).

- [ ] **Step 2: Testes de rede**

Run: `WS_TEST_REDE=1 bash tools/ws/tests/run.sh tools/ws/tests/test_speckit_install.sh`
Esperado: `6 ok, 0 falha(s)`.

- [ ] **Step 3: Registrar na pasta de discovery**

Em `C:\src\00-harness_big_brown_field\docs\discovery\estado-da-sessao.md`, na seção do SP2, registrar:
- as tasks concluídas;
- o PR do AWX a abrir;
- o resultado da validação;
- que o `main` do workspace ainda não recebeu o SP2.

- [ ] **Step 4: Perguntar ao usuário como fechar**

O fechamento publica o workspace e depende dele:
- **Opção 1:** push da branch `sp2-speckit` para o origin do workspace e PR manual no Azure DevOps, depois que o PR do AWX for mergeado.
- **Opção 2:** merge local no `main` e push, como no SP1.

Não publique nada sem a resposta.

---

## Autorrevisão (feita ao escrever o plano)

| Item da spec | Task |
|---|---|
| 1. Critérios 1 a 5 | 2 e 3 (hooks e preset), 8 (ponta a ponta), 6 (AWX) |
| 3. Estrutura | 3, 4 e 5 |
| 4.1 Fluxo de feature nova | 2, 3 e 4; validado na 8 |
| 4.2 Living spec por feature (revisão `-r<k>`, sem sobrescrever) | 2 (branch) e 3 (wrap do `specify`); validado na 8, item 6 |
| 4.3 Specs só no workspace | guarda da Task 1 (`specs/` bloqueado nos prefixos) |
| 5.1 Constitution | 4 |
| 5.2 e 5.3 Arquivos de instrução e `AGENTS.md` | 4 |
| 5.4 Migração por repo | 6 (AWX); Fly e servidor não mudam |
| 5.5 Adendo 4 (guarda) | 1 e 7 |
| 6.1 a 6.4 Componentes | 2, 3 e 5 |
| 7. Erros | 2 (JSON com `ERROR`, revisão, feature inexistente), 3 (`uv` ausente, versão inexistente), 5 (segredos) |
| 8. Testes | 1, 2, 3, 5 e 8 |
| 10. Riscos | Foco da revisão, itens 1 e 3; validação manual na 8 |
