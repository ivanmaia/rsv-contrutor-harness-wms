# SP9: Reserva atômica do número da feature (design)

Data: 2026-10-27. Processo: `superpowers:brainstorming`. Decisões tomadas com o usuário na conversa de 2026-10-27, a partir de uma colisão real observada em teste.

## 1. Intenção e porquê

Dois devs, cada um na sua estação, rodaram `/speckit-ws-feature` (via `/specify`) quase ao mesmo tempo. Cada estação calculou `ws-004` como próximo número livre e seguiu em frente sem erro nenhum — resultado: duas features diferentes nasceram com o mesmo número.

Isso acontece porque, em `ws-feature.sh`:
- `next_num()` só olha o que a estação já viu no `origin` no momento do fetch (specs do main, branches locais e do origin);
- a branch da feature nova é criada só localmente — o `ws start` não dá push dela ao origin nesse momento (spec SP1, ADR 0001);
- `branch_taken()`, a única checagem de colisão que existe, compara o **nome completo** da branch (`ws-004-<slug>`), não o número isolado — e como os slugs das duas features são diferentes, a checagem não acusa nada.

Não existe hoje nenhum ponto do fluxo em que o Azure DevOps arbitre quem ganhou um número.

## 2. Objetivos, não objetivos e antiobjetivos

**Objetivos:**
- eliminar a colisão de número entre features quando duas estações rodam `/specify` ao mesmo tempo, sem depender de coincidência de slug.
- não introduzir nenhuma peça nova de infraestrutura (sem serviço de lock, sem CI, sem arquivo compartilhado fora do git).

**Não objetivos:**
- cobrir o mesmo risco nas rodadas (`-r<k>`) e nos retries de subida/validação (`-<k>`) do `ws-refactor-start.sh` — decisão do usuário: risco residual conhecido, bem mais raro (só colide entre duas pessoas mexendo no mesmo work item/fatia ao mesmo tempo), fica para depois.
- mudar a numeração de bug (`ws-bug-start.sh`) — não usa contador sequencial, a identidade já vem do id do work item ou de `inc-AAAAMMDD`.
- mudar o comportamento de `ws start`/`ws sync` em si.

**Antiobjetivos:**
- poluir a lista de branches do Azure DevOps ou do `git branch -a` com marcadores de reserva.
- exigir rede/origin quando o workspace não tem (deve continuar funcionando offline, como hoje).

## 3. Decisão tomada com o usuário

A estação reserva o número no `origin` com um **push atômico de uma ref fora de `refs/heads`**: `refs/ws-reserved/<NNN>`. Push de uma ref nova é atômico no servidor — só uma estação consegue criar uma ref com esse nome apontando para um commit específico; a perdedora recebe rejeição na hora e tenta o próximo número, no mesmo estilo de retry que `ws_sync_envia` (`tools/ws/lib/start.sh`) já usa para o push da `ws/sync`.

**Ressalva técnica (achada ao testar):** se as duas estações empurrarem exatamente o mesmo commit (o caso comum, já que ambas partem do mesmo `origin/$WS_DESTINO` recém-buscado), um segundo `git push` para uma ref que já existe com aquele valor não é rejeitado — o git responde "Everything up-to-date" e sai com sucesso, porque não há nada de novo para enviar. Isso anularia a reserva. A correção é reservar com um **commit órfão só da reserva** (árvore vazia, sem pai, mensagem com `$$`/`$RANDOM` para ser único por tentativa) em vez do commit da base — garante que o conteúdo enviado por cada estação é sempre diferente, e aí a proteção padrão contra non-fast-forward do git rejeita de verdade a segunda tentativa.

Essas refs ficam no `origin` sem prazo de expiração: o harness nunca apaga nenhuma, e o custo é desprezível (refs leves, sem objeto pesado). Não são imutáveis, porém: quem tem permissão de excluir refs no repositório consegue apagá-las (a credencial do usuário conseguiu, no teste da seção 3.1). Uma reserva apagada não desfaz a feature já criada — a branch e a pasta da spec continuam lá e `next_num()` continua enxergando o número por elas — mas abre a janela para colisão de novo enquanto a branch não chega ao origin. Por estarem fora de `refs/heads`, as reservas não aparecem em `git branch -a`, no `git ls-remote --heads` nem em nenhuma tela de branches do Azure DevOps (seção 3.1).

### 3.1 Validação contra o Azure DevOps real (2026-10-27)

Antes de implementar, o mecanismo foi testado no origin real (`industria-logistica.wms.workspace`), com a credencial do usuário. O registro completo está em `docs/discovery/sp9-teste-azure.md`. O que mudou no design por causa dele:

- **A corrida de verdade é arbitrada pelo próprio Azure:** em 8 de 8 disputas simultâneas entre duas estações houve um vencedor só. A perdedora recebe `! [remote rejected] ... (TF401028: The reference '...' has already been updated by another client ...)`.
- **Colisão aparece de exatamente três formas**, e só essas três podem levar ao número seguinte:
  - `non-fast-forward` (o cliente já tem o commit da reserva vencedora);
  - `fetch first` (o cliente não tem esse commit — o caso normal entre estações);
  - `TF401028` (as duas estações enviaram ao mesmo tempo, e o servidor rejeitou a segunda).
- **Qualquer outro erro faz o fluxo parar**, inclusive outros `[remote rejected]` (permissão negada, política do repositório). Antes o desenho classificava qualquer "rejected" como colisão, e nesse caso o laço avançaria o número sem nunca conseguir reservar. Rede, repositório inexistente e falta de credencial saem com código 128 e sem a palavra "rejected".
- **Sem efeito colateral:** nenhum pipeline, service hook ou notificação disparou, e a ref não apareceu em Branches, Tags, no seletor de branch nem em Pushes (conferido pelo usuário na interface).
- **Fica sem validar:** as permissões dos outros devs, porque o teste usou só a credencial do usuário. Quem não puder criar refs fora de `refs/heads` cai no caso "outro erro" e o fluxo para com a mensagem do Azure, sem colidir.

## 4. Comportamento

- **Com origin:** depois de calcular o slug, a estação tenta reservar `next_num()`; se a reserva for rejeitada por colisão (uma das três formas da seção 3.1), tenta o número seguinte, e assim por diante, até conseguir. Só então monta `ws-<NNN>-<slug>` e segue o fluxo de hoje (`ws start`).
- **Push falhou por outro motivo** (rede, credencial, permissão, política): o fluxo para e mostra a mensagem do git, sem avançar o número.
- **Sem origin** (workspace local, sem rede): pula a reserva inteira, comportamento idêntico ao de hoje.
- `branch_taken()` continua existindo como segunda linha de defesa (não deve mais disparar na prática).

## 5. Fora de escopo

`ws-refactor-start.sh` e `ws-bug-start.sh`: sem nenhuma mudança.
