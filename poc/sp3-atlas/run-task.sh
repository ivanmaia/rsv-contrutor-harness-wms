#!/bin/bash
# Uso: run-task.sh <id> <repo> <cfg: padrao|serena> <prompt>
# Copia o repo para runs/<id>-<cfg>/, roda claude -p e grava o stream JSON. Descartável (PoC SP3).
set -u
B=/c/src/00-harness_big_brown_field/poc/sp3-atlas
id=$1; repo=$2; cfg=$3; prompt=$4
dir=$B/runs/$id-$cfg/$repo
rm -rf "$B/runs/$id-$cfg"; mkdir -p "$B/runs/$id-$cfg"
cp -r "$B/repos/$repo" "$B/runs/$id-$cfg/"; rm -rf "$dir/graphify-out"
[ "$cfg" = padrao ] && rm -rf "$dir/.serena"
winpath=$(cygpath -w "$dir")
if [ "$cfg" = serena ]; then
  cat > "$B/runs/$id-$cfg/mcp.json" <<JSON
{"mcpServers":{"serena":{"command":"serena","args":["start-mcp-server","--context","claude-code","--project",$(python -c "import json,sys;print(json.dumps(sys.argv[1]))" "$winpath")]}}}
JSON
  extra=(--mcp-config "$(cygpath -w "$B/runs/$id-$cfg/mcp.json")" --append-system-prompt "Para navegar e editar código, prefira as ferramentas do Serena (mcp__serena__*): find_symbol, find_referencing_symbols, get_symbols_overview, replace_symbol_body, rename_symbol, insert_before/after_symbol.")
  tools="Read,Grep,Glob,Edit,Write,MultiEdit,mcp__serena__*"
else
  echo '{"mcpServers":{}}' > "$B/runs/$id-$cfg/mcp.json"
  extra=(--mcp-config "$(cygpath -w "$B/runs/$id-$cfg/mcp.json")")
  tools="Read,Grep,Glob,Edit,Write,MultiEdit"
fi
cd "$dir"
s=$(date +%s)
MCP_TIMEOUT=120000 claude -p "$prompt" --model sonnet --strict-mcp-config "${extra[@]}" \
  --allowedTools "$tools" --disallowedTools "Bash,WebFetch,WebSearch,Task,Agent" --permission-mode acceptEdits \
  --output-format stream-json --verbose < /dev/null > "$B/runs/$id-$cfg/stream.jsonl" 2> "$B/runs/$id-$cfg/stderr.txt"
echo "$id $cfg rc=$? $(( $(date +%s)-s ))s"
