#!/bin/bash
cd ~/sp3
./cbm.sh list_projects | awk 'NR>1 && NF>=2 {print $1}' | grep -v -e '^total' -e '^returned' -e '^has_more' | while read p; do ./cbm.sh delete_project --project "$p" >/dev/null 2>&1; done
for r in industria-logistica.wms.servidor.backend industria-logistica.wms.awx.monorepo industria-logistica.wms.picking.frontend; do
  s=$(date +%s)
  ./cbm.sh index_repository --repo-path "$HOME/sp3/repos/$r" --name "$r" > "idx-$r.json" 2>&1
  e=$(( $(date +%s)-s ))
  python3 - "$r" "$e" <<PY
import json,sys
r,e=sys.argv[1],sys.argv[2]
d=json.load(open(f"idx-{r}.json"))
print(r, e+"s", d.get("status"), "nodes",d.get("nodes"),"edges",d.get("edges"),"partial",d.get("parse_partial_count"),"unusable",d.get("parse_unusable_count"))
PY
done
./cbm.sh list_projects
