# Regras do pedido B2C (PedidoService e consumidores)

> **Last updated:** 2026-10-06
> **Scope:** Regras em `AWX.PedidosB2C.Application/Pedidos/PedidoService.cs`, nos validators, no Worker do PedidosB2C e no consumer do AWX.Picking; agrupamento pelo código, `[unverified]` como conceito de negócio
> **Mode:** code-only
> **Status:** code-derived, not validated by a person — see ../../_discovery/assumptions-register.md

## Regras

- **Validação na entrada** — número do pedido, seller e tipo obrigatórios (até 50 cada), armazém opcional (até 20), ao menos um item, SKU até 50, quantidade > 0; erro de validação responde 422 (C-73).
- **Criação idempotente** — número já existente devolve o pedido existente sem gravar nem emitir evento (C-73).
- **Alteração** — substitui os itens e passa a Alterado; se itens ou armazém vierem informados no PUT, reemite `pedido-criado`; sempre emite `status-alterado`; erro de validação no PUT responde 409 (C-73).
- **Cancelamento** — idempotente; emite `status-alterado` com Cancelado. Qualquer erro no DELETE vira 404. Nenhum consumidor cancela o picking (A-18) (C-73).
- **Outbox** — pedido e evento gravados na mesma transação; o dispatcher publica a cada 5s até 50 eventos; 3 falhas inativam o evento (C-70).
- **Status para o legado** — o Worker consome `status-alterado` e faz `PUT /api/v1/wms/pedidos-b2c/{n}/status` na ACL, sem API key e sem DLQ (nack com requeue) (A-4) (C-74).
- **Picking** — exige armazém (opcional no B2C) e rejeita SKU repetido ("Pedido contém SKU duplicado entre os itens."); erro de validação vai direto para a DLQ. Registra o picking antes de chamar a ACL e ignora duplicata; manda ao legado `StatusPedido = "Criado"`, `Grade = "-"`, `Tamanho = 1` e a soma das quantidades. ACL 400 vai para a DLQ, outros erros para retry 10/30/60s (C-75).
- Os limites divergem entre camadas (número do pedido 50 na validação e 100 no banco; armazém 20 no B2C e 10 no Picking) (A-19).
