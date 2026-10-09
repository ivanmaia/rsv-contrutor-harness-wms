# Fluxo: da caixa do picking à NF e etiqueta

> **Last updated:** 2026-10-06
> **Scope:** Full Picking → Checkout → Faturamento → ERP Connector → Linx, e impressão (cross-area)
> **Mode:** code-only
> **Status:** code-derived, not validated by a person — see ../_discovery/assumptions-register.md

```mermaid
sequenceDiagram
  participant PB as Full Picking (picking.backend)
  participant CK as Checkout Worker/Api
  participant FT as Faturamento
  participant ERP as ERP Connector
  participant LX as Linx
  participant IMP as Impressão
  participant ACL as IntegracaoLegadoWMS
  participant WMS as API WMS legado
  PB->>CK: fila awx_checkout_solicitacao (Produtos[])
  Note over CK: grava solicitação, lê Itens[] e fica sem peças (A-1)
  opt armazém com pré-checkout
    CK->>FT: faturar.requested.v1 (NotaFiscalCommand)
  end
  CK->>CK: operador confere peças, fecha caixa(s)
  CK->>ACL: POST volumes-expedicao/gerar-identificador (X-API-KEY)
  ACL->>WMS: POST api/checkout/volume-expedicao/gerar-identificador
  CK->>CK: POST /api/checkout/salvar: volume (id do WMS), status AProcessar
  CK->>FT: faturar.requested.v1 (pós-checkout)
  FT->>ERP: POST faturamento/faturar (X-API-KEY)
  ERP->>LX: POST Faturamento
  FT->>ERP: GET obter-status (até 12 × 5 s)
  FT->>FT: grava faturamento, job reconcilia até Faturado ou NaoConfirmado (48 h)
  Note over FT,ERP: obter-status/{caixa}?pedido&emitidaAPartirDe; só confirma NF do pedido da caixa e autorizada
  CK->>FT: POST etiquetas/checkout (persistir)
  CK->>FT: GET documentos/{caixa}_CHECKOUT (dados de entrega)
  CK->>IMP: POST etiquetas/checkout?idImpressora (se informado)
  FT->>IMP: Mini DANFE só com NF autorizada
```

1. **Chegada.** O Full Picking publica a caixa pronta; o Checkout grava a solicitação. Hoje o nome da lista de peças difere entre os dois lados, e a solicitação chega vazia `[contradicted]` (C-9, A-1).
2. **Pré-checkout** (por armazém): a NF é pedida na chegada, sem esperar a conferência (C-13).
3. **Conferência.** Peça a peça, numa sessão por terminal; várias caixas por solicitação são permitidas por padrão (C-15).
4. **Salvar.** Pede o identificador do volume à ACL, que o obtém da API do WMS legado (antes o Checkout chamava essa API direto), cria o volume e, no pós-checkout, publica o pedido de NF (C-14, C-65). O operador agora é texto (até 64 caracteres), não número, no fechamento parcial e no atualizar caixa; o tipo de caixa deixa de ser exigido quando há sessão de conferência (C-70).
5. **Faturar.** O Faturamento é idempotente por solicitação, chama o Linx via ERP Connector (agora com API key) e reconcilia em segundo plano. Desde `e495e61`, consulta e reconciliação só aceitam a NF se ela for do pedido dos itens embalados, emitida a partir da véspera da embalagem e, na reconciliação, com StatusNfe 5; senão a caixa fica como não faturada e o motivo vai para `msg_erro` (C-21, C-22, C-66).
6. **Etiquetas.** Checkout persiste a etiqueta da caixa no Faturamento e, ao imprimir, relê a versão persistida para sair com dados de entrega (cai no mínimo se não achar). Os dados de entrega do Linx só são aceitos se forem do mesmo pedido. A reimpressão por bip agora imprime todos os volumes da solicitação, ou só o bipado, e reporta falha parcial. A Mini DANFE depende de NF autorizada. Em modo simulação da Impressão, o ZPL volta na resposta (C-23, C-69, C-71).
7. **Sem volta.** O Faturamento não avisa o Checkout do resultado; o Checkout consulta por HTTP quando precisa. No atualizar caixa, o prazo de cancelamento é checado em cada volume confirmado, não só no código de barras da solicitação (C-17, C-57, A-5).
8. **B2C (novo, fora deste fluxo).** `POST /api/v1/faturamento/b2c` repassa "embalar pedido e-commerce" ao Linx de forma síncrona, sem gravar nada no Faturamento. Quem chama não está no repo `[assumption]` (C-72, A-35).
