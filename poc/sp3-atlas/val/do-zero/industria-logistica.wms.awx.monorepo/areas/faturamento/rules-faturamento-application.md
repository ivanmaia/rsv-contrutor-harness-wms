# Regras do faturamento (Awx.Faturamento.Application)

> **Last updated:** 2026-10-06
> **Scope:** Regras em `src/Services/AWX.Faturamento/src/Awx.Faturamento.Application/Services` e `Validators`; agrupamento pelo código, `[unverified]` como conceito de negócio
> **Mode:** code-only
> **Status:** code-derived, not validated by a person — see ../../_discovery/assumptions-register.md

## Regras

- **Validação da caixa** — caixa, embalador, tipo e armazém obrigatórios; tipo dentro do catálogo; data de embalagem presente e não futura; ao menos um item, cada um com pedido, código de barras, produto, cor e quantidade > 0. Pedido sem caixas é erro (C-53).
- **Idempotência por solicitação** — se já existe faturamento da mesma solicitação do checkout (header `x-entity-id`) com status Criada, EmProcessamento ou Faturado, não reenvia ao ERP. Sem o header, o id vira 0 e a idempotência fica compartilhada `[assumption]` (A-14) (C-54).
- **Envio e polling** — envia ao ERP (`POST api/faturamento/faturar`, sucesso só com 202) e consulta o status até 12 vezes a cada 5s enquanto vier "Em Processamento". Texto do ERP vira status: "Fatura Criada"→Criada, "Em Processamento"→EmProcessamento, "Erro ao Faturar"→ErroAoFaturar, outro→AProcessar. Falha do ERP grava ErroAoFaturar com id `ERRO-{caixa}` antes de relançar (C-54).
- **Reconciliação** — a cada `ReconciliacaoFaturamento:IntervaloSegundos` (60s) pega um lote de faturamentos AProcessar/EmProcessamento/Criada sem NF e com verificação vencida, faz claim e consulta o ERP por caixa. Confirma (Faturado, grava NF e filial) só se todas as caixas tiverem NF, o vínculo NF↔caixa for válido e a NF estiver autorizada (`StatusNfe = 5`). Passadas 48h da embalagem mais antiga, marca NaoConfirmado; senão reagenda com backoff `min(2·2^tentativas, 30)` minutos. ErroAoFaturar nunca é reselecionado (C-55).
- **Vínculo NF↔caixa** — os pedidos da NF têm de estar entre os pedidos da caixa, e a emissão tem de ser ≥ data de embalagem − 1 dia (folga de fuso) (C-56).
- **Prazo de cancelamento** — no faturamento confirmado, `dentro_do_prazo_cancelamento` só fica verdadeiro se todas as caixas estiverem no prazo (C-55).
- **Mini-DANFE automática** — ao confirmar, a etiqueta mini-DANFE é materializada só com NF autorizada e sem duplicar; dados da proc do ERP prevalecem; chave de NF com no máximo 44 caracteres; falha não bloqueia (C-57).
- **Reimpressão** — a caixa bipada precisa bater com a etiqueta; bloqueia se `StatusNfe ≠ 5`, mas deixa passar etiquetas antigas sem status (C-58).
- **Consulta persistida** — `GET /api/v1/faturamento/status` aceita exatamente um filtro (`caixa`, `cup`, `numeroPedido`); sem faturamento devolve 404. O filtro `cup` compara com `id_faturamento`, não com o CUP do item (A-15) (C-59).
- **B2C síncrono** — `POST /api/v1/faturamento/b2c` exige pedido e origem e repassa ao ERP (`faturar-b2c`) (C-53).

## Onde são aplicadas

`ProcessarFaturamentoService` (consumer e `POST /api/v1/faturamento`), `ReconciliarFaturamentoPendenteService` (worker), `VinculoNotaFiscalCaixa`, `PersistirEtiquetasService`, `ReimpressaoEtiquetaMiniDanfeService`, `ConsultarStatusFaturamentoPersistidoService`. A API não autentica (A-8). O serviço não publica evento de resultado: o Checkout consulta o status por HTTP (C-50).
