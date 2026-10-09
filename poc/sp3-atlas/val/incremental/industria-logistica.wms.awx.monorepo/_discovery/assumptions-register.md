# Assumptions Register

> **Last updated:** 2026-10-06
> **Purpose:** Hipóteses, contradições e pendências que só uma pessoa resolve. Estado local de processo (git-ignorado).

O register da execução inicial (`af25344`, A-1 a A-31) não está nesta pasta; os IDs citados nos docs continuam valendo. Abaixo, só o que a atualização incremental `af25344..e495e61` acrescentou ou mudou. Modo code-only: nenhum item foi validado por pessoa.

| ID | Tipo | Afirmação / pergunta | Evidência | Status |
|---|---|---|---|---|
| A-3 (atualização) | contradição parcial resolvida | O Faturamento passou a enviar `X-API-KEY` ao ERP Connector. Continuam sem a chave: PedidosB2B → Connector, Worker do PedidosB2C → ACL, ACL → Connector (contagem e, nova, auditoria) | C-24, C-73 | needs SME |
| A-29 (atualização) | hipótese reforçada | A "API WMS" do identificador de volume é a `Reserva.WMS3.API` do `wms.servidor.backend`; agora só a ACL a chama, por `WmsLegadoApi:BaseUrl` | C-65 | needs SME (confirmar a URL configurada por ambiente) |
| A-32 | risco / contrato | A rota `api/recebimento/nota-fiscal-entrada/{erp}/sincronizar`, descrita no próprio código como a usada pelo worker `integracoes.wms.servicos-linx-wms`, foi removida. O worker externo já chama a rota sem `{erp}`? Senão a sincronização de NF de entrada responde 404 | C-64 | needs SME |
| A-33 | lacuna | Quem chama `POST api/pedidos-b2c/cancelamentos` (o código fixa `Origem = "Linx"`) e quem deve consumir `x.awx.erp-connector.eventos` / `pedido-b2c.cancelado-externamente`? Nenhum consumidor no repo; o PedidosB2C não cancela a partir dele | C-67 | needs SME |
| A-34 | lacuna | Quem publica `awx.faturamento.pedido-b2c-concluido`? Nenhum publicador no repo (nem o Faturamento B2C). O consumidor da Expedição roda na Api e no Worker ao mesmo tempo: intencional? | C-68 | needs SME |
| A-35 | lacuna | Quem chama `POST /api/v1/faturamento/b2c` e por que o resultado (Romaneio/Caixa) não é gravado no Faturamento | C-72 | needs SME |
| A-36 | lacuna | Quem chama `POST /api/v1/wms/auditoria/movimentacao` na ACL (auditoria de separação do WMS legado?) | C-73 | needs SME |
| A-37 | consentimento | Sign-off da Fase 5 e reescrita do README não concedidos (instrução do Atlas) | — | needs SME |
