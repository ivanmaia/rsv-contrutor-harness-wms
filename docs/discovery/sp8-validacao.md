# SP8: validação real (Task 8)

Validação ponta a ponta do fim de fluxo único e dos nomes novos do SP8, com um repo fixture dedicado (`industria-logistica.wms.harness-test-dummy`), para não tocar nenhum repo de produção.

## Setup

- Repo fixture criado no Azure DevOps (projeto AReCO), com branches `main` e `homolog`, registrado permanentemente no manifesto do workspace: PR [17331](https://dev.azure.com/ARECO/AReCO/_git/industria-logistica.wms.workspace/pullrequest/17331) (manifesto, via `ws/sync`) e PR [17332](https://dev.azure.com/ARECO/AReCO/_git/industria-logistica.wms.workspace/pullrequest/17332) (mapas em `ferramentas-por-repo.yml` e `AGENTS.md`).
- **Bloqueio real encontrado:** o `ws start` falha de forma reprodutível (não é flakiness) ao sincronizar `industria-logistica.wms.awx.monorepo`. **Causa confirmada pelo usuário: o repositório foi excluído e recriado no Azure DevOps**, não um `force-push` no `main` dele. Por isso o commit `da7a8b7e...`, que o fetch raso do `ws start` usa como ponto de apoio, não existe mais em lugar nenhum do repositório novo — não há ancestral comum entre o histórico antigo (o que a `ws/sync` já sincronizou) e o novo. O cliente git reporta isso como `bad pack header`/`TF401035: The object ... does not exist`. `git ls-remote` e `git fetch` simples funcionam normalmente (não dependem de histórico compartilhado); só o fetch raso específico do `ws start`/`ws sync` falha. Isso bloqueia `ws start`/`ws sync` para qualquer feature, bug ou refactor até alguém reparar. **Ainda não reparado — e o reparo não é um simples ajuste de ponteiro: como não há ancestral comum, o prefixo provavelmente precisa ser readicionado do zero na `ws/sync` (como um repo novo), abandonando a linha de subtree antiga dele.**
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

Rodado no PR do workspace do refactor ([!17340](https://dev.azure.com/ARECO/AReCO/_git/industria-logistica.wms.workspace/pullrequest/17340)).

- Os cinco subagentes (conformidade, contratos, regras, defeitos e testes, banco) rodaram em paralelo; o de banco não achou nada (o PR não tem `.sql` nem migração).
- 13 achados brutos, deduplicados para 10, mostrados numa lista única com gravidade, repo, arquivo e linha.
- O usuário escolheu publicar só os achados 1 e 2; os outros 8 ficaram só na lista, confirmando que **o harness não publica nada sem a escolha explícita do revisor** ("não aprova, não reprova, não vota").
- **Status: completo.**

### Achados da revisão (achados 3 a 10, sem publicar, registrados aqui para o time do harness)

- **3 (conformidade, média):** o "antes" do `assessment.md` do refactor é sintético (criado por um commit de base feito só para o teste); contra a base real da branch, o PR só cria o `NOTAS-DE-TESTE.md`, então a verificação do `verify.md` não prova nada sobre a mudança de fato. Efeito do atalho do teste, não do harness em si — mas achado real de como a revisão lê as coisas.
- **4 (conformidade, média):** se a `ws-001` e o bug forem mergeados depois, as frases que eles escrevem no `README.md` ficam duplicadas no `NOTAS-DE-TESTE.md`. Também efeito dos três testes serem paralelos e não sequenciais.
- **5 (conformidade, baixa):** o `ws atlas concluir` do refactor regenerou um derivado do Atlas do `servidor.backend`, sem relação com a mudança do refactor, sem isso ser citado na descrição do PR.
- **6 (regras, baixa):** sobras de nomes antigos nas regras já renomeadas: a constitution ainda diz "No desacoplar", o `AGENTS.md:96` ainda diz "antes do validar", e a linha 95 do `AGENTS.md` ainda diz que o verify "oferece o envio" (as outras já dizem "segue a skill `/ws-commit-push`").
- **7 (contratos, baixa):** o ADR 0003 ainda cita `refactors/fatias.md`, que virou `refactors/slices.md` no SP8.
- **8 (contratos, baixa):** o Adendo 9 do ADR 0001 diz que "o CLI não muda", mas `abrir.py` só reconhece o sufixo novo `-rollout`; uma branch `-subida` criada antes do merge do SP8 deixaria de ser reconhecida.
- **9 (defeitos, baixa):** em `test_nomes_antigos.sh`, o `|| true` depois do `git grep` esconde uma falha de verdade (código 128, erro de regex ou de repo) como se fosse "sem achados".
- **10 (defeitos, baixa):** falta um teste que fixe o nome da branch nova `refactor/eap-1-1-4-remove-flag`.

**O achado 1** (publicado no PR) é o mais importante: o PR de refactor carrega ~107 arquivos do harness vindos do merge da `harness/sp8-nomes`, que ainda não está no main. Se esse PR for completado antes do PR do SP8, a reescrita do harness entra "de carona", sem a revisão própria dele — e contraria a regra de não mexer no harness durante o trabalho. **Isso vale para os PRs dos três testes**, não só o do refactor: nenhum deles deve ser completado antes do PR do `harness/sp8-nomes` ir para o main.

## Teste 5 — Limpeza

- Os 8 PRs de teste (!17333 a !17340) foram abandonados no Azure DevOps.
- As 6 branches de teste (`ws-001-harness-teste-sp8`, `hotfix/inc-20261025-teste-harness-sp8`, `refactor/rf-20261025-teste-harness-sp8`) foram apagadas no origin dos dois repos (`industria-logistica.wms.workspace` e `industria-logistica.wms.harness-test-dummy`) e localmente no worktree `wms-workspace-sp8`.
- As worktrees extras (`wms-workspace-sp8-bug`, `wms-workspace-sp8-refactor`), criadas para não colidir com o trabalho do usuário na worktree principal, foram removidas do controle do git; as pastas em disco ficaram presas por um processo (provavelmente o VS Code) e precisam ser apagadas à mão depois de fechá-lo.
- O repo fixture `industria-logistica.wms.harness-test-dummy` **ficou**, como decidido: é permanente, para validações futuras do harness.
- **Status: completo** (exceto a sobra de disco das duas pastas, sem efeito no harness).

## Resumo

Os cinco passos da Task 8 foram cumpridos: feature, bug e refactor validados ponta a ponta (até a promoção para o main na feature; até os PRs de homologação no bug e no refactor), a revisão de PR validada com achados reais publicados seletivamente, e a limpeza feita. O achado mais importante — o `ws start`/`ws sync` bloqueado pelo histórico reescrito do AWX — segue em aberto e bloqueia qualquer entrega real até ser reparado; não é um problema do SP8, mas impede validar o `ws start` de verdade nesta rodada.

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
