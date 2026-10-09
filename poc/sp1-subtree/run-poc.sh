#!/usr/bin/env bash
# PoC DESCARTÁVEL do SP1: valida o fluxo git subtree --squash (start/push/pull) com remotos locais.
# Nada vai para o Azure DevOps. Os "remotos" são repos bare criados a partir do HEAD dos clones em repos/.
# Uso: bash poc/sp1-subtree/run-poc.sh  (roda da raiz do projeto)
set -euo pipefail
ROOT=$(pwd)
W=$ROOT/poc/sp1-subtree/work
REPOS="industria-logistica.wms.picking.backend industria-logistica.wms.servidor.backend industria-logistica.reserva-net.autenticacao.monolito industria-logistica.wms.ecommerce.backend"
rm -rf "$W"; mkdir -p "$W/remotes"
export GIT_AUTHOR_NAME=poc GIT_AUTHOR_EMAIL=poc@local GIT_COMMITTER_NAME=poc GIT_COMMITTER_EMAIL=poc@local
log(){ echo "[$(date +%T)] $*"; }
t(){ local s=$(date +%s%N); "$@" >/dev/null 2>&1; local rc=$?; local e=$(date +%s%N); awk -v d=$((e-s)) 'BEGIN{printf "%.1fs", d/1e9}'; return $rc; }

# 1. Remotos simulados: snapshot do HEAD + 30 commits sintéticos de histórico
for r in $REPOS; do
  src=$ROOT/repos/$r; tmp=$W/seed-$r
  mkdir -p "$tmp"; git -C "$src" archive HEAD | tar -x -C "$tmp"
  git -C "$tmp" init -q -b main; git -C "$tmp" config core.longpaths true; git -C "$tmp" config core.autocrlf false
  git -C "$tmp" add -A >/dev/null; git -C "$tmp" commit -qm "snapshot HEAD de $r"
  for i in $(seq 1 30); do echo "hist $i" >> "$tmp/POC_HIST.txt"; git -C "$tmp" add POC_HIST.txt; git -C "$tmp" commit -qm "hist $i"; done
  git clone -q --bare "$tmp" "$W/remotes/$r.git"; rm -rf "$tmp"
  log "remoto $r: $(git -C "$W/remotes/$r.git" ls-tree -r main --name-only | wc -l) arquivos"
done

# 2. Workspace + subtree add --squash
WS=$W/workspace; mkdir -p "$WS"; cd "$WS"
git init -q -b main; git config core.longpaths true; git config core.autocrlf false
printf '%s\n' $REPOS | sed 's|.*|repos/& ../remotes/&.git main|' > workspace.repos
echo "# harness (raiz)" > CLAUDE.md; git add -A; git commit -qm "workspace: manifesto e harness"
while read -r prefix url branch; do
  log "subtree add $prefix: $(t git subtree add --prefix="$prefix" "$W/remotes/$(basename $prefix).git" "$branch" --squash)"
done < workspace.repos
log "workspace: $(git ls-files | wc -l) arquivos, .git $(du -sm .git | cut -f1) MB"

# ws push: prefixos alterados desde a base, guarda contra arquivos de harness, subtree push
ws_push(){
  local br=$(git rev-parse --abbrev-ref HEAD)
  for prefix in $(git diff --name-only main...HEAD | grep '^repos/' | cut -d/ -f1-2 | sort -u); do
    if git diff --name-only main...HEAD -- "$prefix" | grep -qiE "^$prefix/(CLAUDE\.md|AGENTS\.md|\.claude/|\.specify/|specs/)"; then
      log "GUARDA: a branch adiciona/altera arquivos de harness em $prefix; push recusado"; continue
    fi
    log "subtree push $prefix -> $br: $(t git subtree push --prefix="$prefix" "$W/remotes/$(basename $prefix).git" "$br")"
  done
}
# ws start: subtree pull --squash de todos
ws_start(){
  git checkout -q main
  while read -r prefix url branch; do
    log "subtree pull $prefix: $(t git subtree pull --prefix="$prefix" "$W/remotes/$(basename $prefix).git" "$branch" --squash -m "sync $(basename $prefix)" || echo FALHOU)"
  done < workspace.repos
  git checkout -q -b "$1"
}
# simula merge do PR no remoto + um commit direto de outro time
merge_upstream(){
  local r=$1 br=$2 tmp=$W/pr-$1
  rm -rf "$tmp"; git clone -q -c core.longpaths=true "$W/remotes/$r.git" "$tmp"
  git -C "$tmp" merge -q --no-ff "origin/$br" -m "PR $br"
  echo "commit direto $(date +%s%N)" >> "$tmp/OUTRO_TIME.txt"; git -C "$tmp" add -A; git -C "$tmp" commit -qm "commit direto de outro time"
  git -C "$tmp" push -q origin main; rm -rf "$tmp"
}
check_branch(){ # a branch empurrada deve descender do main do remoto (PR sem histórico estranho)
  local r=$1 br=$2 g="$W/remotes/$1.git"
  local ahead=$(git -C "$g" rev-list --count "main..$br") files=$(git -C "$g" diff --name-only "main...$br" | tr '\n' ' ')
  if git -C "$g" merge-base --is-ancestor main "$br"; then log "OK $r/$br: $ahead commit(s) à frente do main; arquivos: $files"
  else log "ATENÇÃO $r/$br não descende do main (merge-base $(git -C "$g" merge-base main "$br" | cut -c1-8)); arquivos: $files"; fi
}

# 3. Ciclo 1: mudança em 2 repos
git checkout -q -b feat/ciclo1
echo "// poc" >> "repos/industria-logistica.wms.picking.backend/README.md"
echo "poc" > "repos/industria-logistica.wms.servidor.backend/POC_CICLO1.txt"
echo "harness local" >> CLAUDE.md
git add -A; git commit -qm "feat: mudança cross-repo ciclo 1"
ws_push
check_branch industria-logistica.wms.picking.backend feat/ciclo1
check_branch industria-logistica.wms.servidor.backend feat/ciclo1
git -C "$W/remotes/industria-logistica.wms.servidor.backend.git" ls-tree -r --name-only feat/ciclo1 | { grep -c CLAUDE.md || true; } | xargs -I{} echo "  CLAUDE.md raiz vazou para o remoto? ocorrências: {}"
merge_upstream industria-logistica.wms.picking.backend feat/ciclo1
merge_upstream industria-logistica.wms.servidor.backend feat/ciclo1

# 4. Ciclo 2: start (pull de volta, branch do ciclo 1 descartada) + nova mudança
ws_start feat/ciclo2
git log --oneline -1 >/dev/null
echo "poc2" > "repos/industria-logistica.wms.servidor.backend/POC_CICLO2.txt"
git add -A; git commit -qm "feat: ciclo 2"
ws_push
check_branch industria-logistica.wms.servidor.backend feat/ciclo2

# 5. Guarda: CLAUDE.md dentro de um prefixo
git checkout -q -b feat/guarda main
echo x > "repos/industria-logistica.wms.picking.backend/CLAUDE.md"; git add -A; git commit -qm "tenta vazar harness"
ws_push

# 6. Crescimento: 200 commits no workspace e tempo do split
git checkout -q -b feat/volume main
for i in $(seq 1 200); do
  r=$(printf '%s\n' $REPOS | sed -n "$(( (i % 4) + 1 ))p")
  echo "$i" >> "repos/$r/POC_VOL.txt"; git add -A; git commit -qm "vol $i"
done
for r in industria-logistica.wms.servidor.backend industria-logistica.wms.picking.backend; do
  log "split após 200 commits ($r): $(t git subtree split --prefix=repos/$r)"
  log "split repetido (cache) ($r): $(t git subtree split --prefix=repos/$r)"
done
log "FIM"
