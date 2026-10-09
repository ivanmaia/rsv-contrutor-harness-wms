# AWX: Azzas Warehouse eXecution System (`industria-logistica.wms.awx.monorepo`)

## O que é

Monorepo .NET 10 com os microsserviços de execução de armazém que substituem aos poucos o WMS legado e se integram ao ERP Linx. Hoje cobre o checkout de caixas e o faturamento até a NF autorizada, os pedidos B2C até o picking e o legado, o recebimento de NF de entrada, o cadastro de produto/CUP, a parametrização B2B por cliente, a impressão de etiquetas ZPL e a triangulação fiscal. São 28 deployáveis (APIs e Workers em GKE); cada serviço de domínio tem seu PostgreSQL. O banco e a API do WMS legado são acessados só pela ACL `AWX.IntegracaoLegadoWMS`, e o Linx só pelo `AWX.ERP.Connector`.

## Documentação

**Coverage:** `full` em 15 áreas (código, contratos, regras e testes amostrados) e `map only` nos três esqueletos. Nada foi validado por pessoa (modo code-only).

| Doc | O que tem |
|---|---|
| [tech/current-architecture.md](./tech/current-architecture.md) | Componentes, layout, persistência, aspectos transversais e riscos |
| [tech/integrations.md](./tech/integrations.md) | Bancos (R/W/X), HTTP de entrada e saída, filas, jobs e quem mais toca os objetos |
| [edges.csv](./edges.csv) | 250 arestas com `caminho:linha` |
| [domain/domain-model.md](./domain/domain-model.md) | Agregados, área dona de cada um e cópias de dados entre serviços |
| [domain/domain-glossary.md](./domain/domain-glossary.md) | Linguagem de negócio |
| [business/workflow-checkout-faturamento.md](./business/workflow-checkout-faturamento.md) | Da solicitação de checkout à NF autorizada |
| [business/workflow-pedido-b2c.md](./business/workflow-pedido-b2c.md) | Pedido B2C até o picking e o legado |
| [business/workflow-recebimento-nf-entrada.md](./business/workflow-recebimento-nf-entrada.md) | NF de entrada do Linx ao legado e contagem |
| [business/workflow-sincronizacao-produtos.md](./business/workflow-sincronizacao-produtos.md) | Fan-out de produtos e CUP |

### Áreas

| Área | O que cobre | Coverage |
|---|---|---|
| [areas/checkout/](./areas/checkout/) | Conferência, caixas e disparo do faturamento (`AWX.Checkout`) | full |
| [areas/faturamento/](./areas/faturamento/) | Faturamento, reconciliação de NF e etiquetas (`AWX.Faturamento`) | full |
| [areas/conector-erp/](./areas/conector-erp/) | Ponte com o Linx e orquestração entre serviços (`AWX.ERP.Connector`) | full |
| [areas/integracao-legado/](./areas/integracao-legado/) | ACL do banco e da API do WMS legado (`AWX.IntegracaoLegadoWMS`) | full |
| [areas/estoque/](./areas/estoque/) | Produto, CUP e código de barras (`AWX.Estoque`) | full |
| [areas/recebimento/](./areas/recebimento/) | Validação e repasse de NF de entrada (`AWX.Recebimento`) | full |
| [areas/pedidos-b2c/](./areas/pedidos-b2c/) | Pedido B2C, outbox e picking (`AWX.PedidosB2C`, `AWX.Picking`) | full |
| [areas/pedidos-b2b/](./areas/pedidos-b2b/) | Parametrização por cliente e geração de demanda (`AWX.PedidosB2B`) | full |
| [areas/expedicao/](./areas/expedicao/) | NF de expedição (`AWX.Expedicao`) | full |
| [areas/impressao/](./areas/impressao/) | Montagem de ZPL e envio à impressora (`AWX.Impressao`) | full |
| relatorios | Proxy da triangulação fiscal (`AWX.Relatorios`); descrito em integrations e na ACL | full |
| fly-bff | Reverse proxy YARP (`AWX.Fly.BFF`); descrito em integrations | full |
| building-blocks / contracts | SharedKernel, EventBus.RabbitMQ, ArchitectureTests, Contracts; descrito em current-architecture | full |
| picking | Consumer do pedido B2C (`AWX.Picking`); documentado junto de pedidos-b2c | full |
| esteiras | 28 pares de pipeline; descrito em current-architecture | full |
| agent-operacao, cross-docking, devolucao | Esqueletos (só `/health`, sem tabelas) | map only |

## Como rodar

Pelo `CLAUDE.md` do repo: `dotnet build AWX.slnx`, `dotnet test AWX.slnx` (testes de integração exigem Docker para Testcontainers) e `dotnet format AWX.slnx --verify-no-changes`. Picking, Relatorios e IntegracaoLegadoWMS ficam fora do `AWX.slnx` e se constroem pelos `.slnx` próprios. O build do Docker usa a raiz do repo como contexto. Chaves de configuração em [integrations.md](./tech/integrations.md) e nos `SECRETS.md` de cada serviço.

## Riscos e dúvidas em aberto

- A ACL grava no banco do legado, mas o README dela diz "somente leitura"; o db/README lista scripts que não existem e proíbe a deduplicação que o código faz (A-1, A-2).
- A rota do Recebimento (`importar`) não bate com README e contrato (`sincronizar`), e o conector chama a URL base sem sufixo (A-3).
- O Worker do PedidosB2C chama a ACL sem API key, e o consumer volta a mensagem à fila sem DLQ (A-4).
- Oito APIs não têm autenticação (A-8). `AWX.slnx` não inclui três projetos (A-9).
- Eventos sem par: NF de expedição sem publicador, cancelamento externo B2C sem consumidor; cancelar o pedido não cancela o picking (A-10, A-18).

Lista completa: [_discovery/assumptions-register.md](./_discovery/assumptions-register.md).
