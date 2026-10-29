# SP9: validação real (Task 3)

Datas: 2026-10-28 (corridas) e 2026-10-29 (conferência na interface e limpeza). Validação de ponta a ponta do `ws-feature.sh` com a reserva de número, contra o origin real (`industria-logistica.wms.workspace`, projeto AReCO), a partir da branch local `harness/sp9-reserva-numero` (commit `354b7c850`), sem push da branch e sem PR. O teste anterior do mecanismo, com `git push` direto, está em `sp9-teste-azure.md`.

## Setup

- Três "estações" (`e1`, `e2` e `e3`): clones locais separados do worktree `C:\src\wms-workspace-sp9`, com o `origin` trocado para o Azure. Clones e não worktrees, para que uma estação não tivesse o commit de reserva da outra.
- Nas rodadas 1 a 6, o `ws start` foi trocado por um stub (`WS_BIN`, que só sai com 0), para que só as reservas fossem ao Azure. A rodada 7 usou o `ws start` real.
- Cada execução rodou com `GIT_TRACE_PACKET` num arquivo próprio. A linha `ng refs/ws-reserved/<NNN> <motivo>` mostra a rejeição do servidor. Um refspec mandado ao helper sem comando ao servidor indica `(fetch first)`. Uma tentativa que nem chega ao helper indica `(non-fast-forward)`, porque o cliente já tinha o commit.
- Antes de começar: nenhuma reserva no origin; branches `ws-001` a `ws-003` no origin. Por isso as corridas começaram no `ws-004`.

## Resultados

| Rodada | Estações | Números | Rejeição da perdedora pelo servidor |
|---|---|---|---|
| 1 | e1 e e2 juntas | e1 = 004, e2 = 005 | `TF401028` no 004 |
| 2 | e1 e e2 juntas | e1 = 006, e2 = 007 | `TF401028` no 006 |
| 3 | e1 e e2 juntas | e1 = 008, e2 = 009 | `TF401028` no 008 |
| 4 | e1 e e2 juntas | e1 = 010, e2 = 011 | `TF401028` no 010 |
| 5 | e1 e e2 juntas | e1 = 012, e2 = 013 | `TF401028` no 012 |
| 6 | e1 e e2 juntas, e3 4 s depois | e2 = 014, e1 = 015, e3 = 016 | `TF401028` no 014 (e1) |
| 7 | e1, com o `ws start` real | e1 = 017 | nenhuma (estação sozinha) |

- Nenhuma colisão e nenhum `ERROR` nas 7 rodadas. Em todas as 6 rodadas simultâneas, o Azure arbitrou com `TF401028`.
- Os três caminhos de rejeição apareceram e foram tratados como colisão: `TF401028`, `(fetch first)` (a reserva era da outra estação) e `(non-fast-forward)` (a reserva era da própria estação, numa rodada anterior).
- **Rodada 7 (`ws start` real):** `ERROR` vazio e branch `ws-017-sp9-teste-7-e1` criada só no clone. O `ws start` sincronizou dois repos com mudanças reais do upstream (`industria-logistica.wms.servidor.backend` e `integracoes.core.plataforma.backoffice.frontend`) e deu push na `ws/sync` (de `33708fd` para `6726daf`). É o fluxo normal de qualquer dev ao abrir uma feature. O `AVISOS` trouxe o aviso que já existia: a `ws/sync` tem 25 commits fora do `main`.

## Visibilidade

- `git ls-remote --heads origin`: nenhuma `ws-reserved`, e nenhuma das branches `ws-004` a `ws-017` foi para o origin.
- Conferido pelo usuário no Azure em 2026-10-29, com as 14 reservas vivas: nada em Branches, Tags, no seletor de branch nem em Pushes.

## Achado: `next_num()` não olhava as reservas

Cada execução partia do maior número *visível* (specs e branches) e tentava uma a uma as reservas acima dele: a rodada 7 fez 14 tentativas, cerca de 1,3 s cada. Como a branch da feature só vai ao origin no `/ws-commit-push`, no fim do fluxo, toda feature em andamento é uma reserva que ninguém vê. Com 20 features em andamento, o teto de tentativas bloquearia todo `/specify` do time.

**Decisão do usuário (2026-10-29):** `next_num()` passa a considerar também `git ls-remote origin 'refs/ws-reserved/*'` (spec, seção 4; adendo no plano). Com isso o laço só anda quando há corrida de verdade.

## Limpeza (2026-10-29)

- As 14 reservas (`004` a `017`) foram apagadas cada uma com `--force-with-lease` pelo SHA registrado, depois de conferir que o origin estava igual ao registro. O `ls-remote` final voltou vazio, então nenhum número ficou queimado.
- Clones e stub apagados; a branch `ws-017` só existia no clone `e1`.
- O push na `ws/sync` da rodada 7 ficou: é sincronização normal.

## Revalidação depois da mudança no `next_num()` (2026-10-29)

Com o OK do usuário, duas rodadas curtas com duas estações (clones novos a partir do commit `24766e1bd`, `ws start` trocado pelo stub). Antes: nenhuma reserva no origin.

| Rodada | Números | Tentativas |
|---|---|---|
| 1 | e2 = 004, e1 = 005 | e1: `004` TF401028, `005` ok |
| 2 | e1 = 006, e2 = 007 | e2: `006` TF401028, `007` ok |

- Na rodada 2 as duas estações partiram direto do `006`, sem tentar o `004` e o `005` já reservados: o `next_num()` passou a enxergar as reservas. O laço só andou na corrida de verdade.
- Nenhum `ERROR`, nenhuma colisão, nada em `--heads`.
- Limpeza: as 4 reservas (`004` a `007`) apagadas com `--force-with-lease` pelo SHA; `ls-remote` final vazio. Clones e stub apagados.
