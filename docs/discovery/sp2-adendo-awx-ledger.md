# SDD ledger — plan: C:/src/00-harness_big_brown_field/docs/superpowers/plans/2026-10-07-sp2-adendo-awx-subordinado.md
Spec: C:/src/00-harness_big_brown_field/docs/superpowers/specs/2026-10-07-sp2-adendo-harness-awx-subordinado-design.md
Base da branch: f2310280d (sp3-atlas)
Pre-flight: Task 3 consome o prefixo ws- da Task 2 (textos e teste citam specs/ws-NNN-<nome>/) — coerente; Task 1 e Task 3 mexem no test_harness.sh (contagens 7 e 8) — coerente.
Task 1: complete (commits f2310280d..24ff8fddb, tests: run.sh test_harness.sh → 7 ok, 0 falha(s))
Task 2: complete (commits 24ff8fddb..b7ad54778, tests: run.sh test_speckit_feature.sh → 36 ok, 0 falha(s)). Nota: a cópia instalada em .specify/extensions/ws/ é atualizada pela reinstalação da Task 3.
Task 3: complete (commits b7ad54778..09ff7f755, tests: run.sh test_harness.sh → 8 ok; test_speckit_install.sh → 6 ok)
Task 4: complete (suíte por arquivo: 186 ok, 0 falhas — 15 arquivos; speckit_feature 36 e speckit_install 6 rodados nas Tasks 2 e 3 sobre o mesmo HEAD)
Task 5: complete (e2e4: 5/5 ok — skill do AWX só qualificada; specify da raiz criou ws-001; plan conferiu a constitution do AWX; ws push levou ws-001 ao espelho; AWX numera 005 ignorando ws-001; ~US$ 2,40)
Final: review: 0 Critical, 2 Important, 4 Minor (revisor opus).
Final: fixed citar spec de repo pelo caminho travava o specify — test_citar_spec_de_repo_pelo_caminho_cria_feature_nova RED→GREEN, test_speckit_feature 37/37
Final: fixed ADR 0001 sem o adendo do AWX — test_adr_registra_o_adendo_do_awx RED→GREEN, test_harness 9/9
Final: Ruling: minor 3 (filtro do squash no teste) regraduado para Important e corrigido — um ws maintain no AWX faria o teste falhar sem motivo — sem RED reproduzível sem criar o marcador; verificado GREEN — custo se errado: nenhum
Final: Ruling: minor 5 (exemplo 'picking b2c consumer') regraduado para Important e corrigido no texto — quem seguisse o exemplo criaria feature nova em vez de revisão — sem teste (texto) — custo se errado: nenhum
Final: minor (deferred): docs/workspace.md:94 lista docs/constitution.md e não .specify/memory/constitution.md como instrução do repo
Final: minor (deferred): test_speckit_feature usa feat(004) nas mensagens de teste do commit-push e tem asserção que nunca falha (linha 272, pré-existente)
- Pós-revisão (2026-10-07): os dois minors adiados foram resolvidos a pedido do usuário — commit 16bfbb005; test_harness 9/9 (asserção nova RED→GREEN), test_speckit_feature 37/37.
