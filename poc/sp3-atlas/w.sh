#!/bin/bash
cd ~/sp3
s=$(date +%s)
./cbm.sh index_repository --repo-path /mnt/c/src/00-harness_big_brown_field/poc/sp3-atlas/repos/industria-logistica.wms.awx.monorepo --name awx-mntc 2>&1 | head -c 300; echo
echo "tempo $(( $(date +%s)-s ))s"
./cbm.sh delete_project --project awx-mntc >/dev/null 2>&1
./cbm.sh config list 2>&1 | head -30
