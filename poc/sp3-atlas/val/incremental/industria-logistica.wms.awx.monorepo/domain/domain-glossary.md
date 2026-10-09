# Glossário de domínio

> **Last updated:** 2026-10-06
> **Scope:** Termos de negócio usados no código do monorepo AWX (`industria-logistica.wms.awx.monorepo`, commit `e495e61`)
> **Mode:** code-only
> **Status:** code-derived, not validated by a person — see ../_discovery/assumptions-register.md

Significados tirados do que o código faz, não de uma definição de negócio. "Área" = serviço/subprojeto do monorepo; `cross-cutting` = usado por mais de um.

| Termo | Área | Significado (pelo código) |
|---|---|---|
| AWX | cross-cutting | Azzas Warehouse eXecution System: plataforma de microsserviços que substitui progressivamente o WMS legado |
| ACL (AWX.IntegracaoLegadoWMS) | integracao-legado-wms | Única porta do AWX para o banco do WMS legado; os serviços falam com ela por HTTP |
| ERP Connector | erp-connector | Ponte HTTP/RabbitMQ entre AWX e o ERP Linx; sede das orquestrações entre contextos (ex.: CUP×Produto) |
| Linx | cross-cutting | ERP. Único valor de `ErpTipo` (`Linx = 1`); o ERP Connector o lê de `Erp:Tipo` |
| Solicitação | checkout | Pedido a conferir no checkout, recebido pela fila `awx_checkout_solicitacao` (Identificador, NumeroPedido, NomeCliente, CodigoBarraCaixa, itens) |
| CUP | cross-cutting | Código único por peça; no checkout cada item da solicitação é uma peça com seu CUP. Expansão da sigla não aparece no código |
| SKU | cross-cutting | Chave de produto (produto + cor + tamanho) no Estoque e na ACL |
| Volume / Caixa | checkout, faturamento | Caixa física de expedição. No checkout o `Identificador` vem do sequencial do WMS; no faturamento "caixa" é a chave do faturamento no ERP |
| Rascunho / Confirmado | checkout | Estados do volume: rascunho enquanto a sessão de conferência está aberta, confirmado ao salvar o checkout |
| Sessão de conferência | checkout | Sessão por terminal/operador em que as peças são bipadas (EmAndamento, Finalizada, Abortada) |
| Fechamento parcial | checkout | Várias caixas por solicitação; ligado por padrão, salvo parametrização ou pré-checkout |
| Faturamento pré-checkout / pós-checkout | checkout | Se a NF é pedida ao ERP na chegada da solicitação (pré) ou ao salvar o checkout (pós); decidido por armazém em `parametrizacoes` |
| Parametrização (checkout) | checkout | Configuração por armazém: faturar pré-checkout, código do armazém no Linx, permitir fechamento parcial |
| TipoCaixa / TipoCaixaFaturamento | checkout, faturamento | Tipo físico (Papelão, Sacola) vs. código de caixa do Linx (001–005, CSS, CX 01–05, NCG, NCM, NCS), espelho de `Reserva.dbo.FATURAMENTO_CAIXA_TIPO` |
| Embalador / Operador | checkout, faturamento | Quem embalou; "SISTEMA" no pré-checkout. Desde `e495e61` é texto livre (até 64 caracteres no fechamento parcial), não mais número |
| Motivo de cancelamento | checkout | Qualidade, Perda da peça, Outros (exige descrição) |
| Assistente / Autorizador | checkout | Operador e supervisor registrados num cancelamento de peça |
| Canal de expedição | checkout | B2C = 1, B2B = 2, enviado ao WMS para gerar o identificador do volume |
| StatusFaturamento | faturamento, checkout | AProcessar 1, EmProcessamento 2, Criada 3, Faturado 4, ErroAoFaturar 5, NaoConfirmado 6 (mesma numeração nos dois serviços) |
| Reconciliação | faturamento | Job que confirma no ERP os faturamentos pendentes, com backoff e janela de 48 h |
| Documento | faturamento | Registro chave/valor (jsonb) que guarda etiquetas persistidas (`{CAIXA}_CHECKOUT`, `{CAIXA}_MINIDANFE`) |
| Etiqueta checkout B2B | faturamento, impressao | Etiqueta ZPL da caixa com cliente, transportadora, lote |
| Mini DANFE B2B | faturamento, impressao | Etiqueta fiscal da caixa; só é persistida ou reimpressa com NF autorizada (StatusNfe 5) |
| Vínculo NF × caixa | faturamento | Regra que aceita a NF devolvida pelo ERP só se os pedidos dela forem os dos itens embalados na caixa e a emissão for no máximo 1 dia antes da embalagem |
| Faturamento B2C (embalar pedido e-commerce) | faturamento, erp-connector | Chamada síncrona ao Linx com pedido, produtos e caixa, que devolve Romaneio, Caixa e Mensagem; não é gravada no AWX |
| Cancelamento externo (B2C) | erp-connector | Fato "pedido B2C cancelado fora do AWX", publicado por pedido; `Origem` fixa "Linx" |
| Movimentação de auditoria | integracao-legado-wms, erp-connector | Perdas e ganhos por SKU de uma auditoria de separação (IdAuditoria, armazém, responsável) enviados ao Linx, que devolve romaneios de perda e de ganho |
| NF de expedição | expedicao | NF de um pedido B2C faturado (chave de 44, pedido, filial, transportadora, loja de retirada, número, séries) aguardando expedição: Pendente, EmLote, Enviada, Cancelada |
| Modo simulação (impressão) | impressao | `Impressao:ModoSimulacao`: gera o ZPL e o devolve em vez de enviar à impressora |
| Volume de expedição (mensagem) | erp-connector | `VolumeExpedicaoCheckoutMessage` consumida da fila `awx_checkout_volume_expedicao` e enviada ao Linx |
| Clifor | cross-cutting | Código do cliente/fornecedor no Linx |
| Armazém | cross-cutting | Armazém do CD (`IdArmazem` numérico no AWX; `CodigoArmazem` no Linx) |
| Pedido B2C | pedidos-b2c, picking | Pedido de e-commerce (NumeroPedido, Seller, TipoPedido, Armazém, itens por SKU) |
| OnDemand / JaFoiOnDemand | pedidos-b2c, picking | Flags do item B2C. Significado de negócio não aparece no código |
| Outbox (OutboxEvento) | pedidos-b2c, picking | Tabela de eventos a publicar (Pendente, Publicado, Falhou); no Picking funciona como log de tentativas |
| PickingEcommerce | picking | Registro local de recebimento de um pedido B2C, com NumeroOR e NumeroLote gerados por sequência |
| NumeroOR / NumeroLote | picking | Sequências locais (a partir de 53000000 e 28000000). Expansão de "OR" não aparece no código |
| Parametrização por cliente | pedidos-b2b | Regras de geração de demanda por cliente e lote: tipo de ordem (Franquia/Atacado), faixa de faturamento, validade |
| Geração de demanda | pedidos-b2b | Funcionalidade B2B; a simulação ainda devolve "Funcionalidade em desenvolvimento." |
| Tipo Ordem Reserva | pedidos-b2b | Franquia = 1, Atacado = 2 |
| Vigente / Vencido | pedidos-b2b | Status calculado da parametrização por `DataValidade >= hoje` |
| Nota Fiscal de Entrada | recebimento, integracao-legado-wms | NF de recebimento; origens aceitas Fornecedor, Loja, CrossDockingRepa |
| Importada / JaImportada | recebimento | Resultado por NF: gravada agora, ou já existia (409 na ACL) |
| Contagem concluída | integracao-legado-wms, erp-connector | Fim da conferência de uma NF de entrada; envia contados, sobras e faltas ao Linx |
| Sobra / Falta | integracao-legado-wms, erp-connector | Divergências da contagem; o Linx devolve romaneios e pedidos que ficam em `dbo.EntidadeExternaNotaFiscal` |
| Romaneio | integracao-legado-wms, erp-connector | Documento Linx devolvido na contagem (sobra/falta, entrada/saída, devolução) |
| StatusEnvioErp | integracao-legado-wms | PENDENTE, ENVIADO, FALHA da contagem para o ERP |
| Triangulação fiscal | relatorios, integracao-legado-wms | Relatório de volumes de um pedido com NF de saída (armazém de origem), lido do Linx |
| Produto / ProdutoCup / CodigoBarraSku | estoque, integracao-legado-wms | Cadastro de produto por SKU, vínculo CUP→SKU e código de barras→SKU |
| Grade / Tamanho | estoque, integracao-legado-wms, erp-connector | Grade e índice de tamanho (1–48); na NF de entrada "a grade vira o tamanho no cadastro" |
| Grife / Grupo / SubGrupo / NCM | estoque | Classificação do produto vinda do ERP |
| Fly | cross-cutting | Novo frontend; o AWX.Fly.BFF é o seu proxy para os serviços AWX |
