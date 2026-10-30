# Correção da ws-002-chaves-centrais (2026-10-30)

Task 1 do plano `docs/superpowers/plans/2026-10-30-branch-teste-e-ajustes-de-pr.md`. Origem: feedback "conflitos e revisões dentro da branch da feature".

## O problema

A resolução de conflito com o ramo de teste (homolog/release) e os ajustes de revisão dos PRs foram feitos direto nas branches `ws-002-chaves-centrais` dos repos. Como o mesmo `<branch>` serve os PRs de homolog e de main, a branch do AWX ficou com 344 commits fora do `main`, e o workspace não tinha os commits de revisão.

## O que foi feito (branch `ws-002-chaves-centrais` do workspace)

1. `ws sync` e merge da `ws/sync` na feature (`402044b73`), 115 conflitos:
   - 88 do Atlas: versão do `main` (mapeamento refeito depois, gatilho `converge`);
   - 27 de código: resoluções do dev de 27/10 (merges `192eca5` no AWX e `07cd208` no linx) + 3-way contra o `main`; 6 à mão, mantendo só o que é da feature.
2. Nove commits de revisão trazidos com o autor original (`format-patch` + `git am -3 --directory=<prefixo>`):
   - servidor `5af796f` → `2a96ec2f6`;
   - linx `62363e0` → `18a067b6e`, `ef579c7` → `ce0036c14`;
   - AWX `1b6ab6a` → `0e523e6c2`, `87a4256` → `63ce9d635`, `4944e95` → `5b2e17e86`, `9b7a472` → `550992e0b`, `8fff95f` → `280ee3bb3` (4 conflitos à mão: o Worker hospeda a sincronização), `43c8333` → `7af5c1773`.
3. Ajuste pós-merge `6611778d6`: validações do ErpConnector no bloco do `Program.cs` da API (o `main` removeu `ValidacaoOpcoesExtensions`); `ErpConnectorOptionsTests` valida pelo `AddSincronizacaoChaves`; dois testes dos clientes do ERP Connector com a versão do `main`.
4. Conferência: `git merge-tree --merge-base=<homolog> main <branch do repo>` (= main + (branch − homolog)) comparado com a feature; só sobraram fim de linha e os pontos acima.
5. Testes: IntegracaoLegadoWMS com as mesmas 47 falhas do `main` (banco de teste local sem `dbo.PickingECommerce` etc.); ERP Connector 525/525; SharedKernel 110/110; linx 368/368; servidor.backend (net48) não compilado.

## Branches dos repos

A pedido do usuário, a ponta antiga foi guardada em `im/bkp/ws-002-chaves-centrais` (push sem force) e a `ws-002-chaves-centrais` foi recriada com o split novo (`--force-with-lease` contra a ponta antiga), conferido por `ls-remote`:

| Repo | Backup (ponta antiga) | Nova |
|---|---|---|
| industria-logistica.wms.awx.monorepo | `43c8333` | `738f1dee0` (102 arquivos vs main) |
| industria-logistica.wms.servidor.backend | `5af796f09` | `6801b4aef` (53 arquivos) |
| integracoes.wms.servicos-linx-wms.monorepo | `ef579c7` | `a88b92021` (13 arquivos) |

Os PRs de homolog 17266, 17267 e 17268 (completados) ficaram como estavam. As branches novas descendem do `main` de cada repo e estão prontas para `/ws-pr-main`.

PR 17503 (`ws/sync` → `main` do workspace) aberto e completado pelo usuário.
