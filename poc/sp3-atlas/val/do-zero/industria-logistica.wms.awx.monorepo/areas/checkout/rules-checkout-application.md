# Regras do checkout (AWX.Checkout.Application)

> **Last updated:** 2026-10-06
> **Scope:** Regras em `src/Services/AWX.Checkout/src/AWX.Checkout.Application/Services` e no `Core/Domain`; agrupamento pelo código, `[unverified]` como conceito de negócio
> **Mode:** code-only
> **Status:** code-derived, not validated by a person — see ../../_discovery/assumptions-register.md

## Regras

- **Chegada da solicitação** — a mensagem da fila `awx_checkout_solicitacao` vira solicitação com itens. Se o armazém fatura no pré-checkout, o comando de faturamento sai logo, com a caixa de origem, operador `SISTEMA` e tipo de caixa de `Faturamento:TipoCaixaPadraoPreCheckout` (padrão `001`). Sem parametrização, o armazém é tratado como pós-checkout (C-23).
- **Modo de fechamento** — o parcial é o padrão; só é desligado quando `realizar_fechamento_parcial_checkout=false` ou `realizar_faturamento_pre_checkout=true`. Na caixa única, o tipo de caixa precisa existir no catálogo (`TipoCaixaInvalido`) e todos os itens não cancelados precisam estar conferidos (`CheckoutIncompleto`) (C-24).
- **Bloqueio de re-checkout** — com `status_faturamento_id` preenchido e diferente de 5 (ErroAoFaturar), o salvar devolve 409 `Checkout.FaturamentoJaIniciado`. Com 5, faz retentativa e republica todos os volumes Confirmados. NaoConfirmado também bloqueia de propósito e exige ação manual, sem fluxo no código para isso (C-25, A-20).
- **Sessão de conferência** — iniciar aborta as sessões órfãs do mesmo terminal; abortar uma sessão finalizada dá 409 `SessaoConferencia.Finalizada`; abortar apaga os volumes Rascunho e desvincula os itens (C-26).
- **Conferência de item** — item cancelado ou já em volume não pode ser conferido (409 `ConferirItem.Invalido`) (C-27).
- **Fechamento parcial** — exige sessão e terminal válidos; item já associado a caixa dá 409 `FecharCaixa.ItemJaAssociado`; o volume nasce Rascunho com identificador gerado pelo WMS legado via ACL. No salvar parcial todos os itens precisam ter volume (`Checkout.ItensPendentes`); os rascunhos viram Confirmados, a sessão é finalizada e sai **um** comando de faturamento com todos os volumes (C-28).
- **Caixa única** — o identificador é gerado com canal de expedição fixo em 2 (B2B), e o peso do volume vai 0. O porquê é pendência (A-13) (C-29).
- **Cancelamento de item** — motivo obrigatório e existente; descrição obrigatória só para o motivo que exige complemento (até 200 caracteres) e proibida nos demais (`Cancelamento.DescricaoNaoPermitida`); CUP repetido, item inexistente ou já cancelado são rejeitados (C-31).
- **Atualizar caixa** — consulta ao vivo no Faturamento o prazo de cancelamento de cada caixa; fora do prazo devolve 409 `AtualizarCaixa.ForaDoPrazoCancelamento` ("NF emitida há mais de 24h") e não publica; dentro dele republica o comando de faturamento (C-32).
- **Consulta de cancelamentos** — período máximo de 90 dias, página de 1 a 500 (C-33).
- **Reimpressão** — exige checkout fechado (`Reimpressao.CheckoutNaoFechado`); a etiqueta é lida no Faturamento pela chave `{CAIXA}_CHECKOUT` ou `{CAIXA}_MINIDANFE`; impressão parcial responde 502 `Reimpressao.ImpressaoParcial` (C-34).
- **Etiqueta best-effort** — falha ao persistir ou imprimir a etiqueta é logada e não desfaz o checkout (C-35).

## Onde são aplicadas

Nos serviços de `Application/Services` (`CheckoutService`, `CheckoutParcialService`, `CheckoutValidacaoService`, `FecharCaixaParcialService`, `SessaoConferenciaCheckoutService`, `SolicitacaoService`, `AtualizarCaixaService`, `Reimpressao*`) e nas entidades `SessaoConferenciaCheckout` e `SolicitacaoItem`. Os endpoints só traduzem `ErrorOr` em HTTP. Não há autenticação na API (A-8).

Fluxo completo: [workflow-checkout-faturamento.md](../../business/workflow-checkout-faturamento.md).
