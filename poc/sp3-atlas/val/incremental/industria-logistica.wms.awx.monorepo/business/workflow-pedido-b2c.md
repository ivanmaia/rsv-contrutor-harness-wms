# Fluxo: pedido B2C até o WMS legado

> **Last updated:** 2026-10-06
> **Scope:** ERP Connector → PedidosB2C → Picking → ACL → banco WMS (cross-area; spec `specs/001-picking-b2c-consumer`)
> **Mode:** code-only
> **Status:** code-derived, not validated by a person — see ../_discovery/assumptions-register.md

```mermaid
sequenceDiagram
  participant SRC as Linx / ERP Connector (api/pedidos-b2c/lote)
  participant B2C as PedidosB2C
  participant PK as Picking Worker
  participant ACL as IntegracaoLegadoWMS
  participant DB as WMS.pedido.*
  SRC->>B2C: POST /api/v1/pedidos-b2c (X-API-KEY)
  B2C->>B2C: pedido + outbox na mesma transação
  B2C-->>PK: awx.pedidos-b2c.pedido-criado (outbox, 5 s)
  PK->>PK: valida e grava picking_ecommerce (NumeroOR, NumeroLote)
  PK->>ACL: POST api/v1/wms/pedidos-b2c
  ACL->>DB: INSERT Pedidos + PedidosItem (idempotente por NumeroPedido)
  B2C-->>B2C: awx.pedidos-b2c.status-alterado (alterar/cancelar)
  B2C->>ACL: PUT pedidos-b2c/{n}/status (sem X-API-KEY, A-3)
```

- **Criar** é idempotente (pedido já existente devolve o existente com 201). **Alterar** sempre marca Alterado e reemite pedido-criado se vierem itens ou armazém. **Cancelar** é idempotente (C-40).
- **Picking:** pedido inválido vai direto para a DLQ; erro transitório tenta de novo em 10/30/60 s e depois vai para a DLQ. Grade e tamanho são enviados como "-" e 1 (placeholders), e NumeroOR/NumeroLote não chegam à ACL `[unverified]` (C-42, C-43, A-15).
- **Status para o legado:** falha na ACL devolve a mensagem para a fila sem limite (A-17).
- **Cancelamento externo (novo em `e495e61`).** O ERP Connector recebe em `POST api/pedidos-b2c/cancelamentos` lotes de até 500 números de pedido, publica um fato por pedido em `x.awx.erp-connector.eventos` (rk `pedido-b2c.cancelado-externamente`) e devolve, por pedido, se o barramento aceitou. Nenhum serviço do repo consome esse fato: o PedidosB2C não cancela o pedido a partir dele `[unverified]` (C-67, A-33).
- **Depois do faturamento B2C (novo).** A Expedição grava a NF do pedido (`expedicao.notas_fiscais`, status Pendente, idempotente por chave) ao receber `awx.faturamento.pedido-b2c-concluido` ou `POST api/v1/expedicao/notas-fiscais`. Ninguém no repo publica esse evento (C-68, A-34).
