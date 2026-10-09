# PoC SP1: git subtree (DESCARTÁVEL)

Não é código a manter. Serve só de evidência para `docs/adr/0001-workspace-git-subtree.md`.

- `run-poc.sh`: roda da raiz do projeto e cria `work/` (remotos bare locais e o workspace). Nada vai para o Azure DevOps.
- `resultado.log`: saída da última execução.
- Testes manuais feitos depois do script (resultados na ADR): `split --rejoin` sem e com `--squash`, push depois do rejoin, e merge da branch no `main` do workspace seguido de `subtree pull`.
