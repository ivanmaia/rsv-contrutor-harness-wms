# Branch de teste por repo e ajustes de PR na feature (design)

Data: 2026-10-30. Processo: `superpowers:brainstorming`. Decisões tomadas com o usuário na conversa de 2026-10-30, a partir do feedback da feature `ws-002-chaves-centrais` (doc "Feedback ao harness: conflitos e revisões dentro da branch da feature", https://claude.ai/artifact/Bckn7BKWFtagQCxFrKEd6a).

## 1. Intenção e porquê

O `ws pr` abre os dois PRs de cada repo (para o ramo de teste e para o `main`) a partir da **mesma** branch, a `<branch>` que o `ws push` cria no repo (`tools/ws/pr/abrir.py`, `itens_do_plano`). Quando o PR de teste conflita com o ramo de teste (`homolog`, `release`, `develop`; `workspace.pr.ini`, seção `[teste]`), o harness não tem caminho: o `ws sync` só conhece o `main`, o `AGENTS.md` proíbe `git subtree` à mão e `git push` para os repos, e o doc da camada 2 manda abortar.

Na ws-002 o dev resolveu tudo direto nas branches dos repos, num clone separado: merges da homolog (27/10 e 29/10), commits de revisão (28/10) e o ajuste de um teste que veio da homolog (29/10). Consequências conferidas em 2026-10-30:

- A `ws-002-chaves-centrais` do AWX no Azure tem o merge da homolog (`4df5665`) e **344 commits fora do `main`**, quase todos de outras features da homolog (PRs 17481, 17474, 17330...). O PR dela para o `main` levaria tudo isso. O usuário quer que o PR do `main` tenha **só a mudança da feature**.
- As três subtrees na branch do workspace diferem das branches dos repos.
- O feedback diz que o próximo `ws push` "desfaz trabalho". **Não é o que acontece:** o `subtree push` faz `git push` sem force (`tools/ws/vendor/git-subtree-ws`, linha 1112) e é recusado com `non-fast-forward`, numa mensagem pouco clara.

A regra que o feedback pede, e que o usuário adota: **todo ajuste de um PR de feature, bug ou refactor é feito na branch da feature, no workspace, e sai pelo `ws push`.**

## 2. Objetivos, não objetivos e antiobjetivos

**Objetivos:**
- Conflito do PR de teste com o ramo de teste resolvido no workspace, sem clone e sem `git subtree` à mão, sem que o ramo de teste entre na branch que vai para o `main`.
- Ajustes de revisão com caminho escrito (camadas 1 e 2) e uma skill do dev para tratar os comentários dos PRs.
- `ws push` para com explicação quando a branch do repo tem commits que não estão no workspace.
- A ws-002 corrigida: as três `<branch>` só com a mudança da feature, iguais às subtrees do workspace, prontas para o PR do `main`.

**Não objetivos:**
- Um comando permanente para trazer de volta o que foi feito direto na branch do repo (decisão do usuário: só neste caso, à mão, na ws-002).
- Mudar o PR do workspace: ele continua saindo da branch da feature, para a `homolog` do workspace e para o `main`.
- Mudar o `ws sync`, o `ws start` ou a sincronização com o `main` dos repos.
- Marcar threads como resolvidos no Azure (o dev marca "Resolved").

**Antiobjetivos:**
- O ramo de teste, ou a resolução de um conflito com ele, chegar à `<branch>`, à branch da feature, à spec ou ao Atlas.
- O dev precisar decidir, a cada entrega, se usa ou não a branch de teste.
- O `ws push` reescrever com força uma branch de repo sem o dev pedir.

## 3. Decisões

### 3.1 A branch `<branch>-teste`, sempre

- Para cada repo da entrega, o PR para o ramo de teste sai **sempre** de `<branch>-teste`, com ou sem conflito. Ela existe só no repo: é a `<branch>` mais merges do ramo de teste daquele repo, com as resoluções de conflito.
- O PR para o `main` continua saindo da `<branch>`, que é sempre o split da branch da feature e nada mais.
- Vale para feature, bug e refactor, porque todos passam por `ws push` e `ws pr`. Cada card de fatia tem o seu PR de teste e, portanto, a sua `-teste`. A branch de subida (`-rollout`) não tem PR de teste e não usa `ws teste`; ela junta as `<branch>` limpas dos cards. *(decisão minha)*
- Segunda rodada de homologação: o `ws teste` parte da `-teste` do origin, se ainda existir, ou da `<branch>`. No AWX os PRs para a `homolog` são completados com merge (sem squash), então a resolução anterior fica no histórico do ramo de teste. Num repo que complete com squash, o conflito pode voltar a cada rodada; é limitação conhecida, sem tratamento. *(decisão minha)*
- Se alguém usar o botão de resolver conflito do Azure no PR de teste, a resolução cai na `-teste`, e não na `<branch>`.

### 3.2 Comando `ws teste` (CLI, em português como o resto do `tools/ws/ws`)

- `ws teste`: para cada repo alterado na branch atual (mesma regra do `ws_changed_prefixes`):
  1. confere que a `<branch>` no repo é exatamente o split da feature (o `ws push` já rodou e nada mudou depois); se não for, para e manda rodar `/ws-commit-push`;
  2. busca o ramo de teste do repo (`cfg.ramo_teste(prefixo)`) e a `-teste` do repo, se existir;
  3. parte da `-teste` do origin do repo, ou da `<branch>` na primeira vez;
  4. faz o merge da `<branch>` atual e depois o do ramo de teste (pula o que já é ancestral);
  5. envia a `-teste` sem force.
- **Conflito:** o comando para naquele repo, com o merge em andamento numa worktree em `.ws/teste/<nome do repo>/` (ignorada pelo git, como o `.ws/revisao/`). Ele lista os arquivos em conflito em dois grupos: os que a feature toca (aparecem no diff `base...HEAD` daquele prefixo) e os que ela não toca. O dev resolve lá e roda `ws teste continuar`, que confere que não sobrou marcador de conflito, faz o commit, envia e segue para os repos restantes. `ws teste abortar` descarta a worktree sem enviar nada.
- Repos sem conflito são enviados mesmo quando outro repo para no conflito.
- Mensagens de commit em português, no padrão `ws: ...` (ex.: `ws: traz homolog para <branch>-teste`), sem atribuição.

### 3.3 O `ws push` mantém a `-teste` em dia

- Depois de enviar a `<branch>` de um repo, se a `-teste` dele existir no origin, o `ws push` faz o merge da `<branch>` nova nela (sem trazer o ramo de teste de novo) e a envia. É o caminho dos ajustes de revisão: o dev corrige na feature, `/ws-commit-push`, e os dois PRs se atualizam.
- Se esse merge conflitar (o ajuste mexeu nas linhas que tinham conflitado), a `<branch>` já foi enviada; o `ws push` para naquele repo e manda rodar `ws teste`, que conduz a resolução como em 3.2.

### 3.4 Guarda no `ws push`

- Antes de enviar qualquer repo (vale a regra atual "ou vai tudo, ou nada"), para cada prefixo: se a `<branch>` já existe no repo e a ponta dela não está no histórico do split que vai ser enviado, o `ws push` para sem enviar nada.
- A mensagem lista, por repo, os commits que estão só no repo (sha curto, autor, data, assunto) e explica a causa provável (alguém fez commit direto na branch do repo, inclusive pelo botão de aplicar sugestão do Azure).
- **Saída (decisão do usuário):** o dev reproduz a mudança na feature, confirma que ela está lá e roda `ws push --sobrescrever <repo>` (aceita mais de um repo). Só os repos nomeados são enviados com `--force-with-lease`, contra a ponta que a guarda mostrou; os outros seguem a regra normal. Se a ponta do repo mudou de novo desde a guarda, o push é recusado e o dev vê a guarda outra vez. Sem `--sobrescrever`, nada é enviado com força.

### 3.5 Mudanças no `ws pr`

- `ws pr abrir homolog` roda o `ws teste` antes de abrir (como o `abrir main` já roda o `ws push`); se ele parar num conflito, nenhum PR é aberto e a saída diz o que fazer. Os PRs dos repos saem de `<branch>-teste`; o do workspace, da branch da feature.
- `ws pr plano homolog` e os links `pullrequestcreate` mostram a origem certa por item.
- `ws pr plano main`: o aviso de "PR para o ramo de teste ainda aberto" procura PRs com origem `<branch>-teste`.
- `recria_branches` (no `abrir main`): para os repos, deixa de recriar a `<branch>` a partir do PR de teste completado, porque a origem desse PR agora é a `-teste` e traria o ramo de teste. Se a `<branch>` não existir, o `ws push` seguinte a recria a partir da feature. O comportamento para o workspace não muda.
- `ws pr revisao` (usado pela `/ws-pr-review`): no PR de teste, acha os PRs dos repos pela origem `-teste`. O diff revisado de cada repo continua sendo o da feature (`<branch>` contra a base), sem o ramo de teste.
- A skill `/ws-pr-homolog` ganha a condução do conflito do `ws teste` (lista dos dois grupos; para os arquivos que a feature não toca, sugere ficar com a versão do ramo de teste; o dev decide). O passo 6 deixa claro que a `-teste` pode ser apagada ao completar o PR; a `<branch>` e a branch do workspace não.
- Transição: um repo que já tem PR ativo de `<branch>` para o ramo de teste (fluxo antigo) mantém esse PR; o `ws pr` avisa e não abre outro da `-teste` para ele. *(decisão minha; ver seção 5)*

### 3.6 Skill `/ws-pr-resolve-comments` (do dev)

Nome escolhido pelo usuário. Par da `/ws-pr-review`: um lado revisa, o outro resolve.

- **Entrada:** o link de um PR, ou nada. Sem link, usa os PRs ativos da branch atual: os dos repos (origem `<branch>` e `<branch>-teste`) e o do workspace.
- **Leitura:** threads ativos, que não são de sistema e sem resposta do dev depois do último comentário. Um comando do CLI monta o contexto em JSON (no molde do `ws pr revisao`), com o caminho no workspace (`repos/<prefixo>/...`) de cada comentário de arquivo.
- **Análise:** para cada comentário, propõe "aplicar" ou "não aplicar", com o motivo, olhando a spec (ou o assessment/rollout-plan), a constitution e o código. Mostra a lista; **o dev confirma ou muda antes de qualquer edição.** Um comentário sobre uma linha que só existe na resolução de conflito da `-teste` é apontado como tal e tratado pelo `ws teste`, não na feature.
- **Correção:** aplica o que foi aceito na branch da feature; `/speckit-converge` quando muda o comportamento da spec; Atlas quando toca contrato; depois `/ws-commit-push`.
- **Resposta:** só depois do push com sucesso, responde em cada thread, em português: o que foi feito (com o commit) ou por que não foi feito. Um comando do CLI publica as respostas a partir de um JSON (no molde do `ws pr comentar`).
- **Status:** não mexe. O dev marca "Resolved".

### 3.7 Docs e regras

- `AGENTS.md`: a regra "todo ajuste de PR é feito na branch da feature e sai pelo `ws push`"; não usar os botões do Azure de aplicar sugestão nem de resolver conflito no PR do `main`.
- Camada 1 (`docs/harness/1-comecar.md`): o caminho dos ajustes de revisão (`/ws-pr-resolve-comments`) e o do conflito com o ramo de teste (`/ws-pr-homolog` / `ws teste`), mais as linhas no "Quero…" do README.
- Camada 2 (`2-quando-da-errado.md`): as mensagens novas (conflito no `ws teste`, conflito da `-teste` no `ws push`, guarda do `ws push`, `<branch>` diferente do split no `ws teste`).
- Camadas 3 e 4: o `ws teste` e a skill nova onde o harness lista comandos e skills.
- ADR 0001: adendo 7 com a `-teste`. A constitution não muda. *(decisão minha)*

### 3.8 Correção da ws-002 (uma vez, à mão, nesta execução)

É a **primeira tarefa** da execução (decisão do usuário), para o dev seguir com o `/ws-pr-main` sem esperar o código novo. Usa só git e as ferramentas atuais. Os PRs 17266, 17267 e 17268 para os ramos de teste já foram completados e ficam como estão. Para cada um dos três repos (AWX, `servidor.backend`, `servicos-linx-wms`), com a confirmação do usuário antes de reescrever cada branch:

1. Listar os commits da `ws-002-chaves-centrais` do repo que não estão no workspace nem vieram do ramo de teste.
2. Trazer para a feature, no workspace, só os commits de revisão (AWX e `servidor.backend`: 28/10; `servicos-linx-wms`: os dois de 28/10), mantendo o autor original. Ficam de fora os merges do ramo de teste (27/10 e 29/10) e o ajuste de 29/10 no AWX do teste que veio da homolog. Antes, conferir que a branch local está sem mudança pendente e se já há PR ativo da `<branch>` para o `main` em algum dos repos.
3. Reenviar a `<branch>` limpa, igual ao split da feature, com `--force-with-lease` (sem `-teste`).
4. Conferir que as três branches dos repos e as subtrees do workspace têm o mesmo conteúdo, e seguir com `/ws-pr-main`.

A branch `ws-002-chaves-centrais` do workspace é do usuário e está só em `C:\src\wms-workspace`.

## 4. Validação

Ponta a ponta no Azure real com o repo fixture `industria-logistica.wms.harness-test-dummy` (SP8), registrada em `docs/discovery/`: PR de teste sem conflito; conflito com a `homolog` resolvido pelo `ws teste` (arquivo tocado e não tocado pela feature); ajuste de revisão pelo `ws push` atualizando os dois PRs; ajuste que reconflita; guarda do `ws push` com um commit feito pelo Azure e a saída por `--sobrescrever`; `/ws-pr-resolve-comments` num PR com comentários reais; PR do `main` sem nada da `homolog`. PRs de teste abandonados e branches apagadas ao fim. O primeiro envio de uma `-teste` num repo real (para conferir que nenhuma política de nome barra o sufixo) só com a confirmação do usuário.

## 5. Decisões minhas (para o usuário conferir)

- Transição: PR de teste ativo do fluxo antigo é mantido (3.5).
- Constitution sem mudança; só `AGENTS.md`, docs e adendo à ADR (3.7).
- Fatias e segunda rodada de homologação (3.1).

## 6. Deixado para quem implementa

- Profundidade de histórico a buscar para o merge do ramo de teste (o `ws` busca raso; o merge precisa da base comum).
- Formato dos JSONs e nomes dos subcomandos do CLI da skill nova.
- Qual commit citar na resposta do thread (o do workspace ou o do repo).
