# Objetos da ACL no banco do WMS legado

> **Last updated:** 2026-10-06
> **Scope:** Tabelas do banco `WMS` (SQL Server) lidas ou gravadas pela ACL `AWX.IntegracaoLegadoWMS` e os scripts que as criam
> **Mode:** code-only
> **Status:** code-derived, not validated by a person — see ../../_discovery/assumptions-register.md

O nome do banco não aparece em config versionada; os testes usam `Database=WMS` e o catálogo do Atlas confirma `dbo.NotaFiscal`, `dbo.TipoPedido`, `dbo.EntidadeExternaNotaFiscal` e `dbo.PickingECommerce` no banco WMS (C-40).

## Entidades

| Objeto | Criado por | O que guarda | Uso pela ACL |
|---|---|---|---|
| `Recebimento.NotaFiscal` | script 001 (move `dbo.NotaFiscal`; o 002 deixa o sinônimo `dbo.NotaFiscal`); o 006 de contagem acrescenta `StatusContagem`, `DataContagemFinalizada`, `StatusEnvioErp`, `DataEnvioErp` | Cabeçalho da NF de entrada | dedup, INSERT, UPDATE de contagem |
| `Recebimento.NotaFiscalItem` | 003 | Itens (UNIQUE por nota+produto+cor+tamanho) | INSERT, SELECT |
| `Recebimento.NotaFiscalItemContagem` | 007 | Quantidade esperada × contada por item | INSERT |
| `dbo.EntidadeExternaNotaFiscal` | já existia | Romaneios e pedidos de sobra/falta ligados à NF | INSERT (`Processado = 0`) |
| `Produtos.Produto` | 005 (schema) + 006 | Produto por SKU (único) | upsert, SELECT |
| `Produtos.CodigoBarraSku` | 008 | Código de barras → SKU | nenhum uso no código |
| `dbo.ProdutosCup` | 004 | CUP → SKU, pedido, validade (UNIQUE `CupId`) | SELECT, INSERT |
| `pedido.Pedidos` / `pedido.PedidosItem` | 007 (schema) + 008 | Projeção do pedido B2C (FK `dbo.TipoPedido`) | INSERT, UPDATE de status |
| `dbo.TipoPedido` | já existia | Tipos de pedido | SELECT por descrição |
| `dbo.PickingECommerce` | já existia; 006 acrescenta `TraceId` | Picking e-commerce do legado | nenhum uso no código |
| `FATURAMENTO_PROD`, `FATURAMENTO` | Linx (banco Reserva) | NF de saída por pedido | SELECT da triangulação (A-7) |

Os prefixos 006, 007 e 008 se repetem em arquivos diferentes, e o db/README lista scripts que não existem (A-2) (C-42).

## Estados da contagem

`StatusContagem`: (vazio) → CONCLUIDA. `StatusEnvioErp`: PENDENTE → ENVIADO ou FALHA (C-46).

Regras: [rules-integracao-legado-application.md](./rules-integracao-legado-application.md).
