# Sincronização dos repos pela branch `ws/sync` (design)

Data: 2026-10-15. Processo: `superpowers:brainstorming`, caminho arquitetural. Decisões tomadas com o usuário na conversa de 2026-10-15. Entra no workspace como adendo 6 do ADR 0001.

## 1. Problema

O `ws start` sincroniza os subtrees no `main` local do workspace e faz push direto no `main` (ADR 0001, seção 3). Em 2026-10-13 e 2026-10-14, o `main` do `industria-logistica.wms.workspace` ganhou duas políticas bloqueantes ("Required reviewers" e "Minimum number of reviewers"). Desde então, o Azure DevOps recusa o push direto de quem não tem a permissão "Bypass policies when pushing".

Efeitos, vistos num `/speckit-bug-assess` em 2026-10-15:
- todo `/speckit-specify` e `/speckit-bug-assess` de quem não tem bypass falha ao criar a branch;
- o `main` local fica com os commits de sync à frente do origin (13 no caso relatado), e a branch não é criada;
- a mensagem diz "Se outro dev enviou o main antes, rode git pull --no-rebase origin main", o que culpa outro dev e manda um comando que não resolve.

## 2. Objetivo e critério de sucesso

O `ws start` volta a funcionar para quem não tem bypass, sem que nada chegue ao `main` sem PR, nem a sincronização dos repos.

**Sucesso:**
- o teste que reproduz o relato (`main` do origin recusando push, seção 7.1, teste 1) passa;
- dois devs sincronizando ao mesmo tempo não geram conflito de merge em `repos/`;
- o `ws push`, o converge e o Atlas continuam enxergando só as mudanças da feature;
- a suíte do `tools/ws/tests` continua 100% verde;
- a validação no Azure DevOps real (seção 7.2) passa.

## 3. Decisões tomadas com o usuário

| Decisão | Valor |
|---|---|
| Push direto no `main` | Não. As políticas do `main` ficam como estão, e nada chega a ele sem PR (opção 2 da conversa, contra dar bypass aos devs) |
| Onde fica a sincronização | Numa branch compartilhada, `ws/sync`, que o `ws` envia sem PR e só com fast-forward. Ela chega ao `main` por um PR próprio, aberto e mergeado à mão (abordagem B, contra levar a sincronização dentro de cada branch de feature) |
| Base do `ws` | `WS_BASE=ws/sync`. O destino dos PRs vira uma variável própria, `WS_DESTINO=main` |
| Número de SP | Nenhum. Adendo 6 do ADR 0001 |

**Por que não levar a sincronização dentro de cada branch (abordagem A):** o PR do workspace só é aberto depois que todos os PRs dos repos forem mergeados, então as branches duram dias. Cada uma traria a sua própria sincronização, com commits diferentes para o mesmo repo. Quando duas sincronizações pegam commits diferentes do repo e o mesmo trecho mudou nas duas janelas, o merge conflita em `repos/<repo>/`. Além disso, o `main` ficaria com linhas paralelas de squash, e a busca da última sincronização (`ws_last_squash`) poderia pegar a mais antiga, o que afeta o `ws push` e o estado do Atlas.

**Por que a `ws/sync` não conflita:** há uma única linha de squash por repo, como hoje, e todos os devs usam os mesmos commits de sincronização. Quando a feature leva esses commits ao `main` e o PR da `ws/sync` também, em qualquer ordem, o git vê os mesmos commits dos dois lados.

## 4. Arquitetura

- **`main`:** destino de todos os PRs do workspace (features, bugs, harness, Atlas e a própria `ws/sync`). Só muda por PR.
- **`ws/sync`:** linha de sincronização. Contém o `main` mais as sincronizações ainda não mergeadas. O `ws` faz push nela sem PR, sempre com fast-forward, nunca forçado.
- **Branches de feature e de bug:** saem da ponta da `ws/sync`.

### 4.1 Fluxo do `ws start <branch>`

1. Busca `origin/ws/sync`. Se ela não existe no origin, cria a `ws/sync` local a partir do `origin/main`. Se existe, a `ws/sync` local passa a ser a do origin.
2. Faz o merge do `origin/main` dentro da `ws/sync`: fast-forward quando dá, merge sem fast-forward quando o `main` tem PRs que ela ainda não tem. Se houver conflito, aborta o merge, não envia nada e para (seção 5.2).
3. Sincroniza os subtrees como hoje (`git subtree merge --squash` dos repos que mudaram) e roda o rejoin do `ws maintain`.
4. Envia a `ws/sync` com fast-forward. Se o push é recusado por não ser fast-forward, volta ao passo 1 sobre a ponta nova, até 3 tentativas no total.
5. Cria a branch a partir da `ws/sync`.
6. Mostra o aviso do PR da `ws/sync` (seção 4.3).

Sem origin (testes, trabalho só local), não há fetch nem push, como hoje.

### 4.1.1 `ws sync` (acrescentado ao escrever o plano)

Os passos 1 a 4 e 6 do `ws start` ficam num comando próprio, `ws sync`, que não cria branch e volta para a branch em que o dev estava. O `ws start` é o `ws sync` mais o passo 5.

**Por quê:** uma branch aberta que precisa do que entrou no `main` depois dela (o caso "parar e pedir a inclusão" da regra 7 do `AGENTS.md`) hoje faz `git merge origin/main`. Com a base em `ws/sync`, o ponto de comparação do `ws push` e do converge passaria a ser anterior ao `main` trazido, e o `ws push` enviaria repos que a feature não mudou (o subtree inteiro de um repo novo, por exemplo). A branch passa a se atualizar com a `ws/sync`, que contém o `main`:

```bash
tools/ws/ws sync
git merge --no-edit ws/sync
```

Assim, o ponto de comparação vira a ponta da `ws/sync`, e o `ws push` e o converge continuam vendo só a feature.

### 4.2 O que usa cada variável

**`WS_BASE` (`ws/sync`), sem mudar a lógica:**
- `ws push`: prefixos alterados por `ws/sync...HEAD`, guarda e split;
- `ws maintain`: rejoin e deriva;
- Atlas: `--base` do plano e do converge, `ws_last_squash`, `ws_current_split`, incorporação e publicação. A `atlas/atualizacao` passa a ser montada sobre a `origin/ws/sync`.

**`WS_DESTINO` (`main`):**
- o link do PR da `atlas/atualizacao` (`targetRef=main`);
- `ws-bug-registro.sh`: "abra o PR do workspace para o main";
- `ws-bug-start.sh` e `ws-feature.sh`: a checagem de bug já registrado e de feature existente olha o `origin/main`, onde está o que já foi mergeado;
- `ws-commit-push.sh`: continua recusando rodar na base.

**`ws add`:** deixa de exigir estar na base. O time do harness roda numa branch criada a partir da `ws/sync`, e o repo novo entra por PR no `main`. No `ws start` seguinte, o passo 2 traz o repo para a `ws/sync`.

### 4.3 Aviso do PR da `ws/sync`

- Quando a `origin/ws/sync` tem commits que não estão no `origin/main`, o `ws start` mostra o link `pullrequestcreate?sourceRef=ws/sync&targetRef=main`.
- Quando a sincronização mais antiga ainda não mergeada passa de `pr_max_dias` (o mesmo limite do `relevancia.ini` que o Atlas usa), mostra também "peça a aprovação do PR de ws/sync".
- O `ws` não chama a API do Azure DevOps, então não sabe se o PR já está aberto: o aviso é um lembrete.

### 4.4 Tipo de merge do PR da `ws/sync`

Recomendado: merge commit. Um squash também funciona:
- os commits de sincronização continuam no histórico da própria `ws/sync`, onde o `ws` procura a última sincronização;
- o conteúdo que chega ao `main` é o mesmo;
- o commit de squash do Azure DevOps não tem os trailers `git-subtree-dir`, então não confunde a busca.

Por isso não se exige o tipo de merge por política.

## 5. Transição, casos de borda e erros

### 5.1 Transição

- **Primeiro `ws start` depois do merge:** cria a `ws/sync` no origin a partir do `origin/main` e mostra o link do primeiro PR.
- **`main` local à frente do origin** (quem rodou o `ws start` antigo e teve o push recusado): o `ws start` não usa o `main` local. Avisa uma vez com N, o número de commits: "seu main local tem N commits que não estão no origin; se forem só de sync (`ws: sync`, `Squashed`, `Split`), rode `git switch main && git reset --hard origin/main`". Não apaga nada.
- **Branches abertas antes da mudança** (saíram do `main`): continuam funcionando sem ação. A `ws/sync` contém o `main`, então o ponto de saída da branch é o mesmo, e o `ws push` e o converge veem só a feature.

### 5.2 Casos de borda

| Caso | Comportamento |
|---|---|
| Dois devs enviam a `ws/sync` ao mesmo tempo | O push do segundo é recusado (não é fast-forward). O `ws start` volta ao passo 1 sobre a ponta nova, até 3 tentativas. A segunda sincronização do mesmo commit de um repo não grava nada |
| Conflito no merge do `origin/main` na `ws/sync` | Não deve acontecer, porque os dois lados compartilham a linha de sincronização. Se acontecer: aborta o merge, não envia e mostra os arquivos, para o time do harness. O dev não resolve |
| Conflito na sincronização de um repo | Como hoje, com "Resolva na ws/sync" no lugar de "Resolva no main" |
| PR da `ws/sync` mergeado | No `ws start` seguinte, ela volta a coincidir com o `main` (fast-forward ou merge sem conflito), e o aviso do PR some |
| Política na `ws/sync` por engano | Push recusado com `TF402455`; mensagem da seção 5.3 |

### 5.3 Mensagens

| Situação | Mensagem |
|---|---|
| Recusa por política (`TF402455` na resposta do origin) | `push de ws/sync recusado por política do Azure DevOps (TF402455); a ws/sync não pode ter política de PR. Peça ao time do harness. Nada foi alterado no main.` |
| 3 tentativas recusadas por concorrência | `push de ws/sync recusado 3 vezes; rode o comando de novo. Resposta do origin: <resposta>` |
| Outra recusa | `push de ws/sync recusado. Resposta do origin: <resposta>` |

Saem as mensagens que mandam rodar `git pull --no-rebase origin main`.

## 6. Documentação

- **ADR 0001:** adendo 6, com o fluxo da seção 4 e o motivo (políticas do `main`).
- **Camada 2:** as entradas "push do main recusado" e "git pull do main falhou" dão lugar às mensagens da seção 5.3 e ao aviso do `main` local à frente; "Falha no sync" e "Conflito no sync" passam a citar a `ws/sync`.
- **Camada 3:** o passo do `ws start` em "Fora do Spec Kit" e a explicação do PR da `ws/sync`.
- **Camada 4:** "Adicionar um repo" numa branch do harness, com PR; como revisar e mergear o PR da `ws/sync`.
- **`AGENTS.md` e camada 1:** só onde citam o `main` como base da branch. A regra 7 do `AGENTS.md` e a entrada "A demanda cita um sistema fora do workspace" da camada 2 trocam `git fetch origin main` e `git merge --no-edit origin/main` pelo `ws sync` e `git merge --no-edit ws/sync` (seção 4.1.1).

## 7. Validação e entrega

### 7.1 Testes automatizados (`tools/ws/tests`)

A política do Azure DevOps é simulada por um hook `pre-receive` no origin `bare` dos testes, que recusa o push e devolve a mensagem `TF402455`. Cada teste novo é escrito antes da mudança e visto falhando:

1. com o `main` do origin protegido pelo hook, o `ws start` cria e envia a `ws/sync`, cria a branch e não tenta enviar o `main` (o caso do relato);
2. a primeira execução cria a `ws/sync` a partir do `origin/main` e mostra o link do PR;
3. `ws/sync` existente e `main` à frente por um PR: o `ws start` faz o merge do `main` e depois sincroniza;
4. dois clones fazem `ws start`; o segundo é recusado, refaz e envia por fast-forward;
5. a `ws/sync` protegida pelo hook: a mensagem cita `TF402455` e não sugere `git pull`;
6. `main` local à frente do origin: o aviso aparece e nada é apagado;
7. branch aberta a partir do `main` antes da mudança: o `ws push` envia só o repo que a feature mudou;
8. PR da `ws/sync` mergeado com squash: a sincronização seguinte acha a última sincronização certa, e o `ws push` não muda;
9. `ws add` numa branch do harness: o repo novo chega à `ws/sync` pelo `main` no `ws start` seguinte.
10. `ws sync` numa branch aberta antes da inclusão de um repo no `main`, seguido de `git merge ws/sync`: a branch passa a ter o repo, e o `ws push` envia só o que a feature mudou.

Os testes que hoje conferem o push do `main` passam a conferir o da `ws/sync`. Os do Atlas e do fluxo de bug que citam o `main` como base ganham ajustes pontuais. A suíte inteira roda antes do PR.

### 7.2 Validação no Azure DevOps real (depois do merge)

1. O usuário confirma que a `ws/sync` não herda política (as duas que existem são só do `main`).
2. Um dev sem bypass faz um `ws start` real (por exemplo, o do relato, depois do `reset` do `main` local): a `ws/sync` é criada e a branch sai dela.
3. O usuário abre e mergeia o primeiro PR da `ws/sync`; outro `ws start` mostra que ela voltou a coincidir com o `main`.

### 7.3 Entrega

Branch própria no workspace (`harness/ws-sync`), PR para o `main`. O merge é urgente: até ele, todo `/speckit-specify` e `/speckit-bug-assess` de quem não tem bypass falha. Paliativo até lá: dar o bypass temporariamente ao dev do piloto.

## 8. Fora do escopo

- Abrir ou mergear o PR da `ws/sync` pela API do Azure DevOps.
- Mudar as políticas do `main`.
- Mudanças no fluxo de bug além da troca de base.

## 9. Riscos

| Risco | Mitigação |
|---|---|
| O PR da `ws/sync` fica dias sem merge e os PRs das features mostram o código sincronizado | Aviso por idade (seção 4.3); o revisor pode filtrar `repos/` |
| Alguém cria política na `ws/sync` | Mensagem específica (seção 5.3) e item na camada 4 |
| Diferença entre a `atlas/atualizacao` montada sobre a `ws/sync` e o `main` | Os mesmos commits de sincronização chegam ao `main` pelo PR dela, pelo da `ws/sync` ou pelos das features, sem conflito (seção 3) |
