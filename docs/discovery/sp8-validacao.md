# SP8: validação real (Task 8)

Validação ponta a ponta do fim de fluxo único e dos nomes novos do SP8, com um repo fixture dedicado (`industria-logistica.wms.harness-test-dummy`), para não tocar nenhum repo de produção.

## Setup

- Repo fixture criado no Azure DevOps (projeto AReCO), com branches `main` e `homolog`, registrado permanentemente no manifesto do workspace: PR [17331](https://dev.azure.com/ARECO/AReCO/_git/industria-logistica.wms.workspace/pullrequest/17331) (manifesto, via `ws/sync`) e PR [17332](https://dev.azure.com/ARECO/AReCO/_git/industria-logistica.wms.workspace/pullrequest/17332) (mapas em `ferramentas-por-repo.yml` e `AGENTS.md`).
- **Bloqueio real encontrado:** o `ws start` falha de forma reprodutível (não é flakiness) ao sincronizar `industria-logistica.wms.awx.monorepo`, porque o `main` desse repo teve o histórico reescrito no Azure DevOps depois do último sync da `ws/sync`: o commit `da7a8b7e...` que o fetch raso busca como ponto de apoio não é mais ancestral do `main` atual (`aa12fa69...`). O cliente git reporta isso como `bad pack header`. Isso bloqueia `ws start`/`ws sync` para qualquer feature, bug ou refactor até alguém reparar o ponto de sync desse prefixo na `ws/sync`. **Ainda não reparado.**
- Por causa do bloqueio, os três testes abaixo tiveram a branch criada manualmente (checkout a partir da `ws/sync` real + merge da `harness/sp8-nomes`), pulando o `ws start`/`ws sync` de verdade. Isso significa que **o `ws start`/`ws sync` em si não foi validado** nesta rodada; só o fim de fluxo (`/ws-commit-push` → `/ws-pr-homolog` → `/ws-pr-main`) e os comandos de bug e refactor.
- Efeito colateral do atalho manual: a pasta da spec saiu como `specs/001-harness-teste-sp8/` em vez de `specs/ws-001-harness-teste-sp8/`, porque o `create-new-feature.sh` foi rodado direto, sem passar pelo `ws-feature.sh` (que aplica o prefixo `ws-`). **Não é um bug do harness**, é artefato do contorno manual.

## Teste 1 — Feature (`ws-001-harness-teste-sp8`)

Mudança: uma linha de boas-vindas no README do repo fixture.

- `/speckit-converge` encadeou sozinho para a oferta de PR (sem o usuário digitar `/ws-commit-push` nem `/ws-pr-homolog`).
- A primeira oferta foi recusada de propósito; `/ws-pr-homolog` rodado à mão depois reabriu a oferta e funcionou — valida o caso de uso "refazer a oferta recusada antes".
- PRs de homologação: [!17333](https://dev.azure.com/ARECO/AReCO/_git/industria-logistica.wms.harness-test-dummy/pullrequest/17333) (repo) e [!17334](https://dev.azure.com/ARECO/AReCO/_git/industria-logistica.wms.workspace/pullrequest/17334) (workspace). Mensagem no Chat de homologação conferida.
- Depois da aprovação, `/ws-pr-main` abriu os PRs para produção: [!17335](https://dev.azure.com/ARECO/AReCO/_git/industria-logistica.wms.harness-test-dummy/pullrequest/17335) e [!17336](https://dev.azure.com/ARECO/AReCO/_git/industria-logistica.wms.workspace/pullrequest/17336). Mensagem postada no espaço de produção do Chat, depois que o usuário incluiu a URL que faltava no `workspace.pr.ini` (ver achados).
- **Status: completo ponta a ponta**, incluindo a promoção para o main.

### Erro operacional (não do harness)

Durante o teste 2, a mesma worktree compartilhada (`C:\src\wms-workspace-sp8`) foi usada em paralelo por mim e pelo usuário, e a troca de branch de um lado atrapalhou o `/ws-pr-main` do outro ("há mudanças não commitadas"). Corrigido com `git stash` e uma worktree dedicada por teste daí em diante. Isso não é um achado sobre o harness, é um erro de processo da validação.

## Teste 2 — Bug (`hotfix/inc-20261025-teste-harness-sp8`)

Bug fabricado: o README do repo fixture não avisava que PRs ali são sempre de teste. Correção: acrescentar essa linha.

- `assessment.md`, `fix.md` (`Status: applied`) e `test.md` (`Result: verified`) escritos seguindo o template oficial do Spec Kit.
- `/speckit-bug-test` encadeou sozinho para a oferta de PR de homologação, que o usuário aceitou.
- PRs de homologação: [!17337](https://dev.azure.com/ARECO/AReCO/_git/industria-logistica.wms.harness-test-dummy/pullrequest/17337) e [!17338](https://dev.azure.com/ARECO/AReCO/_git/industria-logistica.wms.workspace/pullrequest/17338). Mensagem `fix(inc-20261025-teste-harness-sp8): ...`.
- **Status:** até os PRs de homologação abertos. Não foi promovido para o main (não era exigido pelo plano).

## Teste 3 — Refactor (`refactor/rf-20261025-teste-harness-sp8`)

Refactor fabricado: separar os avisos de teste do README para um `NOTAS-DE-TESTE.md` novo, sem perder nenhuma linha.

- **Exceção de caracterização aprovada pelo usuário** (repo só tem Markdown, sem framework de teste; verificação substituta foi a comparação linha a linha do antes/depois).
- **Achado real:** o `/speckit-refactor-assess` não confere se o estado que o diagnóstico descreve existe na base da branch. Os avisos que o assessment mandava mover só existiam nas branches da feature e do bug (ainda não mergeadas no main), não na base real da branch do refactor. O `/speckit-refactor-apply` parou sozinho ao perceber a divergência, em vez de inventar texto — o agente fez um commit de base próprio, copiando as duas linhas exatamente das branches de origem, e seguiu.
- `/speckit-refactor-verify`: `ok`, a comparação bateu (nenhuma linha perdida, só o título novo `# Notas de teste` como acréscimo).
- PRs de homologação: [!17339](https://dev.azure.com/ARECO/AReCO/_git/industria-logistica.wms.harness-test-dummy/pullrequest/17339) e [!17340](https://dev.azure.com/ARECO/AReCO/_git/industria-logistica.wms.workspace/pullrequest/17340). Mensagem `refactor(rf-20261025-teste-harness-sp8): ...`.
- **Status:** até os PRs de homologação abertos.

## Teste 4 — Revisão (`/ws-pr-review`)

Pendente: rodar `/ws-pr-review` num dos PRs do workspace abertos acima.

## Teste 5 — Limpeza

Pendente, como no SP7: abandonar os PRs e branches de teste dos três fluxos ao final.

## Achados para o time do harness

1. **Bloqueio real:** `ws start`/`ws sync` falham de forma reprodutível sincronizando `industria-logistica.wms.awx.monorepo` (histórico reescrito no `main` real desde o último sync da `ws/sync`). Bloqueia qualquer feature/bug/refactor até reparo. **Prioridade alta.**
2. `ws pr plano main` não confere se a branch atual é a mesma que ele mostra como origem, nem avisa de mudanças sem commit antes de abrir; o erro só aparece no `ws pr abrir main`.
3. `workspace.pr.ini` está sem a URL do espaço de produção do Google Chat (campo `producao` vazio). O usuário adicionou a URL ao vivo durante o teste, mas a mudança não foi commitada de propósito (arquivo tem segredo — key/token do webhook — e decisão de como entra no main fica com o time do harness).
4. `ws pr abrir homolog` não confirma no retorno se a postagem no Google Chat deu certo (observado nos testes 2 e 3); é preciso conferir no Chat à parte.
5. `ws atlas plano --gatilho converge` reportou `mudou: false` e `acao: nada` para o repo fixture mesmo com mudança ainda não commitada (teste 2) e depois com commit mas `split_gravado` vazio (teste 3) — parece não enxergar corretamente um repo novo, sem baseline de sync prévio.
6. `/speckit-refactor-assess` não confere se o estado descrito no diagnóstico existe de fato na base da branch (achado do teste 3, detalhado acima).
7. O template do `assessment.md` do refactor tem a seção "Para retomar", mas o `/speckit-refactor-assess` gerado não a inclui; foi preciso acrescentá-la manualmente no `/speckit-refactor-verify`.

## Não validado nesta rodada

- `ws start`/`ws sync` de verdade (bloqueados pelo achado 1).
- `/atlas-atualizar` e o mapeamento real de um repo pelo Atlas.
- A promoção para o main do bug e do refactor (ficou nos PRs de homologação).
