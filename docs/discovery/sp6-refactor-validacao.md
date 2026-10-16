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

## Regressão do bug com hooks nativos (spec 10.3)

Feita em 2026-10-16. Ambiente:
- workspace `C:\src\wms-workspace-e2e6`;
- origin bare `C:\src\wms-e2e6-origin.git`, com o main igual à `harness/speckit-1.2` (`56e5ec2ff`);
- espelhos `C:\src\wms-e2e6-conector.git` e `C:\src\wms-e2e6-linx.git`; o push para o Azure DevOps está bloqueado.

Bug plantado no espelho do conector: `ThrowIfLessThan(quantidade, 0)` no `FaturamentoCaixa`. Por decisão do usuário, o `assess` pulou o `atlas-atualizar` do início; o Atlas do envio (`converge`) rodou.

| Caso | Resultado | Evidência e custo |
|---|---|---|
| Bug com correção em 1 repo, hooks nativos | ok | **Hooks:** o `before_bug_assess` rodou a skill `speckit-ws-bug-start`, que criou a branch `hotfix/90101-caixa-embalada-quantidade-zero`; o `after_bug_assess` rodou a `speckit-ws-bug-sem-correcao` (`EXECUTE_COMMAND` no transcript), que mandou ler o `assessment.md` e rodar o `/speckit-bug-fix`; o `after_bug_test` rodou a `speckit-ws-bug-enviar`. **Relatórios:** `bugs/90101-…/{assessment,fix,test}.md`, sem `.specify/bugs/`. **Diagnóstico:** apontou a linha plantada. **Teste:** `test.md` em `partial` (teste unitário 7/7 e build ok; o ponta a ponta com o Linx ficou `not-run`). **Envio:** commit do Atlas do conector (`65939255`) e `fix(90101-…): caixa de faturamento volta a recusar quantidade zero` (`71409494`); a branch `hotfix/90101-…` chegou ao espelho do conector. **Custo:** US$ 0,75 (assess) + 1,01 (fix) + 4,81 (test com o Atlas do conector) + 4,90 (envio) = US$ 11,47 |

Achado do agente, registrado como fato: o `test.md` aponta que o único chamador de `FaturamentoCaixa.Criar` nunca passa quantidade zero. A guarda plantada, portanto, não explicaria um sintoma real de produção. Isso é coerente com o bug fictício e não afeta a validação do harness.
