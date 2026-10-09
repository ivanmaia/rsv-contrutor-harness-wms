# SP1: Workspace multi-repo com git subtree — plano de implementação

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Objetivo:** criar o repo do workspace WMS, com os 17 repos como git subtree `--squash` em `repos/<repo>/` e os scripts `tools/ws/ws` (`add`, `start`, `push`, `maintain`) que implementam o fluxo da ADR 0001.

**Arquitetura:** um dispatcher bash (`tools/ws/ws`) carrega uma lib por comando (`tools/ws/lib/*.sh`). O único arquivo de configuração é o manifesto `workspace.repos`. Os testes usam repos bare locais numa pasta temporária, com um runner bash próprio, sem dependências. A raiz do workspace guarda o harness (`AGENTS.md`, `CLAUDE.md`, `docs/`); os prefixos guardam só o conteúdo de cada repo.

**Stack:** bash (Git Bash do Git for Windows), git ≥ 2.40 com `git subtree` (validado com 2.54.0.windows.1), awk, grep. Nada mais.

**Spec:** `C:\src\00-harness_big_brown_field\docs\adr\0001-workspace-git-subtree.md` (aceita em 2026-09-24). Evidência: `C:\src\00-harness_big_brown_field\poc\sp1-subtree\`.

**Onde:** repo novo em `C:\src\wms-workspace` (`/c/src/wms-workspace` no Git Bash). A pasta de discovery não é o workspace. Todos os caminhos abaixo são relativos à raiz do workspace, salvo indicação.

**Validação prévia:** o código e os testes deste plano foram rodados em uma cópia descartável antes de o plano ser escrito: 44 testes passando no Windows, com Git 2.54.

## Restrições globais

- Os repos continuam independentes: PRs, pipelines e times não mudam.
- Cada repo entra como `git subtree` com `--squash`, sempre, no prefixo `repos/<nome-completo-do-repo>/` (1:1 com o nome do repo remoto).
- Manifesto `workspace.repos`: uma linha por repo, `prefixo url branch-base`; é a única fonte de configuração dos scripts.
- Clone do workspace com `core.longpaths=true` e `core.autocrlf=false`.
- O base do workspace é `main`; o branch-base de cada repo vem do manifesto (hoje `main` nos 17).
- O harness fica só na raiz. Dentro de um prefixo, a branch não pode **adicionar ou alterar** `CLAUDE.md`, `AGENTS.md`, `.claude/`, `.specify/`, `specs/`, `.github/copilot-instructions.md` e `.github/agents/`. Remover pode (migração da seção 5 da ADR).
- Limite de rejoin: 100 commits desde o último marcador de split do prefixo (`WS_REJOIN_THRESHOLD`).
- Mensagens dos scripts, comentários e docs em português.
- Nada toca o Azure DevOps antes da Task 8, e a Task 8 só começa com o OK explícito do usuário.

## Desvio da ADR descoberto na validação

A ADR (seção 4) manda rodar `git subtree split --rejoin --squash` nos prefixos acima do limite. A validação mostrou que, num prefixo **sem mudança local** desde o último squash, esse comando não grava nada: gasta o split inteiro (cerca de 0,28 s por commit do workspace no Windows) e não cria marcador. Com 17 repos, quase todos parados na maior parte do tempo, cada `ws start` repetiria esse custo, e o primeiro `ws push` de um repo parado há muito tempo ficaria lento.

O plano resolve assim: se a tree do prefixo é igual à do último commit de squash, o `ws maintain` grava ele mesmo o commit que o rejoin gravaria (um merge do HEAD com esse squash, sem mudar a tree, com os trailers `git-subtree-dir`, `git-subtree-mainline` e `git-subtree-split`). Se o prefixo mudou, roda o `split --rejoin --squash` normal, passando a URL do repo para que o git busque o commit citado no squash quando ele não está no clone. Medido: split de um prefixo parado depois de 100 commits caiu de 28 s para 2 s, e `subtree pull`, `split` e `push` seguintes continuam corretos (testes das Tasks 3 e 6). Esse formato de commit é o que o `git subtree` lê em `find_existing_splits` e `find_latest_squash`. Se uma versão futura do git mudar isso, os testes da Task 3 acusam.

**Correção na execução (revisão final, achado C1):** o ramo "se o prefixo mudou, roda o `split --rejoin --squash` normal" foi removido. Um rejoin de verdade grava no `main` um commit de split que só existe no clone local, e isso quebra o `subtree pull` e o `push` desse prefixo nos outros clones. O `ws maintain` agora adia o marcador até o prefixo voltar a ser igual ao último squash, o que acontece no próximo `ws start`. Ver o adendo 2 da ADR.

## Foco da revisão

Entradas e condições que a ADR implica e que mais podem dar errado; cada uma tem teste na task indicada:

1. **Arquivo de agente removido de um repo** (migração da seção 5): o `ws push` precisa aceitar. Recusar travaria a migração. Task 5, `test_guarda_permite_remover_arquivo_de_agente`.
2. **Prefixo parado por muito tempo**: o `ws start` não pode rodar um split longo a cada vez, e o push seguinte tem de continuar correto. Task 3, `test_maintain_marca_prefixo_intocado_sem_rodar_split`.
3. **Conflito no `subtree pull`**: o `ws start` para, sem criar a branch e sem enviar o `main`. Task 4, `test_start_para_no_conflito_sem_criar_branch_nem_enviar_main`.
4. **Clone novo do workspace** (sem os commits dos repos no object store): `start` e `push` funcionam. Task 6, `test_clone_novo_do_workspace_faz_start_e_push`. No Azure DevOps real isso depende de fetch por SHA, verificado na Task 8.
5. **Manifesto salvo com CRLF** por um editor no Windows: tem de funcionar igual. Task 1, `test_manifest_tolera_crlf`.

## Fora deste plano

- Migração dos arquivos de agente de `wms.awx.monorepo`, Fly e `wms.servidor.backend` (seção 5 da ADR): o destino das skills e do Spec Kit é definido no SP2, e o plano do SP2 faz a migração.
- Constitution do workspace (`.specify/memory/constitution.md`): SP2.
- `docs/convencoes.md` nos repos: sob demanda, no uso.

## Estrutura de arquivos

| Arquivo | Responsabilidade |
|---|---|
| `workspace.repos` | Manifesto: `prefixo url branch-base` por repo |
| `tools/ws/ws` | Dispatcher: carrega as libs e chama `ws_<comando>` |
| `tools/ws/lib/common.sh` | `log`, `die`, `ws_root`, `ws_manifest`, `ws_url_of`, `require_clean`, `current_branch`, `has_origin`, `WS_BASE` |
| `tools/ws/lib/add.sh` | `ws_add`: `subtree add --squash` dos repos que faltam |
| `tools/ws/lib/maintain.sh` | `ws_maintain`, `ws_maintain_rejoin`, `ws_maintain_drift`, marcadores de split |
| `tools/ws/lib/start.sh` | `ws_start`: pull do workspace, `subtree pull` de cada repo, marcadores, push do `main`, branch nova |
| `tools/ws/lib/push.sh` | `ws_push`, `ws_changed_prefixes`, `ws_guard_violations` |
| `tools/ws/tests/lib.sh` | Fixture (remotos bare locais) e asserts |
| `tools/ws/tests/run.sh` | Runner: cada `test_*` num bash novo com fixture própria |
| `tools/ws/tests/test_*.sh` | Testes por comando e o ciclo completo |
| `.gitattributes` | LF nos scripts e no manifesto, sem tocar os prefixos |
| `AGENTS.md`, `CLAUDE.md` | Instruções do harness para agentes |
| `docs/workspace.md` | Uso para humanos |
| `docs/adr/0001-workspace-git-subtree.md` | Cópia da ADR aceita |

**Tempo dos testes:** cada teste cria repos e roda subtree de verdade, e leva de 5 a 20 s no Windows; a suíte completa leva cerca de 10 min. Em cada task, rode só o arquivo dela; a suíte completa roda na Task 6.

---

### Task 1: Repo do workspace, dispatcher, manifesto e runner de testes

**Arquivos:**
- Criar: `.gitattributes`, `tools/ws/ws`, `tools/ws/lib/common.sh`, `tools/ws/tests/lib.sh`, `tools/ws/tests/run.sh`
- Testes: `tools/ws/tests/test_manifest.sh`

**Interfaces:**
- Consome: nada.
- Produz (usado por todas as tasks seguintes):
  - `WS_BASE` (padrão `main`), `log <msg>` (stdout, prefixo `ws: `), `die <msg>` (stderr, `ws: erro: `, exit 1)
  - `ws_root` → caminho da raiz; `ws_manifest` → linhas `prefixo url branch`; falha em linha malformada ou prefixo fora de `repos/<nome>`
  - `ws_url_of <prefixo>` → url; falha se o prefixo não estiver no manifesto
  - `require_clean`, `current_branch` → nome da branch, `has_origin` → 0/1
  - Testes: `fx_setup`, `fx_ready`, `mk_remote`, `upstream_commit`, `merge_upstream`, `remote_tree`, `ws_commit`, `ws`, `wslib`, `run` (preenche `OUT` e `RC`), `fail`, `assert_eq`, `assert_contains`, `assert_not_contains`, `assert_ok`, `assert_fails`; variáveis `T` (pasta temporária) e `WS_DIR`
  - Dispatcher: `tools/ws/ws <add|start|push|maintain>` chama `ws_add`, `ws_start`, `ws_push`, `ws_maintain`

- [ ] **Step 1: Criar o repo local**

```bash
mkdir -p /c/src/wms-workspace && cd /c/src/wms-workspace
git init -b main
git config core.longpaths true
git config core.autocrlf false
mkdir -p tools/ws/lib tools/ws/tests docs/adr
```

- [ ] **Step 2: Escrever o `.gitattributes`**

Os padrões ficam ancorados na raiz. Um padrão sem barra, como `*.sh`, valeria também dentro de `repos/` e mudaria os bytes dos repos.

```gitattributes
# Só os arquivos do harness. Os prefixos repos/<repo>/ seguem o .gitattributes de cada repo.
/tools/** text eol=lf
/workspace.repos text eol=lf
```

- [ ] **Step 3: Escrever os helpers de teste `tools/ws/tests/lib.sh`**

```bash
# Helpers dos testes do ws: fixture com remotos bare locais e asserts. Nada acessa a rede.

WS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WS_BIN="$WS_DIR/ws"
export GIT_CONFIG_NOSYSTEM=1

# Cria $T com dois remotos (r1, r2), um origin bare para o workspace e o workspace em $T/ws,
# com manifesto e CLAUDE.md na raiz, commitados e enviados ao origin. Não roda ws add.
fx_setup() {
  T=$(mktemp -d "${TMPDIR:-/tmp}/ws-test.XXXXXX")
  trap 'cd /; rm -rf "$T"' EXIT
  export GIT_CONFIG_GLOBAL="$T/gitconfig"
  git config --global init.defaultBranch main
  git config --global user.name teste
  git config --global user.email teste@local
  git config --global core.autocrlf false
  git config --global core.longpaths true
  mkdir "$T/remotes"
  mk_remote r1
  mk_remote r2
  git init -q --bare "$T/origin.git"
  git init -q "$T/ws"
  cd "$T/ws"
  printf '%s\n' "# prefixo url branch-base" \
    "repos/r1 $T/remotes/r1.git main" \
    "repos/r2 $T/remotes/r2.git main" > workspace.repos
  echo "# harness" > CLAUDE.md
  git add -A
  git commit -qm "ws: init"
  git remote add origin "$T/origin.git"
  git push -q -u origin main
}

# fx_setup + ws add + push do main.
fx_ready() {
  ws add >/dev/null
  git push -q origin main
}

# nome -> repo bare $T/remotes/<nome>.git com README.md e src/app.txt ("v1") no main.
mk_remote() {
  local n=$1 tmp="$T/seed-$1"
  git init -q "$tmp"
  echo "# $n" > "$tmp/README.md"
  mkdir "$tmp/src"
  echo "v1" > "$tmp/src/app.txt"
  git -C "$tmp" add -A
  git -C "$tmp" commit -qm "init $n"
  git clone -q --bare "$tmp" "$T/remotes/$n.git"
  rm -rf "$tmp"
}

# nome arquivo conteúdo -> commit direto no main do remoto, como se fosse outro time.
upstream_commit() {
  local n=$1 f=$2 c=$3 tmp="$T/up-$1"
  rm -rf "$tmp"
  git clone -q "$T/remotes/$n.git" "$tmp"
  mkdir -p "$(dirname "$tmp/$f")"
  echo "$c" > "$tmp/$f"
  git -C "$tmp" add -A
  git -C "$tmp" commit -qm "outro time: $f"
  git -C "$tmp" push -q origin main
  rm -rf "$tmp"
}

# nome branch -> simula o merge do PR da branch no main do remoto.
merge_upstream() {
  local n=$1 br=$2 tmp="$T/pr-$1"
  rm -rf "$tmp"
  git clone -q "$T/remotes/$n.git" "$tmp"
  git -C "$tmp" merge -q --no-ff "origin/$br" -m "PR $br"
  git -C "$tmp" push -q origin main
  rm -rf "$tmp"
}

# nome [ref] -> hash da tree da ref (main por padrão) no remoto.
remote_tree() { git -C "$T/remotes/$1.git" rev-parse "${2:-main}^{tree}"; }

# commita no workspace: arquivo conteúdo [mensagem]
ws_commit() {
  mkdir -p "$(dirname "$1")"
  echo "$2" > "$1"
  git add -A
  git commit -qm "${3:-muda $1}"
}

ws() { bash "$WS_BIN" "$@"; }

# Roda uma função das libs do ws num bash novo, no diretório atual: wslib ws_manifest
wslib() { bash -c 'for f in "$0"/lib/*.sh; do source "$f"; done; "$@"' "$WS_DIR" "$@"; }

# Roda o comando e guarda a saída (stdout+stderr) em OUT e o código em RC, sem abortar.
run() { set +e; OUT=$("$@" 2>&1); RC=$?; set -e; }

fail() { echo "FALHA: $*"; exit 1; }
assert_eq() { [ "$1" = "$2" ] || fail "esperado [$2], obtido [$1]${3:+ ($3)}"; }
assert_contains() { case "$1" in *"$2"*) ;; *) fail "esperado conter [$2] em: $1" ;; esac; }
assert_not_contains() { case "$1" in *"$2"*) fail "não devia conter [$2] em: $1" ;; esac; }
assert_ok() { run "$@"; [ "$RC" -eq 0 ] || fail "falhou ($RC): $* :: $OUT"; }
assert_fails() { run "$@"; [ "$RC" -ne 0 ] || fail "devia falhar: $* :: $OUT"; }
```

- [ ] **Step 4: Escrever o runner `tools/ws/tests/run.sh`**

```bash
#!/usr/bin/env bash
# Roda os testes do ws. Cada função test_* roda num bash novo, com fixture própria.
# Uso: bash tools/ws/tests/run.sh [arquivo_de_teste...]   (WS_TEST=<nome> roda um teste só)
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
files=("$@")
[ ${#files[@]} -gt 0 ] || files=("$HERE"/test_*.sh)
pass=0
failed=0
for f in "${files[@]}"; do
  for t in $(bash -c "source '$HERE/lib.sh'; source '$f'; declare -F | awk '{ print \$3 }' | grep '^test_'"); do
    [ -z "${WS_TEST:-}" ] || [ "$WS_TEST" = "$t" ] || continue
    if out=$(bash -c "set -euo pipefail; source '$HERE/lib.sh'; source '$f'; fx_setup; $t" 2>&1); then
      pass=$((pass + 1))
      echo "ok    $t"
    else
      failed=$((failed + 1))
      echo "FALHA $t"
      sed 's/^/      /' <<< "$out"
    fi
  done
done
echo "$pass ok, $failed falha(s)"
[ "$failed" -eq 0 ]
```

- [ ] **Step 5: Escrever o teste que falha `tools/ws/tests/test_manifest.sh`**

```bash
# Testes do manifesto e do dispatcher.

test_manifest_ignora_comentarios_e_vazias() {
  printf '%s\n' "# comentário" "" "repos/a url-a main" "  " "repos/b url-b dev" > workspace.repos
  assert_eq "$(wslib ws_manifest)" "repos/a url-a main
repos/b url-b dev"
}

test_manifest_tolera_crlf() {
  printf 'repos/a url-a main\r\n' > workspace.repos
  local out
  out=$(wslib ws_manifest)
  assert_eq "$out" "repos/a url-a main"
}

test_manifest_rejeita_linha_malformada() {
  printf '%s\n' "repos/a url-a" > workspace.repos
  assert_fails wslib ws_manifest
  assert_contains "$OUT" "linha inválida"
}

test_manifest_rejeita_prefixo_fora_de_repos() {
  printf '%s\n' "outro/a url-a main" > workspace.repos
  assert_fails wslib ws_manifest
  assert_contains "$OUT" "linha inválida"
}

test_url_of_falha_para_prefixo_desconhecido() {
  assert_eq "$(wslib ws_url_of repos/r1)" "$T/remotes/r1.git"
  assert_fails wslib ws_url_of repos/x
}

test_comando_desconhecido_mostra_uso() {
  assert_fails ws foo
  assert_contains "$OUT" "uso: ws"
}
```

- [ ] **Step 6: Rodar e ver falhar**

Run: `bash tools/ws/tests/run.sh tools/ws/tests/test_manifest.sh`
Esperado: `0 ok, 6 falha(s)`, com erros como `ws_manifest: command not found` e `No such file or directory` para `tools/ws/ws`.

- [ ] **Step 7: Escrever `tools/ws/lib/common.sh`**

```bash
# Funções comuns do ws. Requer bash e git com git-subtree (o Git for Windows já traz).

WS_BASE=${WS_BASE:-main}

log() { echo "ws: $*"; }
die() { echo "ws: erro: $*" >&2; exit 1; }

ws_root() { git rev-parse --show-toplevel 2>/dev/null || die "fora de um repo git"; }

# Imprime o manifesto como linhas "prefixo url branch-base".
# Ignora linhas vazias e comentários (#) e tolera CRLF. Falha em linha malformada.
ws_manifest() {
  local f
  f="$(ws_root)/workspace.repos"
  [ -f "$f" ] || die "manifesto não encontrado: $f"
  tr -d '\r' < "$f" | awk '
    NF == 0 || $1 ~ /^#/ { next }
    NF != 3 || $1 !~ /^repos\/[^\/]+$/ { print "ws: erro: linha inválida no manifesto: " $0 > "/dev/stderr"; bad = 1; exit }
    { print $1, $2, $3 }
    END { exit bad }'
}

# prefixo -> url do manifesto; falha se o prefixo não estiver no manifesto.
ws_url_of() {
  local m
  m=$(ws_manifest)
  awk -v p="$1" '$1 == p { print $2; found = 1 } END { exit !found }' <<< "$m"
}

require_clean() {
  [ -z "$(git status --porcelain)" ] || die "há mudanças não commitadas; faça commit ou stash antes"
}

current_branch() {
  git symbolic-ref --short -q HEAD || die "HEAD destacado; faça checkout de uma branch"
}

has_origin() { git remote get-url origin >/dev/null 2>&1; }
```

- [ ] **Step 8: Escrever o dispatcher `tools/ws/ws`**

```bash
#!/usr/bin/env bash
# ws: fluxo do workspace multi-repo com git subtree --squash (ADR 0001).
# Uso: tools/ws/ws <add|start|push|maintain> [args]
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
  *)        die "uso: ws <add|start|push|maintain> [args]" ;;
esac
```

```bash
git add tools/ws/ws && git update-index --chmod=+x tools/ws/ws
```

- [ ] **Step 9: Rodar e ver passar**

Run: `bash tools/ws/tests/run.sh tools/ws/tests/test_manifest.sh`
Esperado: `6 ok, 0 falha(s)`.

- [ ] **Step 10: Conferir que o `.gitattributes` não alcança os prefixos**

Run: `git check-attr eol -- tools/ws/ws repos/x/a.sh repos/x/workspace.repos`
Esperado: `tools/ws/ws: eol: lf` e `unspecified` para os dois caminhos em `repos/`.

- [ ] **Step 11: Commit**

```bash
git add -A
git commit -m "ws: dispatcher, manifesto e runner de testes"
```

---

### Task 2: `ws add`

**Arquivos:**
- Criar: `tools/ws/lib/add.sh`
- Testes: `tools/ws/tests/test_add.sh`

**Interfaces:**
- Consome: `ws_root`, `require_clean`, `current_branch`, `ws_manifest`, `log`, `die`, `WS_BASE` (Task 1).
- Produz: `ws_add` — no `WS_BASE` e com a árvore limpa, roda `git subtree add --prefix=<p> <url> <branch> --squash -m "ws: add <p>"` para cada prefixo que ainda não existe; imprime `adicionado <p> (<n> s)` ou `<p> já existe; pulando`.

- [ ] **Step 1: Escrever o teste que falha `tools/ws/tests/test_add.sh`**

```bash
# Testes do ws add.

test_add_traz_cada_repo_com_a_tree_do_remoto() {
  assert_ok ws add
  assert_contains "$OUT" "adicionado repos/r1"
  assert_contains "$OUT" "adicionado repos/r2"
  assert_eq "$(git rev-parse HEAD:repos/r1)" "$(remote_tree r1)"
  assert_eq "$(git rev-parse HEAD:repos/r2)" "$(remote_tree r2)"
}

test_add_usa_squash() {
  ws add >/dev/null
  assert_contains "$(git log --format=%s)" "Squashed 'repos/r1/' content from commit"
  assert_not_contains "$(git log --format=%s)" "init r1"
}

test_add_e_idempotente() {
  ws add >/dev/null
  local head
  head=$(git rev-parse HEAD)
  assert_ok ws add
  assert_contains "$OUT" "repos/r1 já existe; pulando"
  assert_eq "$(git rev-parse HEAD)" "$head"
}

test_add_recusa_fora_do_main() {
  git checkout -q -b outra
  assert_fails ws add
  assert_contains "$OUT" "rode ws add no main"
}

test_add_recusa_arvore_suja() {
  echo x > sujo.txt
  assert_fails ws add
  assert_contains "$OUT" "mudanças não commitadas"
}
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `bash tools/ws/tests/run.sh tools/ws/tests/test_add.sh`
Esperado: `0 ok, 5 falha(s)`, com `ws_add: command not found`.

- [ ] **Step 3: Escrever `tools/ws/lib/add.sh`**

```bash
# ws add: subtree add --squash dos repos do manifesto que ainda não estão no workspace.

ws_add() {
  cd "$(ws_root)"
  require_clean
  [ "$(current_branch)" = "$WS_BASE" ] || die "rode ws add no $WS_BASE"
  local m prefix url branch s
  m=$(ws_manifest)
  while read -r prefix url branch; do
    if [ -d "$prefix" ]; then
      log "$prefix já existe; pulando"
      continue
    fi
    s=$SECONDS
    git subtree add --prefix="$prefix" "$url" "$branch" --squash -m "ws: add $prefix" >/dev/null \
      || die "subtree add falhou em $prefix"
    log "adicionado $prefix ($((SECONDS - s)) s)"
  done <<< "$m"
}
```

- [ ] **Step 4: Rodar e ver passar**

Run: `bash tools/ws/tests/run.sh tools/ws/tests/test_add.sh`
Esperado: `5 ok, 0 falha(s)`.

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "ws: comando add (subtree add --squash dos repos do manifesto)"
```

---

### Task 3: `ws maintain` (marcadores de split e deriva)

**Arquivos:**
- Criar: `tools/ws/lib/maintain.sh`
- Testes: `tools/ws/tests/test_maintain.sh`

**Interfaces:**
- Consome: Task 1 inteira; `ws add` (Task 2) nos testes, via `fx_ready`.
- Produz:
  - `WS_REJOIN_THRESHOLD` (padrão 100)
  - `ws_last_rejoin <p>` → hash do último commit com `git-subtree-mainline` para o prefixo, ou vazio
  - `ws_last_squash <p>` → hash do último commit `Squashed '<p>/' …`
  - `ws_commits_since_rejoin <p>` → número de commits do base desde o marcador (ou todos)
  - `ws_mark_split <p> <squash>` → grava o marcador sem mudar a tree (ver "Desvio da ADR")
  - `ws_maintain_rejoin` → para cada prefixo acima do limite, grava marcador ou roda `split --rejoin --squash <base> <url>`; imprime `rejoin <p> (<n> commits desde o último marcador)`. Usado pelo `ws_start` (Task 4)
  - `ws_maintain_drift` → imprime `deriva: <p> …` por prefixo divergente, ou `sem deriva`
  - `ws_maintain` → exige base e árvore limpa; roda os dois e avisa `rode git push origin main` se o base estiver à frente do origin

- [ ] **Step 1: Escrever o teste que falha `tools/ws/tests/test_maintain.sh`**

```bash
# Testes do ws maintain.

test_maintain_sem_deriva_logo_apos_add() {
  fx_ready
  assert_ok ws maintain
  assert_contains "$OUT" "sem deriva"
}

test_maintain_aponta_deriva_quando_remoto_anda() {
  fx_ready
  upstream_commit r2 src/novo.txt "do outro time"
  assert_ok ws maintain
  assert_contains "$OUT" "deriva: repos/r2"
  assert_not_contains "$OUT" "deriva: repos/r1"
}

test_maintain_faz_rejoin_acima_do_limite() {
  fx_ready
  local i
  for i in 2 3 4 5; do ws_commit repos/r1/src/app.txt "v$i"; done
  export WS_REJOIN_THRESHOLD=3
  assert_ok ws maintain
  assert_contains "$OUT" "rejoin repos/r1"
  assert_contains "$OUT" "rejoin repos/r2"
  # Depois do rejoin, o split só percorre os commits criados pelos rejoins seguintes.
  [ "$(wslib ws_commits_since_rejoin repos/r1)" -lt 3 ] || fail "rejoin não zerou a contagem de repos/r1"
  assert_eq "$(wslib ws_commits_since_rejoin repos/r2)" "0"
}

test_maintain_nao_faz_rejoin_abaixo_do_limite() {
  fx_ready
  ws_commit repos/r1/src/app.txt "v2"
  assert_ok ws maintain
  assert_not_contains "$OUT" "rejoin"
}

test_maintain_avisa_main_a_frente_do_origin() {
  fx_ready
  ws_commit HARNESS.md "x"
  assert_ok ws maintain
  assert_contains "$OUT" "rode git push origin main"
}

test_maintain_recusa_fora_do_main() {
  fx_ready
  git checkout -q -b outra
  assert_fails ws maintain
  assert_contains "$OUT" "rode ws maintain no main"
}

test_maintain_marca_prefixo_intocado_sem_rodar_split() {
  fx_ready
  local i
  for i in 1 2 3 4; do ws_commit HARNESS.md "v$i"; done
  WS_REJOIN_THRESHOLD=3 run ws maintain
  assert_eq "$RC" "0" "$OUT"
  assert_contains "$OUT" "rejoin repos/r2"
  assert_contains "$(git log -1 --format=%B)" "git-subtree-mainline:"
  [ "$(wslib ws_commits_since_rejoin repos/r1)" -lt 3 ] || fail "marcador não zerou a contagem de repos/r1"
  # O push depois do marcador continua correto.
  ws start feat/a >/dev/null
  ws_commit repos/r2/src/app.txt "v2"
  assert_ok ws push
  assert_ok git -C "$T/remotes/r2.git" merge-base --is-ancestor main feat/a
  assert_eq "$(git -C "$T/remotes/r2.git" diff --name-only main...feat/a)" "src/app.txt"
}
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `bash tools/ws/tests/run.sh tools/ws/tests/test_maintain.sh`
Esperado: `0 ok, 7 falha(s)`, com `ws_maintain: command not found`.

- [ ] **Step 3: Escrever `tools/ws/lib/maintain.sh`**

```bash
# ws maintain: marcadores de split nos prefixos com histórico longo e verificação de deriva (ADR 0001, seção 4).

WS_REJOIN_THRESHOLD=${WS_REJOIN_THRESHOLD:-100}

# Último marcador de rejoin do prefixo no base; vazio se nunca houve.
# Só um commit com git-subtree-mainline faz o split pular o histórico do workspace;
# os commits de squash do add/pull não fazem isso.
ws_last_rejoin() {
  git log -1 --format=%H --all-match \
    --grep="^git-subtree-dir: $1/*\$" --grep='^git-subtree-mainline:' "$WS_BASE"
}

# Último commit de squash (add, pull ou rejoin --squash) do prefixo no base.
# A tree dele é a tree do repo no commit citado em git-subtree-split.
ws_last_squash() {
  git log -1 --format=%H --all-match \
    --grep="^git-subtree-dir: $1/*\$" --grep="^Squashed '$1/' " "$WS_BASE"
}

# Commits do base que o split do prefixo percorre: desde o último marcador de rejoin, ou todos.
ws_commits_since_rejoin() {
  local mark
  mark=$(ws_last_rejoin "$1")
  if [ -n "$mark" ]; then
    git rev-list --count "$mark..$WS_BASE"
  else
    git rev-list --count "$WS_BASE"
  fi
}

# Prefixo sem mudança local desde o último squash: o split --rejoin não criaria nada.
# Grava o mesmo commit que um rejoin gravaria: um merge do HEAD com esse squash, sem mudar a tree,
# com os trailers do git subtree. O split seguinte começa daqui, e o subtree pull continua achando
# o squash (ele lê o segundo pai do commit de rejoin).
ws_mark_split() {
  local p=$1 sq=$2 head split mark
  head=$(git rev-parse HEAD)
  split=$(git log -1 --format=%b "$sq" | awk '$1 == "git-subtree-split:" { print $2 }')
  [ -n "$split" ] || die "commit de squash sem git-subtree-split em $p: $sq"
  mark=$(printf '%s\n' "Split '$p/' into commit '$split'" "" \
    "ws maintain: marcador sem mudança no prefixo." "" \
    "git-subtree-dir: $p" "git-subtree-mainline: $head" "git-subtree-split: $split" \
    | git commit-tree "HEAD^{tree}" -p "$head" -p "$sq")
  git merge -q --ff-only "$mark"
}

# Roda no base. Marca só os prefixos acima do limite.
ws_maintain_rejoin() {
  local m prefix url branch n sq
  m=$(ws_manifest)
  while read -r prefix url branch; do
    n=$(ws_commits_since_rejoin "$prefix")
    [ "$n" -gt "$WS_REJOIN_THRESHOLD" ] || continue
    sq=$(ws_last_squash "$prefix")
    if [ -n "$sq" ] && [ "$(git rev-parse "$sq^{tree}")" = "$(git rev-parse "HEAD:$prefix")" ]; then
      ws_mark_split "$prefix" "$sq"
    else
      git subtree split --prefix="$prefix" --rejoin --squash "$WS_BASE" "$url" >/dev/null 2>&1 \
        || die "rejoin falhou em $prefix"
    fi
    log "rejoin $prefix ($n commits desde o último marcador)"
  done <<< "$m"
}

# Compara a tree de cada prefixo no base com a do branch remoto e lista os que divergem.
ws_maintain_drift() {
  local m prefix url branch remote local_ drift=0
  m=$(ws_manifest)
  while read -r prefix url branch; do
    git fetch -q "$url" "$branch" || die "fetch falhou em $url"
    remote=$(git rev-parse "FETCH_HEAD^{tree}")
    local_=$(git rev-parse "$WS_BASE:$prefix")
    if [ "$remote" != "$local_" ]; then
      log "deriva: $prefix difere de $branch no remoto (rode ws start para sincronizar)"
      drift=1
    fi
  done <<< "$m"
  [ "$drift" -eq 1 ] || log "sem deriva"
}

ws_maintain() {
  cd "$(ws_root)"
  require_clean
  [ "$(current_branch)" = "$WS_BASE" ] || die "rode ws maintain no $WS_BASE"
  ws_maintain_rejoin
  ws_maintain_drift
  if has_origin && [ -n "$(git rev-list "origin/$WS_BASE..$WS_BASE" 2>/dev/null)" ]; then
    log "o $WS_BASE tem commits novos; rode git push origin $WS_BASE"
  fi
}
```

- [ ] **Step 4: Rodar e ver passar**

Run: `bash tools/ws/tests/run.sh tools/ws/tests/test_maintain.sh`
Esperado: `7 ok, 0 falha(s)`.

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "ws: comando maintain (marcadores de split e verificação de deriva)"
```

---

### Task 4: `ws start`

**Arquivos:**
- Criar: `tools/ws/lib/start.sh`
- Testes: `tools/ws/tests/test_start.sh`

**Interfaces:**
- Consome: Task 1; `ws_maintain_rejoin` (Task 3); `ws add` nos testes.
- Produz: `ws_start <branch>` — exige árvore limpa e branch inexistente; vai para o base; `git pull --ff-only origin <base>` se houver origin; `git subtree pull --squash -m "ws: sync <p>"` de cada prefixo, parando no primeiro erro com `conflito ou falha no subtree pull de <p>…`; `ws_maintain_rejoin`; `git push origin <base>` se houver origin; cria a branch. Imprime `sincronizado <p>` e `branch <b> criada`.

- [ ] **Step 1: Escrever o teste que falha `tools/ws/tests/test_start.sh`**

```bash
# Testes do ws start.

test_start_traz_mudancas_do_remoto_e_cria_branch() {
  fx_ready
  upstream_commit r1 src/novo.txt "do outro time"
  assert_ok ws start feat/a
  assert_contains "$OUT" "sincronizado repos/r1"
  assert_eq "$(git symbolic-ref --short HEAD)" "feat/a"
  assert_eq "$(git rev-parse main:repos/r1)" "$(remote_tree r1)"
  assert_eq "$(cat repos/r1/src/novo.txt)" "do outro time"
}

test_start_envia_o_main_ao_origin() {
  fx_ready
  upstream_commit r1 src/novo.txt "x"
  ws start feat/a >/dev/null
  assert_eq "$(git -C "$T/origin.git" rev-parse main)" "$(git rev-parse main)"
}

test_start_sem_novidade_no_remoto_funciona() {
  fx_ready
  assert_ok ws start feat/a
  git checkout -q main
  assert_ok ws start feat/b
  assert_eq "$(git symbolic-ref --short HEAD)" "feat/b"
}

test_start_recusa_branch_existente() {
  fx_ready
  git branch feat/a
  assert_fails ws start feat/a
  assert_contains "$OUT" "a branch feat/a já existe"
}

test_start_exige_nome_da_branch() {
  fx_ready
  assert_fails ws start
  assert_contains "$OUT" "uso: ws start <branch>"
}

test_start_recusa_arvore_suja() {
  fx_ready
  echo x >> repos/r1/src/app.txt
  assert_fails ws start feat/a
  assert_contains "$OUT" "mudanças não commitadas"
}

test_start_para_no_conflito_sem_criar_branch_nem_enviar_main() {
  fx_ready
  ws_commit repos/r1/src/app.txt "local"
  local origin_antes
  origin_antes=$(git -C "$T/origin.git" rev-parse main)
  upstream_commit r1 src/app.txt "remoto"
  assert_fails ws start feat/a
  assert_contains "$OUT" "subtree pull de repos/r1"
  assert_fails git show-ref --verify -q refs/heads/feat/a
  assert_eq "$(git -C "$T/origin.git" rev-parse main)" "$origin_antes"
}

test_start_recusa_repo_do_manifesto_ausente() {
  fx_ready
  echo "repos/r3 $T/remotes/r3.git main" >> workspace.repos
  git commit -qam "manifesto com r3"
  assert_fails ws start feat/a
  assert_contains "$OUT" "repos/r3 não está no workspace; rode ws add"
}

test_start_faz_rejoin_quando_precisa() {
  fx_ready
  local i
  for i in 1 2 3 4; do ws_commit HARNESS.md "v$i"; done
  git push -q origin main
  WS_REJOIN_THRESHOLD=3 run ws start feat/a
  assert_eq "$RC" "0" "$OUT"
  assert_contains "$OUT" "rejoin repos/r1"
  assert_eq "$(git -C "$T/origin.git" rev-parse main)" "$(git rev-parse main)"
}
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `bash tools/ws/tests/run.sh tools/ws/tests/test_start.sh`
Esperado: `0 ok, 9 falha(s)`, com `ws_start: command not found`.

- [ ] **Step 3: Escrever `tools/ws/lib/start.sh`**

```bash
# ws start <branch>: sincroniza o base com os repos e cria a branch de trabalho (ADR 0001, seção 3).

ws_start() {
  local br=${1:-}
  [ -n "$br" ] || die "uso: ws start <branch>"
  cd "$(ws_root)"
  require_clean
  if git show-ref --verify -q "refs/heads/$br"; then die "a branch $br já existe"; fi
  git checkout -q "$WS_BASE"
  if has_origin; then
    git pull -q --ff-only origin "$WS_BASE" || die "git pull do $WS_BASE falhou"
  fi
  local m prefix url branch
  m=$(ws_manifest)
  while read -r prefix url branch; do
    [ -d "$prefix" ] || die "$prefix não está no workspace; rode ws add"
    git subtree pull --prefix="$prefix" "$url" "$branch" --squash -m "ws: sync $prefix" >/dev/null \
      || die "conflito ou falha no subtree pull de $prefix. Resolva no $WS_BASE (git status), faça commit e rode ws start $br de novo"
    log "sincronizado $prefix"
  done <<< "$m"
  ws_maintain_rejoin
  if has_origin; then
    git push -q origin "$WS_BASE" || die "push do $WS_BASE falhou"
  fi
  git checkout -q -b "$br"
  log "branch $br criada"
}
```

- [ ] **Step 4: Rodar e ver passar**

Run: `bash tools/ws/tests/run.sh tools/ws/tests/test_start.sh`
Esperado: `9 ok, 0 falha(s)`.

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "ws: comando start (sincroniza os repos e cria a branch)"
```

---

### Task 5: `ws push` e a guarda de harness

**Arquivos:**
- Criar: `tools/ws/lib/push.sh`
- Testes: `tools/ws/tests/test_push.sh`

**Interfaces:**
- Consome: Task 1; `ws start` e `ws add` nos testes.
- Produz:
  - `ws_changed_prefixes` → prefixos `repos/<r>` com arquivos alterados em `<base>...HEAD`
  - `ws_guard_violations <p>` → caminhos (relativos ao prefixo) de arquivos de harness adicionados, alterados, copiados ou renomeados; vazio se ok
  - `ws_push` → exige árvore limpa e branch ≠ base; valida todos os prefixos (manifesto e guarda) antes de enviar qualquer um; `git subtree push --prefix=<p> <url> <branch>` em cada; imprime `enviado <p> -> <branch>` ou `nenhum repo alterado nesta branch; nada a enviar`

- [ ] **Step 1: Escrever o teste que falha `tools/ws/tests/test_push.sh`**

```bash
# Testes do ws push e da guarda contra arquivos de harness nos repos.

test_push_envia_so_os_prefixos_alterados() {
  fx_ready
  ws start feat/a >/dev/null
  ws_commit repos/r1/src/app.txt "v2"
  ws_commit CLAUDE.md "harness alterado"
  assert_ok ws push
  assert_contains "$OUT" "enviado repos/r1 -> feat/a"
  assert_not_contains "$OUT" "repos/r2"
  assert_fails git -C "$T/remotes/r2.git" show-ref --verify -q refs/heads/feat/a
}

test_push_branch_descende_do_main_e_traz_so_o_arquivo_alterado() {
  fx_ready
  ws start feat/a >/dev/null
  ws_commit repos/r1/src/app.txt "v2"
  ws_commit CLAUDE.md "harness alterado"
  ws push >/dev/null
  local g="$T/remotes/r1.git"
  assert_ok git -C "$g" merge-base --is-ancestor main feat/a
  assert_eq "$(git -C "$g" diff --name-only main...feat/a)" "src/app.txt"
  assert_eq "$(git -C "$g" show feat/a:src/app.txt)" "v2"
}

test_push_nao_vaza_harness_da_raiz() {
  fx_ready
  ws start feat/a >/dev/null
  ws_commit repos/r1/src/app.txt "v2"
  ws push >/dev/null
  assert_fails git -C "$T/remotes/r1.git" cat-file -e feat/a:CLAUDE.md
  assert_fails git -C "$T/remotes/r1.git" cat-file -e feat/a:workspace.repos
}

test_push_sem_repo_alterado_nao_envia_nada() {
  fx_ready
  ws start feat/a >/dev/null
  ws_commit CLAUDE.md "só harness"
  assert_ok ws push
  assert_contains "$OUT" "nada a enviar"
}

test_push_de_novo_avanca_a_mesma_branch() {
  fx_ready
  ws start feat/a >/dev/null
  ws_commit repos/r1/src/app.txt "v2"
  ws push >/dev/null
  local antes
  antes=$(git -C "$T/remotes/r1.git" rev-parse feat/a)
  ws_commit repos/r1/src/app.txt "v3"
  assert_ok ws push
  assert_ok git -C "$T/remotes/r1.git" merge-base --is-ancestor "$antes" feat/a
  assert_eq "$(git -C "$T/remotes/r1.git" show feat/a:src/app.txt)" "v3"
}

test_push_recusa_no_main() {
  fx_ready
  assert_fails ws push
  assert_contains "$OUT" "ws push não roda no main"
}

test_push_recusa_arvore_suja() {
  fx_ready
  ws start feat/a >/dev/null
  echo x >> repos/r1/src/app.txt
  assert_fails ws push
  assert_contains "$OUT" "mudanças não commitadas"
}

test_push_recusa_prefixo_fora_do_manifesto() {
  fx_ready
  ws start feat/a >/dev/null
  ws_commit repos/r9/x.txt "x"
  assert_fails ws push
  assert_contains "$OUT" "repos/r9 foi alterado, mas não está no manifesto"
}

test_guarda_recusa_cada_arquivo_de_harness() {
  fx_ready
  local f n=0
  for f in CLAUDE.md claude.md sub/AGENTS.md .claude/settings.json app/.claude/x \
           .specify/memory/constitution.md specs/001/spec.md \
           .github/copilot-instructions.md .github/agents/a.md; do
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

test_guarda_aceita_specs_fora_da_raiz_do_repo() {
  fx_ready
  ws start feat/a >/dev/null
  ws_commit repos/r1/src/specs/x.txt "x"
  assert_ok ws push
}

test_guarda_e_tudo_ou_nada() {
  fx_ready
  ws start feat/a >/dev/null
  ws_commit repos/r1/src/app.txt "v2"
  ws_commit repos/r2/CLAUDE.md "x"
  assert_fails ws push
  assert_contains "$OUT" "GUARDA: repos/r2"
  assert_fails git -C "$T/remotes/r1.git" show-ref --verify -q refs/heads/feat/a
}

test_guarda_ignora_arquivo_de_agente_que_ja_existia() {
  upstream_commit r1 AGENTS.md "regras antigas"
  fx_ready
  ws start feat/a >/dev/null
  ws_commit repos/r1/src/app.txt "v2"
  assert_ok ws push
}

test_guarda_permite_remover_arquivo_de_agente() {
  upstream_commit r1 AGENTS.md "regras antigas"
  fx_ready
  ws start feat/a >/dev/null
  git rm -q repos/r1/AGENTS.md
  git commit -qm "migra AGENTS.md para o harness"
  assert_ok ws push
  assert_fails git -C "$T/remotes/r1.git" cat-file -e feat/a:AGENTS.md
}
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `bash tools/ws/tests/run.sh tools/ws/tests/test_push.sh`
Esperado: `0 ok, 13 falha(s)`, com `ws_push: command not found`.

- [ ] **Step 3: Escrever `tools/ws/lib/push.sh`**

```bash
# ws push: envia a branch atual para os repos cujos prefixos ela alterou (ADR 0001, seção 3).

# Prefixos repos/<repo> com arquivos alterados na branch em relação ao base.
ws_changed_prefixes() {
  git diff --name-only "$WS_BASE...HEAD" | awk -F/ '$1 == "repos" && NF >= 3 { print $1 "/" $2 }' | sort -u
}

# Arquivos de harness que a branch adiciona, altera, copia ou renomeia dentro do prefixo.
# Remoção é permitida: é assim que a migração (ADR 0001, seção 5) tira os arquivos de agente dos repos.
ws_guard_violations() {
  local p=$1
  git diff --name-only --diff-filter=ACMR "$WS_BASE...HEAD" -- "$p" \
    | awk -v n=$((${#p} + 2)) '{ print substr($0, n) }' \
    | grep -iE '(^|/)(CLAUDE\.md|AGENTS\.md)$|(^|/)\.claude/|(^|/)\.specify/|^specs/|^\.github/copilot-instructions\.md$|^\.github/agents/' \
    || true
}

ws_push() {
  cd "$(ws_root)"
  require_clean
  local br
  br=$(current_branch)
  [ "$br" != "$WS_BASE" ] || die "ws push não roda no $WS_BASE; crie a branch com ws start"
  local prefixes p v url bad=0
  prefixes=$(ws_changed_prefixes)
  if [ -z "$prefixes" ]; then
    log "nenhum repo alterado nesta branch; nada a enviar"
    return 0
  fi
  # Valida todos os prefixos antes de enviar qualquer um: ou vai tudo, ou nada.
  for p in $prefixes; do
    ws_url_of "$p" >/dev/null || die "$p foi alterado, mas não está no manifesto"
    v=$(ws_guard_violations "$p")
    if [ -n "$v" ]; then
      echo "ws: GUARDA: $p: a branch adiciona ou altera arquivos de harness:" >&2
      sed 's/^/  /' <<< "$v" >&2
      bad=1
    fi
  done
  [ "$bad" -eq 0 ] || die "push recusado; o harness fica na raiz do workspace (ADR 0001, seção 2)"
  for p in $prefixes; do
    url=$(ws_url_of "$p")
    git subtree push --prefix="$p" "$url" "$br" >/dev/null || die "subtree push de $p falhou"
    log "enviado $p -> $br"
  done
  log "abra um PR por repo no Azure DevOps a partir da branch $br"
}
```

- [ ] **Step 4: Rodar e ver passar**

Run: `bash tools/ws/tests/run.sh tools/ws/tests/test_push.sh`
Esperado: `13 ok, 0 falha(s)`.

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "ws: comando push com guarda contra arquivos de harness nos repos"
```

---

### Task 6: Ciclo completo e suíte inteira

**Arquivos:**
- Testes: `tools/ws/tests/test_ciclo.sh`
- Modificar, só se um teste falhar: `tools/ws/lib/*.sh`

**Interfaces:**
- Consome: todos os comandos das Tasks 2 a 5.
- Produz: a prova do fluxo da seção 3 da ADR (iniciar, trabalhar, enviar, PR, fechar, voltar), do PR abandonado, de ciclos repetidos com marcadores e de um clone novo do workspace.

- [ ] **Step 1: Escrever `tools/ws/tests/test_ciclo.sh`**

```bash
# Ciclo completo do fluxo da ADR 0001 (seção 3), como na PoC.

test_ciclo_completo_volta_ao_main_sem_conflito() {
  fx_ready
  # Iniciar e trabalhar: uma branch toca dois repos e o harness.
  ws start feat/ciclo >/dev/null
  ws_commit repos/r1/src/app.txt "v2"
  ws_commit repos/r2/README.md "# r2 alterado"
  ws_commit CLAUDE.md "harness alterado"
  # Enviar.
  assert_ok ws push
  # PR: os times fazem merge dos PRs e outro time commita direto no r1.
  merge_upstream r1 feat/ciclo
  merge_upstream r2 feat/ciclo
  upstream_commit r1 src/outro.txt "outro time"
  # Fechar: PR do workspace mergeia a branch no main.
  git checkout -q main
  git merge -q --no-ff feat/ciclo -m "PR do workspace feat/ciclo"
  git push -q origin main
  # Voltar: o próximo start sincroniza sem conflito e o prefixo fica idêntico ao remoto.
  assert_ok ws start feat/proximo
  assert_eq "$(git rev-parse main:repos/r1)" "$(remote_tree r1)"
  assert_eq "$(git rev-parse main:repos/r2)" "$(remote_tree r2)"
  git checkout -q main
  assert_ok ws maintain
  assert_contains "$OUT" "sem deriva"
}

test_ciclo_pr_abandonado_reverte_o_prefixo() {
  fx_ready
  ws start feat/ciclo >/dev/null
  ws_commit repos/r1/src/app.txt "v2"
  ws_commit repos/r1/src/novo.txt "novo"
  ws_commit repos/r2/src/app.txt "v2"
  ws push >/dev/null
  merge_upstream r2 feat/ciclo
  # PR do r1 abandonado: a branch devolve o prefixo ao estado do main antes do merge.
  git restore --source=main --staged --worktree -- repos/r1
  git commit -qm "reverte repos/r1: PR abandonado"
  git checkout -q main
  git merge -q --no-ff feat/ciclo -m "PR do workspace feat/ciclo"
  assert_ok ws start feat/proximo
  assert_eq "$(git rev-parse main:repos/r1)" "$(remote_tree r1)"
  assert_eq "$(git rev-parse main:repos/r2)" "$(remote_tree r2)"
}

test_ciclo_repetido_com_marcadores_de_split() {
  export WS_REJOIN_THRESHOLD=2
  fx_ready
  local n
  for n in 1 2 3; do
    assert_ok ws start "feat/c$n"
    ws_commit repos/r1/src/app.txt "ciclo $n"
    ws_commit CLAUDE.md "harness ciclo $n"
    assert_ok ws push
    assert_ok git -C "$T/remotes/r1.git" merge-base --is-ancestor main "feat/c$n"
    assert_eq "$(git -C "$T/remotes/r1.git" diff --name-only "main...feat/c$n")" "src/app.txt"
    merge_upstream r1 "feat/c$n"
    upstream_commit r2 "src/c$n.txt" "outro time $n"
    git checkout -q main
    git merge -q --no-ff "feat/c$n" -m "PR do workspace feat/c$n"
    git push -q origin main
  done
  assert_ok ws start feat/fim
  assert_eq "$(git rev-parse main:repos/r1)" "$(remote_tree r1)"
  assert_eq "$(git rev-parse main:repos/r2)" "$(remote_tree r2)"
}

test_clone_novo_do_workspace_faz_start_e_push() {
  fx_ready
  git clone -q "$T/origin.git" "$T/ws2"
  cd "$T/ws2"
  upstream_commit r1 src/novo.txt "outro time"
  assert_ok ws start feat/novo-dev
  ws_commit repos/r1/src/app.txt "v2"
  assert_ok ws push
  assert_ok git -C "$T/remotes/r1.git" merge-base --is-ancestor main feat/novo-dev
  assert_eq "$(git -C "$T/remotes/r1.git" diff --name-only main...feat/novo-dev)" "src/app.txt"
}
```

- [ ] **Step 2: Rodar o ciclo**

Run: `bash tools/ws/tests/run.sh tools/ws/tests/test_ciclo.sh`
Esperado: `4 ok, 0 falha(s)`. Estes testes cobrem comportamento já implementado. Se algum falhar, trate como bug nas libs: leia a saída, corrija a lib responsável e rode de novo o arquivo de teste dela e este.

- [ ] **Step 3: Rodar a suíte inteira**

Run: `bash tools/ws/tests/run.sh`
Esperado: `44 ok, 0 falha(s)` (cerca de 10 min no Windows).

- [ ] **Step 4: Commit**

```bash
git add -A
git commit -m "ws: testes do ciclo completo do fluxo"
```

---

### Task 7: Harness na raiz (`AGENTS.md`, `CLAUDE.md`, docs)

**Arquivos:**
- Criar: `AGENTS.md`, `CLAUDE.md`, `docs/workspace.md`, `docs/adr/0001-workspace-git-subtree.md`

**Interfaces:**
- Consome: os nomes dos comandos e as regras das Tasks 1 a 5.
- Produz: a regra da seção 2 da ADR em forma operacional para agentes e o guia de uso para humanos. A redação da constitution fica para o SP2.

- [ ] **Step 1: Escrever `AGENTS.md`**

```markdown
# Workspace WMS: instruções para agentes

Este repo é o workspace multi-repo do WMS (`docs/adr/0001-workspace-git-subtree.md`). O código de cada sistema está em `repos/<repo>/`, um git subtree do repo no Azure DevOps. Todo o resto é o harness. Uso humano: `docs/workspace.md`.

## Regras

1. Antes de mexer em `repos/<repo>/`, leia `repos/<repo>/docs/convencoes.md` e `repos/<repo>/docs/adr/`, se existirem.
2. Ao surgir uma regra ou decisão nova:
   - se vale só para um repo, grave em `repos/<repo>/docs/convencoes.md` ou numa ADR em `repos/<repo>/docs/adr/NNNN-<titulo>.md`;
   - se vale para mais de um repo, ou é sobre como o agente trabalha, grave no harness, na raiz.
3. Nunca crie nem altere dentro de `repos/<repo>/`: `CLAUDE.md`, `AGENTS.md`, `.claude/`, `.specify/`, `specs/`, `.github/copilot-instructions.md`, `.github/agents/`. O `ws push` recusa a branch.
4. Fluxo: `tools/ws/ws start <branch>`, commits, `tools/ws/ws push`, PR manual por repo. Não rode `git push` para os repos, `git subtree` à mão nem `git pull` numa branch de trabalho.
5. Os repos continuam independentes: cada mudança em `repos/<repo>/` precisa passar no build e nos testes daquele repo, com as ferramentas dele.
```

- [ ] **Step 2: Escrever `CLAUDE.md`**

O Claude Code lê o `CLAUDE.md` e importa o `AGENTS.md`; os dois agentes leem o mesmo texto.

```markdown
@AGENTS.md
```

- [ ] **Step 3: Escrever `docs/workspace.md`**

````markdown
# Workspace WMS: como usar

Workspace multi-repo do WMS. Cada repo do Azure DevOps entra como git subtree `--squash` em `repos/<repo>/`; a raiz é o harness (instruções, skills, specs, scripts). Decisão e alternativas: `docs/adr/0001-workspace-git-subtree.md`.

## Clonar

```bash
git clone -c core.longpaths=true -c core.autocrlf=false https://dev.azure.com/ARECO/AReCO/_git/industria-logistica.wms.workspace
```

Requisitos: Git for Windows (os scripts rodam no Git Bash) e credencial do Azure DevOps (Git Credential Manager ou PAT) com permissão de push de branch nos repos do `workspace.repos`.

## Fluxo

1. `tools/ws/ws start <branch>`: sincroniza o `main` do workspace com o `main` de cada repo, envia o `main` e cria a branch.
2. Trabalhe com commits normais. Uma branch pode tocar vários repos e o harness.
3. `tools/ws/ws push`: envia a branch, com o mesmo nome, para cada repo que ela alterou. Pode rodar de novo depois de novos commits.
4. Abra um PR por repo no Azure DevOps, no fluxo normal de cada time.
5. Com **todos** os PRs dos repos mergeados, abra o PR do workspace da branch para o `main`. Ele leva também as mudanças do harness.
   Se o PR de um repo for abandonado, devolva o prefixo ao estado do `main` antes do PR do workspace:
   ```bash
   git restore --source=main --staged --worktree -- repos/<repo>
   git commit -m "reverte repos/<repo>: PR abandonado"
   ```
6. O próximo `ws start` traz o `main` de cada repo, já com o seu PR.

## Regras

- Não faça `git push` para os repos nem `git subtree` à mão. Um `git push` no workspace só vai para o workspace.
- Dentro de `repos/<repo>/`, não crie nem altere `CLAUDE.md`, `AGENTS.md`, `.claude/`, `.specify/`, `specs/` (na raiz do repo), `.github/copilot-instructions.md` e `.github/agents/`. O `ws push` recusa a branch inteira. Remover esses arquivos é permitido.
- Regra ou decisão que vale só para um repo: `repos/<repo>/docs/convencoes.md` e `repos/<repo>/docs/adr/`. O resto fica no harness, na raiz.

## Conflito no `ws start`

O `ws start` para no primeiro repo com conflito, no `main`, com o merge em andamento. Nenhuma branch é criada e o `main` não é enviado. Resolva (`git status`, edite, `git add`, `git commit`) e rode `tools/ws/ws start <branch>` de novo.

## Manutenção

`tools/ws/ws maintain`, no `main`:
- grava um marcador de split nos prefixos com mais de `WS_REJOIN_THRESHOLD` commits (padrão 100) desde o último, para o split do `ws push` continuar rápido. O `ws start` já faz isso;
- lista os prefixos cuja tree diverge do `main` do repo.

Depois, `git push origin main`.

## Adicionar um repo

Acrescente a linha `repos/<repo> <url> <branch-base>` no `workspace.repos`, faça commit no `main` e rode `tools/ws/ws add`.

## Testes do `tools/ws`

```bash
bash tools/ws/tests/run.sh                              # todos (cerca de 10 min no Windows)
bash tools/ws/tests/run.sh tools/ws/tests/test_push.sh  # um arquivo
WS_TEST=test_push_recusa_no_main bash tools/ws/tests/run.sh tools/ws/tests/test_push.sh
```

Os testes usam repos bare locais em uma pasta temporária; nada acessa a rede.
````

- [ ] **Step 4: Copiar a ADR aceita**

```bash
cp /c/src/00-harness_big_brown_field/docs/adr/0001-workspace-git-subtree.md docs/adr/
```

- [ ] **Step 5: Conferir as referências cruzadas**

Run: `grep -o 'tools/ws/ws [a-z]*' AGENTS.md docs/workspace.md | sort -u`
Esperado: só `add`, `maintain`, `push` e `start`, que são os comandos do dispatcher.
Run: `ls docs/adr/0001-workspace-git-subtree.md docs/workspace.md AGENTS.md CLAUDE.md`
Esperado: os quatro arquivos existem.

- [ ] **Step 6: Commit**

```bash
git add -A
git commit -m "harness: AGENTS.md, CLAUDE.md, guia do workspace e ADR 0001"
```

---

### Task 8: Bootstrap real no Azure DevOps

Esta task age em sistemas externos. **Não comece sem o OK explícito do usuário**, e peça OK de novo antes do Step 7.

**Arquivos:**
- Criar: `workspace.repos`
- Registrar os resultados (na pasta de discovery): `C:\src\00-harness_big_brown_field\docs\discovery\sp1-bootstrap.md` e a seção SP1 de `docs\discovery\estado-da-sessao.md`

**Interfaces:**
- Consome: todos os comandos do `tools/ws/ws`.
- Produz: o workspace publicado com os 17 repos e as medidas reais que a PoC não tinha: rede, Azure DevOps, 17 repos.

- [ ] **Step 1: Pré-requisitos, com o usuário**

1. Confirmar o nome do repo do workspace. Proposta: `industria-logistica.wms.workspace`, no projeto `AReCO` da organização `ARECO`. Se o nome mudar, ajuste a URL em `docs/workspace.md`.
2. O usuário cria o repo vazio no Azure DevOps, sem README.
3. Conferir a credencial num repo qualquer:

Run: `git ls-remote https://dev.azure.com/ARECO/AReCO/_git/industria-logistica.wms.picking.backend HEAD`
Esperado: uma linha `<sha>	HEAD`, sem pedir senha no terminal (o GCM pode abrir uma janela na primeira vez).

- [ ] **Step 2: Escrever o manifesto `workspace.repos`**

```text
# prefixo url branch-base (ADR 0001). Uma linha por repo.
repos/industria-logistica.print-zebra.utilitario.backend https://dev.azure.com/ARECO/AReCO/_git/industria-logistica.print-zebra.utilitario.backend main
repos/industria-logistica.reserva-net.api-gateway.backend https://dev.azure.com/ARECO/AReCO/_git/industria-logistica.reserva-net.api-gateway.backend main
repos/industria-logistica.reserva-net.autenticacao.monolito https://dev.azure.com/ARECO/AReCO/_git/industria-logistica.reserva-net.autenticacao.monolito main
repos/industria-logistica.reserva-net.b2b.backend https://dev.azure.com/ARECO/AReCO/_git/industria-logistica.reserva-net.b2b.backend main
repos/industria-logistica.wms.app.frontend https://dev.azure.com/ARECO/AReCO/_git/industria-logistica.wms.app.frontend main
repos/industria-logistica.wms.awx.monorepo https://dev.azure.com/ARECO/AReCO/_git/industria-logistica.wms.awx.monorepo main
repos/industria-logistica.wms.conector.backend https://dev.azure.com/ARECO/AReCO/_git/industria-logistica.wms.conector.backend main
repos/industria-logistica.wms.ecommerce.backend https://dev.azure.com/ARECO/AReCO/_git/industria-logistica.wms.ecommerce.backend main
repos/industria-logistica.wms.ecommerce.frontend https://dev.azure.com/ARECO/AReCO/_git/industria-logistica.wms.ecommerce.frontend main
repos/industria-logistica.wms.hubprodutividade.backend https://dev.azure.com/ARECO/AReCO/_git/industria-logistica.wms.hubprodutividade.backend main
repos/industria-logistica.wms.picking.backend https://dev.azure.com/ARECO/AReCO/_git/industria-logistica.wms.picking.backend main
repos/industria-logistica.wms.picking.frontend https://dev.azure.com/ARECO/AReCO/_git/industria-logistica.wms.picking.frontend main
repos/industria-logistica.wms.servidor.backend https://dev.azure.com/ARECO/AReCO/_git/industria-logistica.wms.servidor.backend main
repos/industria-logistica.wms.tms-finished.backend https://dev.azure.com/ARECO/AReCO/_git/industria-logistica.wms.tms-finished.backend main
repos/industria-logistica.wms.tms.backend https://dev.azure.com/ARECO/AReCO/_git/industria-logistica.wms.tms.backend main
repos/industria-logistica.wms.trakta.backend https://dev.azure.com/ARECO/AReCO/_git/industria-logistica.wms.trakta.backend main
repos/integracoes.core.plataforma.backoffice.frontend https://dev.azure.com/ARECO/AReCO/_git/integracoes.core.plataforma.backoffice.frontend main
```

```bash
git add workspace.repos
git commit -m "ws: manifesto com os 17 repos"
```

- [ ] **Step 3: Adicionar os 17 repos, medindo o tempo**

Run: `time tools/ws/ws add 2>&1 | tee /c/src/00-harness_big_brown_field/docs/discovery/sp1-bootstrap-add.log`
Esperado: 17 linhas `ws: adicionado repos/<repo> (<n> s)`. Se um `subtree add` falhar, o comando para ali. Corrija a causa (credencial, `core.longpaths`) e rode de novo: os repos já adicionados são pulados.

- [ ] **Step 4: Conferir o resultado**

```bash
git ls-files | wc -l
du -sm .git
tools/ws/ws maintain
```

Esperado: `ws: sem deriva` (o `maintain` faz 17 fetches). Anote o número de arquivos e o tamanho do `.git`.

- [ ] **Step 5: Publicar o workspace**

```bash
git remote add origin https://dev.azure.com/ARECO/AReCO/_git/industria-logistica.wms.workspace
git push -u origin main
```

- [ ] **Step 6: Clone novo e `ws start`, sem tocar os repos**

```bash
git clone -c core.longpaths=true -c core.autocrlf=false https://dev.azure.com/ARECO/AReCO/_git/industria-logistica.wms.workspace /c/src/wms-workspace-check
cd /c/src/wms-workspace-check
time tools/ws/ws start chore/ws-smoke
```

Esperado: 17 linhas `ws: sincronizado …` e `ws: branch chore/ws-smoke criada`. O `ws start` só lê os repos; o único push dele é o do `main` do workspace, que não tem novidade.

- [ ] **Step 7: Smoke test de push num repo real (opcional, com OK do usuário)**

Este passo cria uma branch num repo de time. Ele valida o `subtree push` real a partir de um clone novo: credencial, push de branch e uma branch que descende do `main` do repo. A revisão mostrou que o fetch por SHA não é exercitado aqui, porque o `ws start` já trouxe o `main` do repo; e, depois da correção C1, o `ws` não grava mais commits que dependam disso. Sugestão: `industria-logistica.wms.picking.backend`, o repo do piloto.

```bash
cd /c/src/wms-workspace-check
echo "" >> repos/industria-logistica.wms.picking.backend/README.md
git commit -am "chore: smoke test do ws push (descartar)"
time tools/ws/ws push
git ls-remote https://dev.azure.com/ARECO/AReCO/_git/industria-logistica.wms.picking.backend chore/ws-smoke
git push https://dev.azure.com/ARECO/AReCO/_git/industria-logistica.wms.picking.backend --delete chore/ws-smoke
```

Esperado: `ws: enviado repos/industria-logistica.wms.picking.backend -> chore/ws-smoke`, a branch listada pelo `ls-remote` e depois apagada. Se o push falhar com `could not rev-parse split hash`, o Azure DevOps não serviu o fetch por SHA. Registre o erro e pare: isso muda a ADR e precisa de decisão do usuário.

Depois: `cd /c/src && rm -rf wms-workspace-check`.

- [ ] **Step 8: Registrar os resultados na pasta de discovery**

Escrever `C:\src\00-harness_big_brown_field\docs\discovery\sp1-bootstrap.md` com: data, versão do git, tempo total e por repo do `ws add` (do log), número de arquivos, tamanho do `.git`, tempo do `ws start` no clone novo, resultado do Step 7 (ou "não executado") e qualquer desvio. Na seção SP1 de `docs\discovery\estado-da-sessao.md`, marcar o SP1 como concluído e apontar para esse arquivo.

---

## Autorrevisão (feita ao escrever o plano)

| Item da ADR | Onde |
|---|---|
| 1. Repo novo, subtree `--squash`, prefixo 1:1, manifesto, `longpaths`/`autocrlf` | Tasks 1, 2 e 8 |
| 2. Harness na raiz; regra repo × workspace no `AGENTS.md`/`CLAUDE.md` | Task 7 (constitution: SP2) |
| 3. `ws start`, `ws push`, guarda, PR manual, fechar, PR abandonado, voltar | Tasks 4, 5 e 6; `docs/workspace.md` |
| 4. `ws maintain`: rejoin acima de 100 e deriva | Task 3, com o desvio descrito acima |
| 5. Migração dos arquivos de agente | Fora deste plano (SP2); a guarda já permite a remoção (Task 5) |
| Pendências 1 a 4 da ADR | 1: Task 8. 2: Tasks 1 a 6. 3: Task 7. 4: SP2 |
