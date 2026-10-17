# SP6: validação da vertente de refactor

Spec: `docs/superpowers/specs/2026-10-16-sp6-refactor-design.md`. Plano: `docs/superpowers/plans/2026-10-16-sp6-refactor.md`.

## PoC do Spec Kit 1.2.0 (spec 10.1, itens 1 a 3)

Feito em 2026-10-16, numa cópia descartável do workspace em `%TEMP%\sp6-poc`, clonada do `main` local (`a996df32c`) e sem origin.

| # | Item | Resultado | Evidência e custo |
|---|---|---|---|
| 1 | Atualização sem quebrar `multirepo` e `bugs` | ok | O `ws speckit` com `VERSION` = 1.2.0 deu `rc=0`. A skill `speckit-specify` mantém "Regras do workspace multi-repo"; o `spec-template` resolvido mantém "Repos afetados"; a skill `speckit-bug-assess` mantém o preâmbulo do preset `bugs`. A extensão `bug` instalada é a 1.0.1: o `speckit.bug.assess` ainda cita `.specify/bugs/` (7 vezes) e dispara `before_bug_assess`, e o `speckit.bug.test` dispara `after_bug_test`. A suíte offline deu 275 ok e 0 falha. |
| 2 | Extensão nossa com hook de nome próprio | ok | Duas extensões de brinquedo (`poc` e `pocws`) instalaram com `extension add --dev` sem aviso. O `.specify/extensions.yml` registrou `before_poc_ola` e `before_bug_assess` → `speckit.pocws.marca`. No `claude -p "/speckit-poc-ola"`, o agente rodou o hook (gravou `marca.txt`) e respondeu `olá concluído`. Custo: US$ 0,37. |
| 3 | Hook nativo `before_bug_assess` | ok | No `/speckit-bug-assess` (work item fictício 90100), o hook `before_bug_assess` gravou o `marca.txt` e o preset criou a branch `hotfix/90100-healthcheck-banco-fora`. O relatório foi para `bugs/90100-healthcheck-banco-fora/`, e o `.specify/bugs/` não foi criado. Custo: US$ 0,27 na primeira execução, que parou certo na árvore suja, e US$ 0,67 na segunda. |
| — | Bundle `bugfix` na 1.2.0 | **funciona** | Num projeto vazio, `specify bundle add bugfix` deu `rc=0`: `Installed 'bugfix' (2 added, 0 already present)`, com a extensão `bug` e o workflow `bugfix`. A Task 2 usou a variante B (pelo bundle). **A revisão do PR 1 a derrubou:** o catálogo da 1.2.0 baixa o `bundle.yml` do `main` do Spec Kit, não da tag, e o `bundle add` recusa reinstalar quando o `bundle-records.json` registra outra versão. A instalação voltou a ser separada, com o workflow fixado na tag `v$ver`. |

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

## Ponta a ponta da vertente de refactor (spec 10.1, item 4, e 10.3), parcial em 2026-10-17

Ambiente: o mesmo `C:\src\wms-workspace-e2e6`, agora com o main igual à `harness/refactor`, e espelhos locais também do `servidor.backend` e do `awx.monorepo`. Por decisão do usuário, os comandos pularam o `atlas-atualizar` do início da branch; o Atlas do envio (`converge`) rodou.

Padrão do caminho novo: o **real**, explicado pelo usuário (`docs/discovery/sources/arquitetura-transicao-linx.md`). A rota é legado → `AWX.IntegracaoLegadoWMS` → `AWX.ERP.Connector` → `servicos-linx-wms`.

| Caso | Resultado | Evidência e custo |
|---|---|---|
| Tipo 1 com caracterização (90201, conector) | ok | Hooks `before_refactor_assess`, `after_refactor_assess` e `after_refactor_verify` rodaram as skills da `ws`. Houve o commit `test(90201-…): caracterização` antes do refactor e 5 testes xUnit novos. **1º verify:** `falhou`, por 2 testes que já falhavam (o bug plantado na Task 3 ainda estava no espelho); o agente recusou o envio, pela regra III. **Ajuste do ambiente:** merge do PR do hotfix no espelho, `ws sync` e merge da `ws/sync`. **2º verify:** ok. **Envio:** commit do Atlas e `refactor(90201-…): …`, com a branch no espelho do conector. US$ 17,42 |
| Tipo 1 com exceção (90202) | **não exercitado** | O agente achou caracterização viável (uma `DbConnection` falsa) e não propôs exceção. O caminho da exceção segue sem teste ponta a ponta. US$ 1,80 |
| Teste de caracterização alterado | pulado | Coberto pelos 6 testes offline do `ws-refactor-confere.sh`; o comportamento do `verify` diante de uma falha apareceu no 1º verify do 90201 |
| Não é refactor (90203) | ok | Veredito `reclassificar`, commit `docs(90203-…): diagnóstico, não é refactor`, branch no origin do workspace e não no espelho do conector. US$ 1,24 |
| Tipo 3, M1 (90301, servidor → IntegracaoLegadoWMS → ERP.Connector → servicos-linx-wms) | ok, depois de duas correções no harness | **Assess:** seguiu o padrão real; propôs a chave `LinxCodigoBarraHelveticaOrigem` em modo sombra e 5 critérios de M3. **Apply:** endpoints novos nas três peças e o servidor atrás da chave. Os builds e os testes da fatia passaram nos três repos, inclusive o MSBuild do servidor (.NET Framework, com `nuget restore`). **1º verify:** `falhou`, porque o csproj antigo do projeto de testes, que estava no commit de caracterização, ganhou linhas. **Correções no harness:** o confere passou a aceitar arquivo de projeto que só cresce, e o apply e o verify passaram a usar a linha de base de falhas antigas (623 no servidor, 44 no IntegracaoLegadoWMS, 6 no servicos-linx-wms). **2º verify:** ok, com a linha da fatia em `M1` e a seção "Para retomar" preenchida. **Atlas do envio:** o mapeamento do AWX achou um defeito real no caminho novo, que o envio não cobriu: a `IntegracaoLegadoWMS` chama o ERP Connector sem o `X-API-KEY`, e os testes passaram porque o host de teste usa um Connector falso. O agente parou antes do envio e pediu decisão. US$ 52,90 (assess 1,92, apply 10,98, verify 11,97, verify2 28,02) |

**Achados de desenho, corrigidos com teste na `harness/refactor`:**
- a cópia instalada da extensão ficou velha depois de mudar a fonte (`test_extensao_refactor_instalada_igual_a_fonte`);
- o csproj antigo no commit de caracterização (`test_refactor_confere_aceita_csproj_que_so_cresceu`);
- os testes que já falhavam antes do refactor (`test_verify_compara_com_a_linha_de_base_de_falhas`).

**Para o usuário decidir:** se a regra III da constitution ganha a mesma ressalva da linha de base.

**Custo até aqui:** US$ 73,35.
