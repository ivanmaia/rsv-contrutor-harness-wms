# Integrações e dependências

> **Last updated:** 2026-10-06
> **Scope:** Bancos, HTTP, filas e jobs de todos os subprojetos do monorepo AWX (`industria-logistica.wms.awx.monorepo`, commit `e495e61`; atualização incremental sobre `af25344`)
> **Mode:** code-only
> **Status:** code-derived, not validated by a person — see ../_discovery/assumptions-register.md

A lista linha a linha, com `arquivo:linha`, está em [`edges.csv`](../edges.csv) (292 arestas). IDs `C-n` apontam para o [índice de rastreabilidade](../_discovery/traceability-index.md); `A-n` para o registro de premissas. Bancos PostgreSQL próprios aparecem como `pg-<serviço>`: o nome físico não está no config (só em testes e READMEs).

## Visão geral

| Sistema | Propósito | Direção | Mecanismo | Quem usa (subprojeto) |
|---|---|---|---|---|
| Full Picking B2B API (repo `picking.backend`) | Entrega a caixa pronta para o checkout | inbound | RabbitMQ, fila `awx_checkout_solicitacao` | AWX.Checkout. **O payload do publicador (`Produtos`) não casa com o do consumidor (`Itens`)** (C-9, A-1) |
| ERP Linx (APIs `LinxIntegration:*:ApiUrl`) | Faturar (B2B e, novo, B2C "embalar pedido e-commerce"), status de NF, etiquetas, produtos, clientes, pedidos, contagem, auditoria, volume de expedição | outbound | REST | AWX.ERP.Connector apenas; o ERP alvo vem de `Erp:Tipo` (só `Linx`), não mais da rota (C-25, C-64) |
| Banco **WMS** legado (SQL Server) | Recebimento, produtos, CUP, pedidos B2C | read/write | Dapper, `WmsLegadoSql:ReadOnlyConnectionString` / `WriteConnectionString` | AWX.IntegracaoLegadoWMS apenas (C-32) |
| Banco **Reserva** (Linx), via sinônimos do WMS | Triangulação fiscal (`FATURAMENTO`, `FATURAMENTO_PROD`) | read | SQL pela conexão de leitura do WMS | AWX.IntegracaoLegadoWMS (C-39) |
| PostgreSQL por serviço | Estado próprio de cada serviço | read/write | EF Core + Npgsql, `PostgreSql:DefaultConnection` / `MigrationsConnection` | Checkout, Faturamento, Estoque, Picking, PedidosB2B, PedidosB2C, Expedição (novo), Recebimento (só o schema) |
| RabbitMQ | Eventos entre serviços e com o legado | pub/sub | RabbitMQ.Client (e MassTransit no Faturamento) | Checkout, Faturamento, ERP Connector (agora também publica), PedidosB2C, Picking, Expedição (C-6, C-67, C-68) |
| API do WMS legado (`WmsLegadoApi:BaseUrl`) | Gerar o identificador do volume de expedição | outbound | REST | Agora só a ACL chama; o Checkout passou a pedir à ACL. A rota casa com `Reserva.WMS3.API` do repo `wms.servidor.backend` (`CheckOutController.cs:37`, pelo Atlas) (C-65) |
| Printers API (`PrintersApiBaseUrl`) | Enviar ZPL à impressora | outbound | REST | AWX.Impressao |
| Fly (frontend) | Telas de checkout, faturamento e B2B | inbound | HTTP via AWX.Fly.BFF (YARP) | Checkout, Faturamento, PedidosB2B (C-50) |
| Worker Linx externo (`integracoes.wms.servicos-linx-wms`) | Empurrar NF de entrada, produtos e CUP | inbound | REST no ERP Connector | Chamador citado em comentário, fora do repo `[assumption]` (A-29) |
| Sistema externo de cancelamento B2C (não identificado) | Avisar pedido B2C cancelado fora do AWX | inbound | REST no ERP Connector, `POST api/pedidos-b2c/cancelamentos` | Chamador não está no repo; o código fixa `Origem = "Linx"` `[assumption]` (A-33) |
| Sentry | Erros | outbound | SDK (`Dsn` ou `Sentry:Dsn`) | Todos os Api |

## Banco de dados

R = leitura, W = escrita, Exec = DDL/migration/proc. Detalhe por operação no `edges.csv`.

### SQL Server WMS (legado) e Reserva, só via AWX.IntegracaoLegadoWMS

| Objeto | R | W | Exec | Observação |
|---|---|---|---|---|
| `WMS.Recebimento.NotaFiscal` (sinônimo `dbo.NotaFiscal`) | R | W (insert, update de status) | DDL: schema `Recebimento` criado e tabela legada transferida de `dbo` | Dedup por ChaveNFE ou fornecedor+número+série (C-35) |
| `WMS.Recebimento.NotaFiscalItem` | R | W | CREATE TABLE | Mesma transação da NF |
| `WMS.Recebimento.NotaFiscalItemContagem` | | W | CREATE TABLE | **INSERT omite `Produto`, `CorProduto`, `Tamanho`, que são NOT NULL também no HML**: a tabela fica sem linhas (C-36, A-4) |
| `WMS.dbo.EntidadeExternaNotaFiscal` | | W | | Romaneios/pedidos devolvidos pelo Linx na contagem, `Processado=0` (C-37) |
| `WMS.Produtos.Produto` | R | W (upsert com UPDLOCK) | CREATE SCHEMA + TABLE | |
| `WMS.dbo.ProdutosCup` | R | W | CREATE TABLE | Idempotente por CupId (409) |
| `WMS.Produtos.CodigoBarraSku` | | | CREATE TABLE | Nenhum código da aplicação usa; ausente no catálogo HML (C-52) |
| `WMS.pedido.Pedidos`, `WMS.pedido.PedidosItem` | R | W | CREATE SCHEMA + TABLE | Projeção do pedido B2C (C-38) |
| `WMS.dbo.TipoPedido` | R | | FK de `pedido.Pedidos` | Busca por `Descricao` |
| `WMS.dbo.PickingECommerce` | | | ALTER ADD `TraceId` | Tabela legada; coluna ausente no HML (C-52, A-14) |
| `Reserva.dbo.FATURAMENTO`, `Reserva.dbo.FATURAMENTO_PROD` | R (NOLOCK) | | | Nome sem schema no código; resolvido pelos sinônimos `WMS.dbo.FATURAMENTO` / `faturamento_prod` (C-39) |

Scripts em `src/Integrations/AWX.IntegracaoLegadoWMS/db/` são entregues ao DBA e têm numeração duplicada (três `006`, dois `007`, dois `008`); `006_recebimento_nota_fiscal_contagem.sql` não é idempotente (A-14).

### PostgreSQL próprio de cada serviço (schema `public`, salvo Recebimento)

| Serviço | Tabelas (R/W) | Migrations |
|---|---|---|
| Checkout (`pg-checkout`) | `solicitacao`, `solicitacao_item`, `volume`, `sessao_conferencia_checkout`, `cancelamento_item_solicitacao`, `parametrizacoes`, `parametrizacoes_log` (R/W); `faturamento_caixa_tipo`, `status_faturamento` (R, seed em migration); `motivo_cancelamento` (R, sem seed em migration, A-26) | 3, aplicadas no boot fora de Development com advisory lock |
| Faturamento (`pg-faturamento`) | `faturamento`, `caixa_faturamento`, `item_embalado`, `documento` (R/W); `faturamento_caixa_tipo` (seed, sem leitor). Consulta de status e reconciliação agora leem a caixa embalada e seus itens para validar a NF devolvida (C-66) | 10; duas com SQL cru (renumeração de status, tipo de documento) |
| Estoque (`pg-estoque`) | `produtos`, `produtos_cup`, `produtos_codigo_barra` (R/W) | 6 |
| Picking (`pg-picking`) | `picking_ecommerce`, `picking_ecommerce_item`, `outbox_eventos` (W); sequências NumeroOR/NumeroLote | 5 |
| PedidosB2B (`pg-pedidosb2b`) | `geracao_demanda_parametrizacao_por_cliente` (R/W, soft delete) | 1 |
| PedidosB2C (`pg-pedidosb2c`) | `pedidos`, `pedido_itens`, `outbox_eventos` (R/W) | 1 |
| Recebimento (`pg-recebimento`) | nenhuma tabela, só o schema `recebimento` | 1 |
| Expedição (`pg-expedicao`) | `expedicao.notas_fiscais` (R/W; índice único em `Chave`; status Pendente/EmLote/Enviada/Cancelada, só Pendente é gravado hoje) | 1 (`20260922185345_RegistrarNotaFiscalExpedicao`) |

ERP Connector, Relatórios, Impressão e Fly.BFF não têm banco. AgentOperacao, CrossDocking e Devolução têm DbContext sem entidades; Expedição deixou de ser scaffold (C-2, C-68).

## HTTP exposto (inbound)

Autenticação: header `X-API-KEY` (middleware do SharedKernel, `/health` excluído; o log de rejeição agora informa se o tamanho confere e se há espaços nas pontas, sem o valor) só em ERP Connector, IntegracaoLegadoWMS, PedidosB2C, Relatórios e Fly.BFF. **Checkout, Faturamento, Estoque, PedidosB2B, Recebimento, Impressão e a nova API da Expedição não autenticam nada** (C-7, C-8, A-7). Todos expõem `GET /health`, exceto a WebApi do Faturamento.

| Subprojeto | Rotas (resumo; lista completa no edges.csv) |
|---|---|
| AWX.Checkout.Api | `/api/solicitacao/*` (consulta por pedido/CUP, cancelamento, conferir item, sessão de conferência, fechar parcial, atualizar) · `POST /api/checkout/salvar` · `/api/checkout/etiquetas/*reimprimir` · `/api/parametrizacoes` · `/api/cancelamentos` (+ CSV) · `/api/tipos-caixa` · `GET /pedidos/{pedido}` (mock) |
| Awx.Faturamento.Ui.WebApi | `POST /api/v1/faturamento` · `POST /api/v1/faturamento/b2c` (novo: proxy síncrono, 200 com Romaneio/Caixa) · `GET /api/v1/faturamento/status?caixa|cup|numeroPedido` · `GET /api/faturamento/status/{caixa}` (ao vivo no ERP) · `/api/v1/faturamento/etiquetas/{checkout,mini-danfe,reimprimir}` · `/api/v1/documentos/*` · `/api/v1/etiquetas/*/imprimir` |
| AWX.ERP.Connector.Api | `api/faturamento/{faturar, faturar-b2c, obter-status/{id}?pedido&emitidaAPartirDe}` · `api/faturamento/etiqueta-danfe/{caixa}` · `api/checkout/etiqueta/{caixa}?pedido=` · `api/clientes/consultar` · `api/pedidos/validar` · `api/pedidos-b2c/{lote, cancelamentos}` · `api/auditoria/movimentacao` · `api/produtos-cup/{sync,{cup}/resolver}` · `api/linx/produtos/sync` · `api/produtos/{sku}/resolver` · `servicos/recebimento/contagem-concluida` · `api/recebimento/nota-fiscal-entrada/sincronizar`. **O segmento `{erp}` saiu de todas as rotas, e a rota `.../{erp}/sincronizar`, que o próprio código descrevia como contrato do worker Linx, foi removida** (C-64, A-32) |
| AWX.IntegracaoLegadoWMS.Api | `/api/v1/wms/triangulacao-fiscal/pedidos/{n}` · `/api/v1/wms/recebimento/{notas-fiscais-entrada/sincronizar, notas-fiscais-entrada/{id}/itens, contagem-concluida}` · `/api/v1/wms/produtos/{sku, por-cup/{cup}, por-sku/{sku}, sincronizar}` (os GET por CUP/SKU gravam) · `/api/v1/wms/produtos-cup/sincronizar` · `/api/v1/wms/pedidos-b2c` (POST, PUT status) · `/api/v1/wms/volumes-expedicao/gerar-identificador` (novo) · `/api/v1/wms/auditoria/movimentacao` (novo, repasse ao ERP Connector) (C-73) |
| AWX.Estoque.Api | `api/produtos/{sync, existentes, por-cup/{cup}, por-sku/{sku}}` · `api/produtos-cup/sync` |
| AWX.PedidosB2B.Api | `/api/geracao-demanda/parametrizacao-por-cliente` (CRUD, clientes, importar modelo/prévia/confirmar) · `/api/geracao-demanda/simulacao` (placeholder) |
| AWX.PedidosB2C.Api | `/api/v1/pedidos-b2c` (POST, PUT, DELETE, GET status) |
| AWX.Recebimento.Api | `POST /api/v1/recebimento/notas-fiscais-entrada/importar` |
| Awx.Relatorios.Ui.WebApi | `GET /api/v1/relatorios/triangulacao-fiscal/pedidos/{n}` |
| AWX.Impressao.Api | `POST api/etiquetas/checkout` · `POST api/etiquetas/miniDanfeb2b` (query `idImpressora`). Com `Impressao:ModoSimulacao=true` devolve 200 com o ZPL e não imprime; Faturamento e Checkout repassam esse ZPL na reimpressão (C-69) |
| AWX.Expedicao.Api | `POST api/v1/expedicao/notas-fiscais` (201; 409 se a chave já existe) |
| AWX.Fly.BFF (YARP) | `/checkout/**` → Checkout · `/faturamento/api/v1/faturamento/status/**` → Faturamento · `/pedidosb2b/**` → PedidosB2B (sem destino configurado no repo) |
| AWX.Picking.Api, Workers, scaffolds (AgentOperacao, CrossDocking, Devolução) | só `/health` |

## HTTP consumido (outbound)

| Origem | Chave de base URL | Destino e rotas | Notas |
|---|---|---|---|
| Checkout | `FaturamentoApi:Url` | Faturamento: `api/faturamento/status/{caixa}` (no atualizar caixa, agora uma vez por volume confirmado), `api/v1/faturamento/status?cup/numeroPedido`, `etiquetas/checkout`, `etiquetas/reimprimir`, `api/v1/documentos/{chave}` (também no salvar, para imprimir com os dados de entrega persistidos) | timeout 30 s |
| Checkout | `ImpressaoApi:Url` | Impressão: `api/etiquetas/checkout?idImpressora=` | best-effort, só se `IdImpressora` vier no salvar |
| Checkout | `IntegracaoLegadoWmsApi:Url` (+ `ApiKey`; ambos obrigatórios no boot) | ACL `POST api/v1/wms/volumes-expedicao/gerar-identificador` | X-API-KEY; substituiu `WmsApi:Url` (C-65) |
| Faturamento | `ErpConnector:BaseUrl` | ERP Connector: `faturamento/{faturar, faturar-b2c, obter-status/{caixa}?pedido&emitidaAPartirDe}`, `checkout/etiqueta/{caixa}?pedido=`, `faturamento/etiqueta-danfe` | **Agora envia `X-API-KEY`** (`ErpConnector:ApiKey`, obrigatória e validada no boot); o achado A-3 deixa de valer para o Faturamento (C-24) |
| Faturamento | `Impressao:BaseUrl` | Impressão: `checkout`, `miniDanfeb2b` | timeout 30 s |
| PedidosB2B | `ErpConnector:BaseUrl` | `api/clientes/consultar`, `api/pedidos/validar` | **Sem `X-API-KEY`** (A-3) |
| PedidosB2C Worker | `IntegracaoLegadoWms:BaseUrl` | ACL `PUT /api/v1/wms/pedidos-b2c/{n}/status` | **Sem `X-API-KEY`** (A-3) |
| Picking Worker | `IntegracaoLegadoWms:BaseUrl` | ACL `POST api/v1/wms/pedidos-b2c` | X-API-KEY, retry exponencial |
| Recebimento | `IntegracaoLegadoWms:BaseUrl` (URL completa) | ACL `notas-fiscais-entrada/sincronizar` | X-API-KEY, timeout 120 s, retry linear |
| Relatórios | `IntegracaoLegadoWms:BaseUrl` | ACL `triangulacao-fiscal/pedidos/{n}` | X-API-KEY |
| Estoque | `ErpConnector:BaseUrl` | `api/produtos-cup/{cup}/resolver`, `api/produtos/{sku}/resolver` | X-API-KEY, retry linear |
| IntegracaoLegadoWMS | `ErpConnector:BaseUrl` | `servicos/recebimento/contagem-concluida`, `api/auditoria/movimentacao` (novo) | **Sem `X-API-KEY`** (A-3) |
| IntegracaoLegadoWMS | `WmsLegadoApi:BaseUrl` (URL absoluta obrigatória no boot) | API do WMS legado: `POST api/checkout/volume-expedicao/gerar-identificador` | Sem chave; retry linear (`RetryCount`, `BackoffSeconds`, `MaxWaitSeconds`); erro se vier sem `Sequencial` (C-65) |
| IntegracaoLegadoWMS | `Estoque:BaseUrl` | `api/produtos/por-cup/{cup}`, `por-sku/{sku}` | X-API-KEY |
| ERP Connector | `LinxIntegration:{Faturamento, FaturamentoB2c, StatusFatura, EtiquetaCheckout, EtiquetaDanfe, ProdutoPorSku, ProdutoPorCup, ContagemConcluida, Cliente, Pedido, Auditoria, VolumeExpedicao}:ApiUrl` | Linx | Timeout 2 min; retry Polly também em POST não idempotente (C-31, A-18). `FaturamentoB2c` é obrigatória no boot. O status de fatura repassa `pedido` e `emitidaAPartirDe`; 404 `FATURAMENTO_NAO_ENCONTRADO` vira "aguardando NF" (C-66) |
| ERP Connector | `LinxIntegration:{ProdutosWms, ProdutosCupWms}:ApiUrl` | ACL `produtos/sincronizar`, `produtos-cup/sincronizar` | `LinxIntegration:WmsApiKey`. `RecebimentoWms:ApiUrl` é obrigatório no boot e não tem uso |
| ERP Connector | `AwxEstoque:BaseUrl`, `AwxRecebimento:BaseUrl`, `AwxPedidosB2C:BaseUrl` | Estoque `produtos/{sync,existentes}`, `produtos-cup/sync`; Recebimento `importar`; PedidosB2C `POST /api/v1/pedidos-b2c/` | Fan-out CUP×Produto e NF de entrada (C-28, C-30) |
| Impressão | `PrintersApiBaseUrl` | `POST /print` com ZPL | |
| Fly.BFF | `ReverseProxy:Clusters:<cluster>:Destinations:destination-1:Address` | Checkout, Faturamento, PedidosB2B | Destinos só no launchSettings (localhost) |

## Filas e mensageria

Biblioteca comum `AWX.EventBus.RabbitMQ` (RabbitMQ.Client 7): DLQ `{fila}-dlq` via default exchange, sem retry por padrão; agora traz helpers de retry por fila TTL `{fila}-retry-{N}s` (contagem por header e `x-death`), fábrica de conexão e propriedades de evento padrão (`x-schema-version`, `x-producer`, `x-event-type`). O Checkout segue com cópia própria da base (C-6). O Faturamento usa MassTransit.

| Fila / exchange | Publicador | Consumidor | Contrato | Notas |
|---|---|---|---|---|
| fila `awx_checkout_solicitacao` (config `RabbitMQ:AwxCheckoutFilaSolicitacao`) | Full Picking B2B (repo `picking.backend`, default exchange, rk = nome da fila) | Checkout `SolicitacaoConsumer` (declara exchange topic homônimo + binding `#`, DLQ) | publicador `SolicitacaoCheckoutObjetoValor {…, Produtos[]}`; consumidor `SolicitacaoMessage {…, Itens[]}` | **Descompasso `Produtos` × `Itens`: a solicitação é gravada sem peças e a mensagem recebe ack** (C-9, C-10, A-1). Sem idempotência; exceção deixa a mensagem sem ack (C-18, A-6) |
| exchange topic `faturamento.nota-fiscal.faturar.requested.v1` | Checkout (5 pontos: pré-checkout, salvar, parcial, retentativa, atualizar caixa) | Faturamento, fila `iniciar-faturamento`, rk `#`, retry 5/15/30 s | `NotaFiscalCommand` (Checkout) = `IniciarFaturamentoEvent` (Faturamento), acoplados por shape com teste E2E | Nenhum evento de resultado volta ao Checkout (C-57, A-5) |
| fila `awx_checkout_volume_expedicao` | **nenhum no repo** | ERP Connector `VolumeExpedicaoConsumer` → Linx | `VolumeExpedicaoCheckoutMessage` | Retry TTL `-retry-{N}s` só se `LinxIntegration:QueueRetry:Enabled` (A-9) |
| exchange topic `awx.pedidos-b2c.pedido-criado` | PedidosB2C (outbox, a cada 5 s) | Picking, fila `awx.picking.pedido-b2c-criado`, retry 10/30/60 s → DLQ | `PedidoB2CCriadoEvent` v1 | |
| exchange topic `x.awx.erp-connector.eventos`, rk `pedido-b2c.cancelado-externamente` (novo) | ERP Connector Api, um evento por pedido distinto do lote, com publisher confirms | **nenhum consumidor no repo** | `PedidoB2CCanceladoExternamenteEvent` v1 (`NumeroPedido`, `Origem`, `TraceId`) | A resposta HTTP diz por pedido se o barramento aceitou; o Connector Api passou a exigir credenciais RabbitMQ no boot (C-67, A-33) |
| exchange topic `awx.faturamento.pedido-b2c-concluido` (novo) | **nenhum no repo** | Expedição, fila `RabbitMQ:AwxExpedicaoFilaFaturamentoPedidoB2cConcluido`, retry 10/30/60 s → DLQ (erro de validação vai direto à DLQ) | `FaturamentoPedidoB2cConcluidoEvent` v1 | Grava a NF em `expedicao.notas_fiscais`; o consumidor roda no Worker **e** na Api (C-68, A-34) |
| exchange topic `awx.pedidos-b2c.status-alterado` | PedidosB2C (outbox) | PedidosB2C Worker, fila `awx.pedidos-b2c.status-alterado.integracao-legado` → ACL | `PedidoB2CStatusAlteradoEvent` | Falha na ACL = nack com requeue sem limite nem DLQ (A-17) |

A chave `AwxCheckoutFilaSolicitacao` também está no appsettings do Worker do ERP Connector, mas nenhum código do Connector a lê (C-27, A-10).

## Jobs e agendamentos

Nenhum cron/scheduler externo no repo; tudo é `BackgroundService` dentro dos Workers.

| Job | Subprojeto | Cadência | Efeito |
|---|---|---|---|
| `ReconciliacaoFaturamentoWorker` | Faturamento Consumer | a cada 60 s (`ReconciliacaoFaturamento:IntervaloSegundos`), lote 50 | Confirma no ERP faturamentos pendentes, agora só se a NF for do pedido da caixa, emitida a partir da véspera da embalagem e com StatusNfe 5; divergência vai para `msg_erro`; backoff min(2 × 2^tentativas, 30) min; `NaoConfirmado` após 48 h (C-22, C-66) |
| `OutboxDispatcherWorker` | PedidosB2C Worker | a cada 5 s, 50 eventos | Publica o outbox; `Falhou` após 3 tentativas (C-40) |
| `SolicitacaoWorker`, `PedidoB2CCriadoWorker`, `PedidoB2CStatusAlteradoConsumer`, `VolumeExpedicaoRabbitMqHostedService`, `FaturamentoPedidoB2cConcluidoWorker` (novo) | Checkout, Picking, PedidosB2C, ERP Connector, Expedição (Worker e Api) | contínuo | Consumidores de fila, reconexão a cada 10 s |
| Migrations EF no boot | Todos os serviços com Postgres | a cada start (fora de Development; o Worker do Picking também em Development) | Aplica o schema |

## Quem mais toca o meu schema

Fonte: `extract/db-hml/{WMS,Reserva}/{dependencies,synonyms,columns}.csv` e `modules/`. Só os objetos legados que a ACL cria ou altera; os bancos Postgres do AWX (incluindo o novo `expedicao.notas_fiscais`) não estão no catálogo. As mudanças de `e495e61` não tocam objetos do WMS nem do Reserva, e o índice de impacto não muda para este repo.

| Objeto do AWX no WMS | Quem mais referencia (HML) | Efeito |
|---|---|---|
| `WMS.Recebimento.NotaFiscal` / sinônimo `dbo.NotaFiscal` | 21 objetos do WMS (ex.: `dbo.PrFinalizaNotasFiscais`, `prConsultaStatusContagemNotaFiscal`, `prIncluirNotasFiscaisSemStatus`, `RSV_WMS3_GERA_XD_3.0`, views `vwQualidadeNotaFiscal`, `vwEnderecamentoStatus`, `vwPerformanceRecebimento`, trigger `trVoltarStatusOperacao`); triggers `Recebimento.tr_NOTAFISCAL_{Insert,Update,Delete}` gravam em `Audit.dbo.ADT_WMS_NOTAFISCAL`; procs do Reserva `PR_RSV_RECEBIMENTO_AUTOMACAO`, `PR_RSV_RECEBIMENTO_GERA_OP_TRANSFORMACAO_AUTOMATICO`, `RSV_GERA_OP_DE_TRANSFORMACAO` (C-51) | A tabela é do legado: o AWX move o schema e grava nela, e todo o recebimento legado continua lendo |
| `WMS.dbo.PickingECommerce` (coluna `TraceId`) | 69 módulos do WMS (ex.: `pREPAAutomaticaEnderecaProdutoECommerceColetor`, `p_RSV_WMS_REPROCESSA_PEDIDO`, `PR_WMS_LISTAR_CAIXAS_COLMEIA`, `Quarentena.prRetornaPedidoCheckoutCaixa`) e procs Reserva `RSV_ATG_ECOMMERCE_SYNC_PEDIDOS_20191130`, `RSV_ECOMMERCE_PEDIDOS_ACOMPANHAMENTO` | Tabela central do picking e-commerce legado; a coluna `TraceId` do script 006 não existe no HML (C-52) |
| `Recebimento.NotaFiscalItem`, `NotaFiscalItemContagem`, `Produtos.Produto`, `dbo.ProdutosCup`, `pedido.Pedidos`, `pedido.PedidosItem`, `dbo.EntidadeExternaNotaFiscal` | Nenhuma proc, view ou trigger do WMS ou do Reserva no HML | Hoje só o AWX usa; quem lê `EntidadeExternaNotaFiscal` (`Processado=0`) não aparece (C-53, A-4) |
| `Produtos.CodigoBarraSku` | Não existe no HML | Script 008 não aplicado em homologação (C-52) |
| `dbo.TipoPedido` | Nenhuma dependência registrada | Lida pela ACL, FK de `pedido.Pedidos` |
| Sinônimos `WMS.dbo.FATURAMENTO`, `faturamento_prod`, `FATURAMENTO_CAIXA_TIPO` → `Reserva.dbo.*` | Tabelas do Linx | Leitura cross-database da triangulação; `FATURAMENTO_CAIXA_TIPO` é espelhada em Postgres por Checkout e Faturamento (C-39) |
