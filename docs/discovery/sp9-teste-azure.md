# SP9: teste do mecanismo de reserva contra o Azure DevOps

Data: 2026-10-27. Teste feito **antes** da implementação, para checar a premissa central do design do SP9 (`docs/superpowers/specs/2026-10-27-sp9-reserva-numero-feature-design.md`, seção 3): que o Azure DevOps aceita refs fora de `refs/heads`, arbitra a disputa entre duas estações e não mostra essas refs nas telas de branches. Os testes do plano usam um remoto bare local e não respondiam isso.

## Setup

- Origin real: `industria-logistica.wms.workspace` (projeto AReCO), com a credencial do usuário.
- Git 2.54.0 para Windows.
- Clones descartáveis no scratchpad da sessão; `C:\src\wms-workspace` não foi tocado.
- Duas "estações" sem o commit uma da outra: `git init` + `git fetch --depth 1 origin main`. Um clone parcial (`--filter=blob:none`) não serve para isso, porque busca sob demanda o objeto que falta e mascara o caso real.
- Refs de teste com nomes não numéricos (`refs/ws-reserved/sp9-probe`, `sp9-probe-base`, `sp9-race-1` a `8`, `sp9-probe-ui`), para não bloquear nenhum número real se a limpeza falhasse.
- Todos os commits de reserva são órfãos sobre a árvore vazia (`4b825dc6...`), com mensagem única (`$$-$RANDOM`), como no design.

## Resultados

| Cenário | Saída do `git push` | Código |
|---|---|---|
| Primeira reserva de uma ref nova | `* [new reference]` | 0 |
| Outro commit órfão, estação que já tem o commit vencedor | `! [rejected] ... (non-fast-forward)` | 1 |
| Outro commit órfão, estação **sem** o commit vencedor (o caso normal entre estações) | `! [rejected] ... (fetch first)` | 1 |
| O mesmo commit empurrado de novo | `Everything up-to-date` | 0 |
| Ref apontando para o commit da base, depois um commit órfão | `! [rejected] ... (non-fast-forward)` | 1 |
| **Duas estações empurrando a mesma ref nova ao mesmo tempo, 8 rodadas** | Em 8 de 8, uma só venceu (e o valor no remoto é o da vencedora). A perdedora recebeu `! [remote rejected] ... (TF401028: The reference '...' has already been updated by another client, so you cannot update it. Please try again.)` | 0 e 1 |
| Repositório inexistente | `remote: TF401019: ... does not exist or you do not have permissions ...` | 128 |
| Host inexistente (rede) | `fatal: unable to access ...: Could not resolve host` | 128 |
| Sem credencial | `fatal: could not read Username ...: terminal prompts disabled` | 128 |

As 8 corridas dividiram a vitória entre as duas estações (5 para uma, 3 para a outra), então o resultado não depende de qual processo sai primeiro.

## Visibilidade e efeitos colaterais

- `git ls-remote --heads` não lista nenhuma `ws-reserved` (11 branches, nenhuma reserva); `--tags` também não. O `git ls-remote` completo lista.
- Conferido pelo usuário na interface do Azure, com a ref `sp9-probe-ui` viva: não aparece em Repos → Branches (abas e busca), Repos → Tags, no seletor de branch da tela Files e do "New pull request", nem em Repos → Pushes.
- Conferido pelo usuário: nenhum pipeline rodou, não há service hooks no projeto e ninguém recebeu notificação.

## Limpeza

Todas as refs de teste foram apagadas com `git push origin :refs/ws-reserved/<nome>` (`[deleted]`), e o `git ls-remote origin 'refs/ws-reserved/*'` final voltou vazio. A limpeza da primeira leva foi feita antes de o usuário conferir a interface (erro de ordem meu); por isso a `sp9-probe-ui` foi recriada só para essa conferência e apagada em seguida.

## O que mudou no design e no plano

1. **Colisão = só três padrões:** `(non-fast-forward)`, `(fetch first)` e `TF401028`. O plano casava com `*rejected*`, o que também pegaria outro `[remote rejected]` (permissão negada, política) e faria o laço avançar o número sem nunca reservar.
2. **O caminho `TF401028` não existe com remoto bare local.** O plano ganhou um teste que o simula com um hook `pre-receive` (conferido localmente: a mensagem do hook chega na saída do push) e uma Task 3 de validação de ponta a ponta contra o Azure.
3. **As reservas não são "para sempre":** a credencial do usuário conseguiu apagá-las. O harness nunca as apaga, mas quem tiver permissão consegue.

## Fica sem validar

- **Permissões dos outros devs:** só a credencial do usuário foi testada. Quem não puder criar refs fora de `refs/heads` deve receber um `[remote rejected]` com outro código TF; com o ajuste 1, o fluxo para com a mensagem do Azure em vez de colidir.
- **O `ws-feature.sh` real disputando contra o Azure:** este teste provou o mecanismo com `git push` direto; a prova do hook é a Task 3 do plano.
