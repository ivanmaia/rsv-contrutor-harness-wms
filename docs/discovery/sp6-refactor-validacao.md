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
| Bug com correção em 1 repo, hooks nativos | ok | **Hooks:** o `before_bug_assess` rodou a skill `speckit-ws-bug-start`, que criou a branch `hotfix/90101-caixa-embalada-quantidade-zero`; o `after_bug_assess` rodou a `speckit-ws-bug-sem-correcao` (`EXECUTE_COMMAND` no transcript), que mandou ler o `assessment.md` e rodar o `/speckit-bug-fix`; o `after_bug_test` rodou a `speckit-ws-bug-enviar`. **Relatórios:** `bugs/90101-…/{assessment,fix,test}.md`, sem `.specify/bugs/`. **Diagnóstico:** apontou a linha plantada. **Teste:** `test.md` em `partial` (teste unitário 7/7 e build ok; o ponta a ponta com o Linx ficou `not-run`). **Envio:** commit do Atlas do conector (`65939255`) e `fix(90101-…): caixa de faturamento volta a recusar quantidade zero` (`71409494`); a branch `hotfix/90101-…` chegou ao espelho do conector. **Custo:** cerca de US$ 4,90. O `total_cost_usd` de uma sessão retomada com `--resume` é acumulado, então vale o maior valor da sessão, e não a soma (a soma de antes, US$ 11,47, contava em dobro) |

Achado do agente, registrado como fato: o `test.md` aponta que o único chamador de `FaturamentoCaixa.Criar` nunca passa quantidade zero. A guarda plantada, portanto, não explicaria um sintoma real de produção. Isso é coerente com o bug fictício e não afeta a validação do harness.

## Ponta a ponta da vertente de refactor (spec 10.1, item 4, e 10.3)

Feito em 2026-10-17 e 2026-10-18. Ambiente:
- workspace `C:\src\wms-workspace-e2e6`, com o main igual à `harness/refactor`;
- espelhos locais do conector, do servicos-linx-wms, do servidor.backend e do awx.monorepo; o push para o Azure DevOps está bloqueado;
- os PRs foram simulados por merge nos espelhos e no main do workspace (`C:\src\wms-e2e6-pr.sh`).

Padrão do caminho novo: o **real**, explicado pelo usuário (`docs/discovery/sources/arquitetura-transicao-linx.md`). A rota é legado → `AWX.IntegracaoLegadoWMS` → `AWX.ERP.Connector` → `servicos-linx-wms`.

Por decisão do usuário (2026-10-17), a qualidade vem antes do custo. Os casos que tinham sido pulados para economizar foram feitos.

| Caso | Resultado | Evidência |
|---|---|---|
| Tipo 1 com caracterização (90201, conector) | ok | Hooks `before_`/`after_refactor_assess` e `after_refactor_verify`. O commit `test(…): caracterização` veio antes do refactor, com 5 testes xUnit novos. **1º verify:** `falhou`, por 2 testes que já falhavam (o bug plantado na Task 3); o agente recusou o envio. **Depois de ajustar o ambiente:** verify ok, e o envio fez o commit do Atlas e `refactor(90201-…): …`, com a branch no espelho |
| Tipo 1, teste de caracterização alterado | ok | Alterei o teste à mão e rodei o `verify` numa sessão nova: `falhou`, com o arquivo apontado. O agente não ajustou o teste nem enviou |
| Tipo 1 com exceção (90204, `PermissaoAttribute` do servidor) | ok | **Duas tentativas sem exceção:** o agente preferiu caracterização viável, numa delas com uma `DbConnection` falsa (90202, descartado). **No 90204:** o dev recusou referenciar o projeto web nos testes, e o agente registrou a exceção (motivo, roteiro manual antes e depois, aprovação `pendente`). O `apply`, numa sessão nova, pediu a aprovação antes de mexer no código; com o sim, gravou `sim, 2026-10-18`, fez o refactor sem commit de caracterização, e o `verify` deu ok com a verificação manual. Parado antes do envio |
| Não é refactor (90203) | ok | Veredito `reclassificar`, commit `docs(…): diagnóstico, não é refactor`, push só do workspace |
| Tipo 3, M1 (90301, servidor → IntegracaoLegadoWMS → ERP.Connector → servicos-linx-wms) | ok | **Assess:** seguiu o padrão real, com a chave `LinxCodigoBarraHelveticaOrigem` em modo sombra e 5 critérios de M3. **Apply:** endpoints novos nas três peças e o servidor atrás da chave; builds e testes nos três repos, inclusive o MSBuild do servidor. **Defeito real achado:** o Atlas do envio pegou que o `IntegracaoLegadoWMS` chamava o Connector sem `X-API-KEY`; o agente parou e o dev escolheu corrigir só a fatia. **Revisão do agente:** trouxe retry, `SECRETS.md` e o SKU na resposta. **Envio:** commit do Atlas dos três repos e `refactor(…)`, com a branch nos três espelhos |
| Aviso e pendentes | ok | O `pendentes` mandou "virar a chave e rodar /speckit-refactor-validar"; o `ws start` mostrou `1 fatia(s) do desacoplamento linx aguardando validação desde 2026-10-17` |
| Portão 1 (desacoplar sem M3) | ok | Numa branch `-desacoplar` criada à mão, o comando parou no M1, sem mexer em nada |
| `validar` que falha, em sessão nova | ok | O agente percebeu o período de sombra no futuro e pediu confirmação. Depois gravou o `validacao.md` com `falhou`, o marco `M3-falhou` e o commit `docs(…): validação sem sucesso`, com push só do workspace |
| Nova rodada `-r2` | ok | A branch `refactor/…-r2` foi criada pelo hook, e o `assessment.md` ganhou a seção "Rodada 2". O apply acrescentou testes do SKU com zero à esquerda nas três peças, o verify deu ok e o M1 foi marcado de novo, com a convivência atualizada depois da correção do harness. O envio criou a branch `-r2` nos três espelhos |
| `validar` ok, em sessão nova | ok | Branch `refactor/…-desacoplar-2` (a `-desacoplar` da falha estava no origin), `validado`, `M3` |
| Portão 2 (acesso plantado) | ok | O `desacoplar` parou apontando `RelatorioHelvetica.cs:5`. Quem achou o acesso foi a busca no código: o Atlas classificou a mudança como irrelevante |
| `desacoplar` ok | ok | O comando removeu do servidor o caminho antigo, a chave e o decorador. Build ok; os 13 testes da fatia passaram; as 620 falhas restantes já estavam na linha de base. O envio fez o Atlas do servidor e `refactor(…): desacopla …`, e a fatia ficou em `M4`. Depois do merge, o `pendentes` mostrou `nenhuma fatia pendente` |

### Achados de desenho, corrigidos com teste na `harness/refactor`
1. A cópia instalada da extensão ficava velha depois de mudar a fonte (`test_extensao_refactor_instalada_igual_a_fonte`).
2. O csproj antigo entra no commit de caracterização e precisa crescer: o confere aceita arquivo de projeto que só ganhou linhas.
3. Testes que já falhavam antes do refactor: linha de base no apply e no verify; a regra III foi emendada por decisão do usuário, com o adendo "o teste corrigido tem de passar".
4. `ws refactor marco` repetido no mesmo marco (verify rodado de novo) não falha mais.
5. O M1 da nova rodada passou a atualizar a data de convivência.

### Pendências fora do harness, registradas pelo agente para outros times (só como fato)
- **AWX:** o `IntegracaoLegadoWMS` não tem `ExceptionHandlingMiddleware`; os clients de Contagem e Auditoria não mandam `X-API-KEY`; `AWX.slnx` e `AWX.ArchitectureTests` já não compilavam.
- **Servidor:** o ramo OnDemand do `AssociarProdutoRastreadoServicoDominio` não retorna ao achar o produto (A-44 do Atlas); o vstest só carrega o NLog com `/InIsolation`.

### Custo
O `total_cost_usd` de uma sessão retomada é acumulado, e por isso conta o maior valor de cada sessão. O total ficou em cerca de **US$ 116**. As sessões mais caras foram:
- o envio do tipo 3, com builds e testes de três repos e o Atlas de três repos repetidos três vezes: US$ 40;
- a validação que falhou, cujo `ws start` mapeou o Atlas de três repos que tinham mudado: US$ 48.
