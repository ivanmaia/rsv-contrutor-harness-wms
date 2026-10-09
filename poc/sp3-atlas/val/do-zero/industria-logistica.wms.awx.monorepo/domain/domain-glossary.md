# Glossário de domínio

> **Last updated:** 2026-10-06
> **Scope:** Linguagem de negócio usada no AWX (`industria-logistica.wms.awx.monorepo`, commit `e495e61`)
> **Mode:** code-only
> **Status:** code-derived, not validated by a person — see ../_discovery/assumptions-register.md

Significados tirados do que o código faz. Termos com definição `[unverified]` dependem de confirmação de negócio. A área é o nome usado em `areas/` e em [current-architecture.md](../tech/current-architecture.md).

| Termo | Área | Significado | Também chamado / nome no código | Relacionado |
|---|---|---|---|---|
| AWX | cross-cutting | Azzas Warehouse eXecution System: conjunto de microsserviços de execução de armazém que substitui aos poucos o WMS legado e se integra ao ERP Linx | — | WMS legado, ERP Linx |
| ACL | integracao-legado | Camada anticorrupção: o único caminho do AWX para o banco e a API do WMS legado | `AWX.IntegracaoLegadoWMS` | WMS legado |
| WMS legado | cross-cutting | Sistema de armazém anterior (banco SQL Server `WMS`, API WMS3) que o AWX substitui | `wms.erp-dinossauro.backend`, `WmsLegado*` | ACL |
| ERP Linx | cross-cutting | ERP da companhia. O AWX fala com ele só pelo conector | `Linx`, `LinxIntegration` | Conector ERP |
| Conector ERP | conector-erp | ACL entre o AWX e o Linx; também orquestra fluxos que cruzam serviços (fan-out CUP×Produto, recebimento) | `AWX.ERP.Connector` | ERP Linx |
| Solicitação | checkout | Pedido de checkout recebido por fila: identificador, pedido, cliente, caixa de origem e itens a conferir | `Solicitacao`, `SolicitacaoMessage` | Item da solicitação, Volume |
| CUP | cross-cutting | Código único da peça física (até 14 caracteres), ligado a um SKU; no Checkout é o código bipado do item | `Cup`, `CupId` | SKU, Produto |
| SKU | cross-cutting | Identificador do produto na grade (produto + cor + tamanho) | `Sku` | CUP, Produto |
| Clifor | cross-cutting | Código de cliente/fornecedor no Linx | `Clifor`, `CodigoCliente` | Parametrização por cliente |
| Sessão de conferência | checkout | Sessão de um terminal que confere os itens de uma solicitação; EmAndamento, Finalizada ou Abortada | `SessaoConferenciaCheckout` | Fechamento parcial |
| Volume | checkout | Caixa física montada no checkout; Rascunho antes de salvar, Confirmado depois | `Volume`, `VolumeStatus` | Identificador do volume |
| Identificador do volume | checkout | Sequencial do volume gerado pelo WMS legado via ACL | `Volume.Identificador`, `Sequencial` | Volume de expedição |
| Fechamento parcial | checkout | Modo em que uma solicitação vira várias caixas, fechadas uma a uma antes do salvar | `FecharCaixaParcial`, `realizar_fechamento_parcial_checkout` | Caixa única |
| Caixa única | checkout | Modo em que o salvar cria um único volume com todos os itens | — | Fechamento parcial |
| Pré-checkout / pós-checkout | checkout | Momento em que o faturamento é disparado: na chegada da solicitação ou no salvar do checkout | `realizar_faturamento_pre_checkout` | Faturamento |
| Parametrização (checkout) | checkout | Configuração por armazém dos modos de fechamento e faturamento | `Parametrizacao`, tabela `parametrizacoes` | — |
| Motivo de cancelamento | checkout | Motivo de cancelar um item: Qualidade, Perda da peça, Outros (exige descrição) | `MotivoCancelamento` | Cancelamento de item |
| Tipo de caixa | checkout, faturamento | Código de embalagem no catálogo do Linx (14 códigos de `001` a `NCS`) | `FaturamentoCaixaTipo`, `TipoCaixa` | Volume |
| Faturamento | faturamento | Pedido de emissão de NF para uma ou mais caixas, acompanhado até a NF autorizada | `Faturamento`, `StatusFaturamento` | Status de faturamento |
| Status de faturamento | checkout, faturamento | AProcessar, EmProcessamento, Criada, Faturado, ErroAoFaturar, NaoConfirmado (base 1, igual nos dois serviços) | `StatusFaturamento`, `StatusFaturamentoEnum` | Reconciliação |
| Reconciliação | faturamento | Verificação periódica no ERP que confirma a NF de cada faturamento pendente | `ReconciliarFaturamentoPendenteService` | Janela de confirmação |
| NF autorizada | faturamento | NF com `StatusNfe = 5`; condição para confirmar e imprimir mini-DANFE | `StatusNfe` | Mini-DANFE |
| Mini-DANFE B2B | faturamento, impressao | Etiqueta resumida da NF B2B, em ZPL | `MiniDanfeB2B` | Etiqueta de checkout |
| Etiqueta de checkout | checkout, faturamento, impressao | Etiqueta da caixa gerada no checkout, em ZPL | `CheckoutB2B`, `EtiquetaCheckout` | Documento |
| Documento | faturamento | Registro JSON de uma etiqueta, com chave `{CAIXA}_CHECKOUT` ou `{CAIXA}_MINIDANFE` | `Documento` | Reimpressão |
| Prazo de cancelamento | faturamento | Indica se a NF ainda pode ser cancelada; o checkout bloqueia atualização de caixa fora dele | `DentroDoPrazoCancelamento` | Atualizar caixa |
| Volume de expedição | conector-erp | Mensagem do checkout com o volume pronto, repassada ao Linx | `VolumeExpedicaoCheckoutMessage` | Expedição |
| Pedido B2C | pedidos-b2c | Pedido de e-commerce com número, seller, tipo, armazém e itens; Criado, Alterado ou Cancelado | `Pedido`, `PedidoStatus` | Picking e-commerce |
| Outbox | pedidos-b2c | Tabela que guarda eventos na transação do pedido até o dispatcher publicá-los | `OutboxEvento` | Pedido B2C |
| OnDemand | pedidos-b2c | Marca de item sob demanda (e se já passou por on demand) `[unverified]` | `OnDemand`, `JaFoiOnDemand` | Pedido B2C |
| Picking e-commerce | picking | Registro do pedido B2C no picking, com número de OR e de lote gerados por sequence | `PickingEcommerce` | Pedido B2C |
| OR / número de OR | picking, pedidos-b2b | Ordem de reserva `[unverified]` | `NumeroOR`, `TipoOrdemReserva` | Lote |
| Parametrização por cliente | pedidos-b2b | Regra por cliente e lote para geração de demanda (tipo de ordem, faixas mín./máx., validade) | `ParametrizacaoPorCliente` | Geração de demanda |
| Tipo de ordem de reserva | pedidos-b2b | Franquia ou Atacado | `TipoOrdemReserva` | Pedido franquia |
| Vigente / Vencido | pedidos-b2b | Situação calculada de uma parametrização pela data de validade | — | Parametrização por cliente |
| Geração de demanda | pedidos-b2b | Simulação de demanda B2B; hoje só valida a entrada | `GeracaoDemanda` | — |
| Produto | estoque, integracao-legado | Cadastro de SKU (código, cor, tamanho, grade, grife, grupo, NCM, código de barras) | `Produto` | SKU |
| Código de barras do SKU | estoque | Mapa código de barras → SKU, único por código | `CodigoBarraSku` | Produto |
| NF de entrada | recebimento, integracao-legado | Nota fiscal recebida no armazém, com origem e itens | `NotaFiscalEntrada`, `NotaFiscal` | Contagem |
| Origem da NF | recebimento | Fornecedor, Loja ou CrossDockingRepa | `OrigemNotaFiscal` | NF de entrada |
| Contagem | integracao-legado | Conferência física de uma NF de entrada (quantidade esperada vs contada) enviada ao ERP | `NotaFiscalContagem`, `StatusContagem` | Sobra/Falta |
| Sobra / Falta | integracao-legado, conector-erp | Divergências da contagem, que viram romaneios e pedidos no ERP | — | Romaneio |
| Romaneio | conector-erp | Documento devolvido pelo Linx em faturamento B2C, contagem e auditoria | `Romaneio`, `NumeroRomaneioPerda/Ganho` | Auditoria |
| Auditoria de movimentação | integracao-legado, conector-erp | Envio de perdas e ganhos de estoque ao ERP | `AuditoriaMovimentacao` | Romaneio |
| Triangulação fiscal | relatorios, integracao-legado | Fluxo de troca de NF entre armazém de origem, etapas intermediárias e loja destino; o AWX entrega a etapa Armazém Origem | `TriangulacaoFiscal` | — |
| NF de expedição | expedicao | NF registrada para expedição: Pendente, EmLote, Enviada, Cancelada (só Pendente é usada) | `NotaFiscalExpedicao` | — |
| ZPL | impressao | Linguagem das impressoras Zebra; formato das etiquetas | — | Etiqueta |
| Ship To | impressao | Modalidade de entrega em loja, impressa na etiqueta | — | Retire em loja |
| Fly | fly-bff | Frontend atendido pelo BFF `[unverified]` | `AWX.Fly.BFF` | — |
| DLQ | cross-cutting | Fila de mensagens que falharam (`{fila}-dlq`) | — | Retry |
