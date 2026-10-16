# SP6: validação da vertente de refactor

Spec: `docs/superpowers/specs/2026-10-16-sp6-refactor-design.md`. Plano: `docs/superpowers/plans/2026-10-16-sp6-refactor.md`.

## PoC do Spec Kit 1.2.0 (spec 10.1, itens 1 a 3)

Feito em 2026-10-16, numa cópia descartável do workspace em `%TEMP%\sp6-poc`, clonada do `main` local (`a996df32c`) e sem origin.

| # | Item | Resultado | Evidência e custo |
|---|---|---|---|
| 1 | Atualização sem quebrar `multirepo` e `bugs` | ok | O `ws speckit` com `VERSION` = 1.2.0 deu `rc=0`. A skill `speckit-specify` mantém "Regras do workspace multi-repo"; o `spec-template` resolvido mantém "Repos afetados"; a skill `speckit-bug-assess` mantém o preâmbulo do preset `bugs`. A extensão `bug` instalada é a 1.0.1: o `speckit.bug.assess` ainda cita `.specify/bugs/` (7 vezes) e dispara `before_bug_assess`, e o `speckit.bug.test` dispara `after_bug_test`. A suíte offline deu 275 ok e 0 falha. |
| 2 | Extensão nossa com hook de nome próprio | ok | Duas extensões de brinquedo (`poc` e `pocws`) instalaram com `extension add --dev` sem aviso. O `.specify/extensions.yml` registrou `before_poc_ola` e `before_bug_assess` → `speckit.pocws.marca`. No `claude -p "/speckit-poc-ola"`, o agente rodou o hook (gravou `marca.txt`) e respondeu `olá concluído`. Custo: US$ 0,37. |
| 3 | Hook nativo `before_bug_assess` | ok | No `/speckit-bug-assess` (work item fictício 90100), o hook `before_bug_assess` gravou o `marca.txt` e o preset criou a branch `hotfix/90100-healthcheck-banco-fora`. O relatório foi para `bugs/90100-healthcheck-banco-fora/`, e o `.specify/bugs/` não foi criado. Custo: US$ 0,27 na primeira execução, que parou certo na árvore suja, e US$ 0,67 na segunda. |
| — | Bundle `bugfix` na 1.2.0 | **funciona** | Num projeto vazio, `specify bundle add bugfix` deu `rc=0`: `Installed 'bugfix' (2 added, 0 already present)`, com a extensão `bug` e o workflow `bugfix`. A Task 2 usa a variante B (instalação pelo bundle). |

Achado: a primeira execução do item 3 parou porque a cópia tinha as mudanças do `ws speckit` sem commit. O `ws start` recusou a árvore suja, e o agente parou antes de criar a pasta, como manda o preset. Na segunda execução, com o commit feito, o fluxo seguiu.

Custo total do PoC: cerca de US$ 1,31.
