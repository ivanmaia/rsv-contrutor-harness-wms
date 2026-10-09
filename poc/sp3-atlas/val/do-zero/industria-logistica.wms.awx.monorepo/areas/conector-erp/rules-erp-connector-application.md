# Regras do conector ERP (Awx.ErpConnector.Application)

> **Last updated:** 2026-10-06
> **Scope:** Regras e orquestração em `src/Integrations/AWX.ERP.Connector/src/Application` e `Infrastructure`; agrupamento pelo código, `[unverified]` como conceito de negócio
> **Mode:** code-only
> **Status:** code-derived, not validated by a person — see ../../_discovery/assumptions-register.md

O conector não tem banco. Cada bloco `LinxIntegration:<Bloco>:ApiUrl` vira um HttpClient nomeado com timeout de 2 min e retry linear de `LinxIntegration:HttpRetry`. O ERP é escolhido por `Erp:Tipo` (só `Linx` existe); a rota não carrega `{erp}` (C-30).

## Regras

- **Faturamento** — cliente (`Clifor`) e armazém do lote saem da primeira caixa; resposta "Fatura Criada" ou "Erro ao Faturar" conforme o Linx; Linx 400 vira `BAD_REQUEST_400`, outros erros `BAD_GATEWAY_502`; há também `TIMEOUT_2MIN`, `EMPTY_RESPONSE`, `DESERIALIZATION_ERROR`, `ERP_NAO_SUPORTADO`. Lotes com clifor ou armazém misturados são pendência (A-16) (C-61).
- **Status de fatura** — Linx 404 "Faturamento não encontrado" vira "Aguardando emissão de NF" com `Encontrado=false`; encontrado vira "Faturado"; `DentroDoPrazoCancelamento` assume `true` quando o Linx não informa (C-62).
- **Fan-out CUP×Produto** (`POST /api/produtos-cup/sync`) — por item: exige `CupId` e `Sku`; CUP repetido no lote conta como JaExistia; grava primeiro no Estoque e, se falhar, marca Falha ("reenvie"); depois envia ao WMS legado via ACL, onde 409 conta como JaExistia; a exceção de um item não afeta os outros. Responde 200 com o estado de cada CUP (C-63).
- **Produtos (push do Linx)** — lista vazia dá 400; se o Estoque falhar responde 502 sem chamar o WMS; o envio ao WMS é best-effort; o código de barras gravado no Estoque é o próprio SKU (C-64).
- **Resolver por SKU/CUP** — consulta só o Linx, sem gravar; 404 vira `ProdutoNaoEncontrado`/`CupNaoEncontrado` (C-65).
- **NF de entrada** — para cada nota garante os SKUs no Estoque (SKU novo sem descrição, NCM ou grade dá `RECEBIMENTO_PRODUTO_INCOMPLETO`); envia ao AWX.Recebimento em lotes de `AwxRecebimento:TamanhoDeLote` (100); um lote com erro conta todas as suas notas como falha; o retorno diz "Sincronizado" ou "SincronizadoComFalhas" e que as falhas "serão reenviadas na próxima execução" (C-66).
- **Contagem concluída e auditoria** — repassam ao Linx e devolvem os romaneios (sobra/falta, perda/ganho); erro vira `LINX_CONTAGEM_FALHOU` / `LINX_AUDITORIA_FALHOU` (C-67).
- **Volume de expedição** (Worker) — sem `LinxIntegration:VolumeExpedicao:ApiUrl` só loga o payload e confirma; 4xx (exceto 408/429) vai direto para a DLQ; outros erros são elegíveis a retry, que vem desligado por padrão (`QueueRetry.Enabled=false`); `OrigemSistema = "AWX_CHECKOUT"` (C-68).
- **Pedidos B2C** — lote: pedido duplicado conta como Enviado. Cancelamentos: 1 a 500 por lote, trim e dedupe, um evento `pedido-b2c.cancelado-externamente` por pedido com origem "Linx"; publish não confirmado volta "reenvie" (C-69).

## Onde são aplicadas

Nos serviços de `Application/<Contexto>` e nos clients `Linx*Client`. A API exige API key; ela não envia API key ao Estoque nem ao Recebimento (A-5).
