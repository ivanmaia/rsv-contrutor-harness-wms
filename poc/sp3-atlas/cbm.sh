#!/bin/bash
# roda o cbm (linux) dentro do WSL; uso: cbm.sh <tool> [json-args]
exec ~/sp3/bin/codebase-memory-mcp cli --quiet "$@"
