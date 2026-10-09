# Integrações e dependências

> **Last updated:** 2026-10-06
> **Scope:** Bancos, HTTP de entrada e saída, filas e jobs do AWX (`industria-logistica.wms.awx.monorepo`, commit `e495e61`)
> **Mode:** code-only
> **Status:** code-derived, not validated by a person — see ../_discovery/assumptions-register.md

Cada aresta, com `caminho:linha`, está no [edges.csv](../edges.csv) (250 linhas). IDs `C-n` remetem ao [índice de rastreabilidade](../_discovery/traceability-index.md). Segredos aparecem só pelo nome da chave.

## Visão geral

| Sistema | Para quê | Direção | Mecanismo | Configuração (nomes) |
|---|---|---|---|---|
| ERP Linx | Faturamento, status de NF, etiquetas, contagem, auditoria, clientes, pedidos, produtos, volume de expedição | saída (via ERP.Connector) | REST, um HttpClient nomeado por bloco, timeout 2 min, retry linear | `LinxIntegration:<Bloco>:ApiUrl`, `LinxIntegration:HttpRetry:*` (C-30) |
| Banco do WMS legado (SQL Server) | NF de entrada, contagem, produtos, CUP, pedidos B2C, triangulação | leitura e escrita (só a ACL) | Dapper + SqlClient | `WmsLegadoSql:ReadOnlyConnectionString`, `WmsLegadoSql:WriteConnectionString` (connection strings) (C-40) |
| API do WMS legado | Gerar identificador de volume de expedição | saída (só a ACL) | REST | `WmsLegadoApi:BaseUrl` (C-41) |
| PostgreSQL por serviço | Estado próprio de Checkout, Faturamento, Estoque, PedidosB2C, PedidosB2B, Picking, Expedicao, Recebimento | leitura e escrita | EF Core + Npgsql | `PostgreSql:DefaultConnection`, `PostgreSql:MigrationsConnection` (connection strings) (C-3) |
| RabbitMQ | Solicitação de checkout, comando de faturamento, volume de expedição, eventos de pedido B2C, NF de expedição | ambas | RabbitMQ.Client e MassTransit | `RabbitMQ:AmqpUri`/`VHost`/`User`/`Pass` (senha) ou `RabbitMQ:Host`/`Username`/`Password` no Faturamento (C-14) |
| Printers API (`print-zebra.utilitario.backend`) | Enviar ZPL à impressora | saída (Impressao) | REST `POST /print` | `PrintersApiBaseUrl` (C-90) |
| Full Picking B2B (`wms.picking.backend`) | Publica a caixa pronta na fila `awx_checkout_solicitacao` | entrada | RabbitMQ (default exchange) | (lado do produtor) (C-91) |
| BFF `logistica.integrada.bff` (fora do monorepo) | Chama o Relatorios para a triangulação fiscal | entrada | REST | — `[assumption]` (C-92) |
| Sentry | Telemetria de erro | saída | SDK | `Dsn` / `Sentry:Dsn` (DSN) |

## Banco de dados

R = leitura, W = escrita, X = execução (migration, lock, `ExecuteUpdate`). Postgres: o nome `pg-<serviço>` é convenção do Atlas; o nome real do banco vem do ambiente (A-6).

| Objeto | Serviço | R | W | X | Operação |
|---|---|---|---|---|---|
| `pg-checkout.public.solicitacao` | Checkout | R | W | | INSERT com itens; UPDATE de checkout e status de faturamento |
| `pg-checkout.public.solicitacao_item` | Checkout | R | W | | UPDATE de conferência, volume e cancelamento |
| `pg-checkout.public.volume` | Checkout | R | W | | INSERT, UPDATE Rascunho→Confirmado, DELETE de rascunhos |
| `pg-checkout.public.sessao_conferencia_checkout` | Checkout | R | W | | INSERT/UPDATE de status |
| `pg-checkout.public.cancelamento_item_solicitacao` | Checkout | R | W | | INSERT de auditoria |
| `pg-checkout.public.motivo_cancelamento` | Checkout | R | | | SELECT (seed fora de migration, A-12) |
| `pg-checkout.public.parametrizacoes` / `parametrizacoes_log` | Checkout | R | W | | UPDATE + log |
| `pg-checkout.public.faturamento_caixa_tipo` | Checkout | R | | | SELECT (seed de 14 tipos) |
| `pg-checkout.public.__EFMigrationsHistory` | Checkout | | | X | `pg_advisory_lock` + migrate |
| `pg-faturamento.public.faturamento` | Faturamento | R | W | X | INSERT/UPDATE; claim por `ExecuteUpdateAsync` |
| `pg-faturamento.public.caixa_faturamento` / `item_embalado` | Faturamento | R | W | | INSERT de caixas e itens; UPDATE `faturamento_id` |
| `pg-faturamento.public.documento` | Faturamento | R | W | | upsert e DELETE de etiquetas (JSON) |
| `pg-faturamento.public.faturamento_caixa_tipo` | Faturamento | | W | | só seed via migration |
| `pg-estoque.public.produtos` / `produtos_cup` / `produtos_codigo_barra` | Estoque | R | W | | upsert por SKU e por CUP; INSERT de código de barras |
| `pg-pedidosb2c.public.pedidos` / `pedido_itens` | PedidosB2C | R | W | | INSERT/UPDATE |
| `pg-pedidosb2c.public.outbox_eventos` | PedidosB2C | R | W | | INSERT na transação; UPDATE no dispatcher |
| `pg-pedidosb2b.public.geracao_demanda_parametrizacao_por_cliente` | PedidosB2B | R | W | | CRUD com soft delete |
| `pg-picking.public.picking_ecommerce` / `picking_ecommerce_item` | Picking | | W | X | INSERT; sequences `NumeroOR` (53000000) e `NumeroLote` (28000000) |
| `pg-picking.public.outbox_eventos` | Picking | | W | | log de tentativas de consumo |
| `pg-expedicao.expedicao.notas_fiscais` | Expedicao | R | W | | EXISTS por chave; INSERT |
| `pg-recebimento.recebimento.__EFMigrationsHistory` | Recebimento | | | X | só migration (serviço sem tabelas) |
| `WMS.Recebimento.NotaFiscal` | ACL | R | W | | dedup, INSERT em transação, UPDATE de status de contagem |
| `WMS.Recebimento.NotaFiscalItem` | ACL | R | W | | INSERT na transação do cabeçalho |
| `WMS.Recebimento.NotaFiscalItemContagem` | ACL | | W | | INSERT |
| `WMS.dbo.EntidadeExternaNotaFiscal` | ACL | | W | | INSERT (romaneios e pedidos de sobra/falta) |
| `WMS.dbo.TipoPedido` | ACL | R | | | SELECT por descrição |
| `WMS.pedido.Pedidos` / `PedidosItem` | ACL | R | W | | INSERT em transação; UPDATE de status |
| `WMS.dbo.ProdutosCup` | ACL | R | W | | SELECT/INSERT |
| `WMS.Produtos.Produto` | ACL | R | W | | upsert com `UPDLOCK, HOLDLOCK` |
| `Reserva.dbo.FATURAMENTO_PROD`, `Reserva.dbo.FATURAMENTO` | ACL | R | | | SELECT NOLOCK por pedido; a query não qualifica banco nem schema e roda na connection string de leitura do WMS `[assumption]` (A-7) |

Os objetos `Recebimento.*`, `Produtos.*`, `pedido.*` e `dbo.ProdutosCup` são criados pelos scripts de `src/Integrations/AWX.IntegracaoLegadoWMS/db/` e ainda não constam do catálogo `docs/atlas/banco/WMS/objects.csv`; o script 001 move `dbo.NotaFiscal` para `Recebimento.NotaFiscal` e o 002 cria o sinônimo `dbo.NotaFiscal` (C-42).

## HTTP exposto (inbound)

89 rotas no [edges.csv](../edges.csv) (tipo `http-in`). Resumo por API:

| API | Prefixos | Autenticação | Quem chama (encontrado no código) |
|---|---|---|---|
| AWX.Checkout.Api | `/api/solicitacao/*`, `/api/checkout/*`, `/api/parametrizacoes`, `/api/cancelamentos`, `/api/tipos-caixa`, `/pedidos/{pedido}` (mock) | nenhuma | Fly.BFF (`/checkout/**`) |
| AWX.Faturamento.Ui.WebApi | `/api/faturamento/status/{caixa}`, `/api/v1/faturamento*`, `/api/v1/etiquetas/*`, `/api/v1/documentos*` | nenhuma | Checkout; Fly.BFF (status) |
| AWX.ERP.Connector.Api | `/api/faturamento/*`, `/api/checkout/etiqueta/{caixa}`, `/api/clientes/consultar`, `/api/pedidos/validar`, `/api/auditoria/movimentacao`, `/servicos/recebimento/contagem-concluida`, `/api/recebimento/nota-fiscal-entrada/sincronizar`, `/api/linx/produtos/sync`, `/api/produtos*`, `/api/produtos-cup*`, `/api/pedidos-b2c/*` | API key | Faturamento, Estoque, PedidosB2B, ACL; Linx/integração externa nas rotas de push `[assumption]` |
| AWX.IntegracaoLegadoWMS.Api | `/api/v1/wms/{triangulacao-fiscal,recebimento,produtos,produtos-cup,pedidos-b2c,volumes-expedicao,auditoria}/*` | API key | Checkout, Recebimento, Picking, PedidosB2C, Relatorios, ERP.Connector |
| AWX.Estoque.Api | `/api/produtos/{sync,existentes,por-cup/{cup},por-sku/{sku}}`, `/api/produtos-cup/sync` | nenhuma | ERP.Connector, ACL |
| AWX.Recebimento.Api | `POST /api/v1/recebimento/notas-fiscais-entrada/importar` | nenhuma | ERP.Connector (URL base completa, A-3) |
| AWX.PedidosB2C.Api | `/api/v1/pedidos-b2c` (POST, PUT, DELETE, GET status) | API key | ERP.Connector |
| AWX.PedidosB2B.Api | `/api/geracao-demanda/parametrizacao-por-cliente*`, `/api/geracao-demanda/simulacao` | nenhuma | Fly.BFF (`/pedidosb2b/**`) |
| AWX.Expedicao.Api | `POST /api/v1/expedicao/notas-fiscais` | nenhuma | nenhum chamador no repo |
| Awx.Relatorios.Ui.WebApi | `GET /api/v1/relatorios/triangulacao-fiscal/pedidos/{numeroPedido}` | API key | BFF externo `[assumption]` |
| AWX.Impressao.Api | `POST /api/etiquetas/checkout`, `POST /api/etiquetas/miniDanfeb2b` | nenhuma | Checkout, Faturamento |
| AWX.Fly.BFF | `/checkout/**`, `/faturamento/api/v1/faturamento/status/**`, `/pedidosb2b/**` | API key (`/health`, `/ready` isentos) | Frontend Fly `[assumption]` |

Todas as APIs expõem `GET /health` sem autenticação, exceto a `Awx.Faturamento.Ui.WebApi`, que não tem health check (C-9).

## HTTP consumido (outbound)

| De | Para | Chave da base URL | Rotas |
|---|---|---|---|
| Checkout | ACL | `IntegracaoLegadoWmsApi:Url` (+ `ApiKey`) | `POST /api/v1/wms/volumes-expedicao/gerar-identificador` |
| Checkout | Faturamento | `FaturamentoApi:Url` | status por caixa/CUP/pedido, persistir etiqueta, documento, reimprimir |
| Checkout | Impressao | `ImpressaoApi:Url` | `POST /api/etiquetas/checkout?idImpressora=` |
| Faturamento | ERP.Connector | `ErpConnector:BaseUrl` (+ `ErpConnector:ApiKey`) | faturar, faturar-b2c, obter-status, etiquetas; `/linx-integracao/servico/faturar` sem chamador |
| Faturamento | Impressao | `Impressao:BaseUrl` | checkout e miniDanfeb2b |
| ERP.Connector | Linx | `LinxIntegration:<Bloco>:ApiUrl` (15 blocos) | ver edges |
| ERP.Connector | ACL | `LinxIntegration:ProdutosCupWms:ApiUrl`, `LinxIntegration:ProdutosWms:ApiUrl` (+ `LinxIntegration:WmsApiKey`) | sincronizar produtos e CUP |
| ERP.Connector | Estoque | `AwxEstoque:BaseUrl` (sem API key) | existentes, sync de produtos e de CUP |
| ERP.Connector | Recebimento | `AwxRecebimento:BaseUrl` (sem API key) | POST na URL base, em lotes de `TamanhoDeLote` |
| ERP.Connector | PedidosB2C | `AwxPedidosB2C:BaseUrl` + `Rota` (+ `AwxPedidosB2C:ApiKey`) | POST do pedido |
| ACL | ERP.Connector | `ErpConnector:BaseUrl` (sem API key, sem retry) | contagem concluída, auditoria |
| ACL | Estoque | `Estoque:BaseUrl` (+ `Estoque:ApiKey`) | por-cup, por-sku |
| ACL | API WMS legado | `WmsLegadoApi:BaseUrl` | gerar identificador de volume |
| Estoque | ERP.Connector | `ErpConnector:BaseUrl` (+ `ErpConnector:ApiKey`) | resolver por CUP e por SKU |
| Recebimento | ACL | `IntegracaoLegadoWms:BaseUrl` (URL completa do endpoint, + `ApiKey`) | sincronizar NF de entrada |
| PedidosB2C Worker | ACL | `IntegracaoLegadoWms:BaseUrl` (sem API key) | `PUT /api/v1/wms/pedidos-b2c/{n}/status` |
| Picking Worker | ACL | `IntegracaoLegadoWms:BaseUrl` (+ `ApiKey`) | `POST /api/v1/wms/pedidos-b2c` |
| PedidosB2B | ERP.Connector | `ErpConnector:BaseUrl` | clientes/consultar, pedidos/validar |
| Relatorios | ACL | `IntegracaoLegadoWms:BaseUrl` (+ `ApiKey`) | triangulação por pedido |
| Impressao | Printers API | `PrintersApiBaseUrl` | `POST /print` |
| Fly.BFF | Checkout, Faturamento, PedidosB2B | `ReverseProxy:Clusters:<cluster>:Destinations:destination-1:Address` | catch-all; o destino de `cluster-pedidosb2b` não está no repo |

Quem chama a ACL sem API key (PedidosB2C Worker) e quem a ACL chama sem API key (ERP.Connector, que exige) são pendências (A-4, A-5).

## Filas e mensageria

| Recurso | Tipo | Produtor | Consumidor | Retry / DLQ |
|---|---|---|---|---|
| `awx_checkout_solicitacao` (fila e exchange topic, `RabbitMQ:AwxCheckoutFilaSolicitacao`) | fila | Full Picking B2B (`wms.picking.backend`), fora do monorepo | Checkout Worker | sem retry; DLQ `awx_checkout_solicitacao-dlq` |
| `faturamento.nota-fiscal.faturar.requested.v1` → fila `iniciar-faturamento` | exchange topic | Checkout (`NotaFiscalCommand`, `x-schema-version=2`, `x-entity-id`) | Faturamento Ui.Consumer (MassTransit, RK `#`) | retry 5s/15s/30s (MassTransit) |
| `awx_checkout_volume_expedicao` (`RabbitMq:AwxCheckoutFilaVolumeExpedicao`) | fila | externo ao monorepo, segundo a constituição; não identificado (A-11) | ERP.Connector Worker | `-retry-{N}s` (desligado por padrão), `-dlq` |
| `awx.pedidos-b2c.pedido-criado` → `awx.picking.pedido-b2c-criado` | exchange topic, RK = nome da exchange | PedidosB2C (outbox) | Picking Worker | `-retry-10s/30s/60s`, `-dlq` |
| `awx.pedidos-b2c.status-alterado` → `awx.pedidos-b2c.status-alterado.integracao-legado` | exchange topic | PedidosB2C (outbox) | PedidosB2C Worker | sem DLQ; nack com requeue |
| `x.awx.erp-connector.eventos`, RK `pedido-b2c.cancelado-externamente` | exchange topic | ERP.Connector (publisher confirms) | nenhum no repo (A-10) | — |
| `awx.faturamento.pedido-b2c-concluido` → fila de `RabbitMQ:AwxExpedicaoFilaFaturamentoPedidoB2cConcluido` | exchange topic | nenhum no repo (A-10) | Expedicao (Api e Worker) | `-retry-10s/30s/60s`, `-dlq` |

A constituição do repo lista esses nomes como dívida a renomear para o padrão `x.awx.<contexto>.eventos` / `q.awx.<contexto>.<entidade>-<fato>` (C-19).

## Jobs e agendamentos

| Job | Serviço | Periodicidade | O que faz |
|---|---|---|---|
| `ReconciliacaoFaturamentoWorker` | Faturamento Ui.Consumer | `ReconciliacaoFaturamento:IntervaloSegundos` (padrão 60s) | Confirma NF no ERP para faturamentos pendentes (C-55) |
| `OutboxDispatcherWorker` | PedidosB2C Worker | 5s, até 50 eventos | Publica eventos pendentes do outbox (C-70) |
| `SolicitacaoWorker`, `VolumeExpedicaoRabbitMqHostedService`, `PedidoB2CCriadoWorker`, `PedidoB2CStatusAlteradoConsumer`, `FaturamentoPedidoB2cConcluidoWorker` | vários | contínuo; reconexão em 10s | Mantêm os consumers RabbitMQ |
| `ErpConnectorConfiguracaoLogger` | Faturamento | no boot | Loga a base URL e o tamanho da chave do ERP, sem o valor |

Nenhum cron nem job de SQL Agent no código.

## Quem mais toca o meu schema

Pelo catálogo `docs/atlas/banco/WMS/` e pelo índice `docs/atlas/impacto/`:

- **`WMS.dbo.NotaFiscal`** (que o script 001 move para `Recebimento.NotaFiscal`, deixando sinônimo): tem triggers `tr_NOTAFISCAL_Insert/Update/Delete`, é referenciada pelas views `Recebimento.vwTriangulacaoFiscal` e `dbo.vwQualidadeNotaFiscal`, e o impacto lista 79 afetados: 36 objetos do banco Reserva, 32 do WMS, 6 jobs do SQL Agent e o `wms.servidor.backend` (distância 2). Mexer nela afeta o legado inteiro (C-43).
- **`WMS.dbo.PickingECommerce`** (script 006 adiciona `TraceId`; o código da ACL não a acessa): 248 afetados, com triggers próprias, 64 objetos do WMS, 119 do Reserva, 24 jobs e os repos `wms.ecommerce.backend`, `wms.servidor.backend` e `wms.picking.backend` (C-44).
- **`Reserva.dbo.FATURAMENTO` / `FATURAMENTO_PROD`** (lidas pela triangulação): 649 e 426 afetados; escritas e lidas por `reserva-net.b2b.backend`, `wms.conector.backend`, `wms.ecommerce.backend`, `wms.servidor.backend`, `wms.tms*` e dezenas de jobs (C-45).
- **`WMS.dbo.TipoPedido`**, **`WMS.dbo.EntidadeExternaNotaFiscal`**: só o AWX aparece como app de código no índice; TipoPedido tem 10 afetados no próprio banco.
- **`Recebimento.NotaFiscalItem`, `NotaFiscalItemContagem`, `Produtos.Produto`, `Produtos.CodigoBarraSku`, `dbo.ProdutosCup`, `pedido.Pedidos`, `pedido.PedidosItem`**: o índice só mostra o AWX; são objetos novos, de escrita exclusiva da ACL (o db/README diz o mesmo de `pedido.*`).
- **Postgres do AWX**: cada banco `pg-*` só é tocado pelo próprio serviço; o índice de impacto não mostra outro consumidor.
