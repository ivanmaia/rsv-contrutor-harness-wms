# AWX Monorepo (`industria-logistica.wms.awx.monorepo`)

## O que é

Monorepo .NET 10 do AWX (Azzas Warehouse eXecution System), a plataforma de microsserviços que substitui aos poucos o WMS legado e se integra ao ERP Linx. Hoje contém 12 serviços de domínio (4 ainda são esqueletos), 3 integrações e o BFF do novo frontend Fly. O fluxo mais maduro vai da caixa pronta no picking à conferência no Checkout, à NF no Linx e à etiqueta. Também cobre produtos, pedidos B2C, parametrização B2B e recebimento de NF de entrada. Cada serviço tem o próprio PostgreSQL; só a ACL `AWX.IntegracaoLegadoWMS` fala com o banco do WMS legado, e só o `AWX.ERP.Connector` fala com o Linx.

## Documentação

**Coverage:** 13 áreas `full` (fontes, config e contratos lidos por sub-agentes; testes só amostrados), 3 `map only` (serviços scaffold, esteiras, specs/ferramentas de agente). Nada foi validado por pessoa (modo code-only).

| Área | Estado |
|---|---|
| checkout, faturamento, erp-connector, integracao-legado-wms, estoque, picking, pedidos-b2c, pedidos-b2b, recebimento, relatorios, impressao, fly-bff, base compartilhada | full |
| scaffolds (AgentOperacao, CrossDocking, Devolução, Expedição), esteiras, specs/.specify/.claude | map only |

| Doc | O que tem |
|---|---|
| [tech/current-architecture.md](./tech/current-architecture.md) | Subprojetos, mapa de contexto, padrões e surpresas, build e deploy |
| [tech/integrations.md](./tech/integrations.md) | Bancos e objetos, HTTP de entrada e saída, filas, jobs, quem mais toca o schema legado |
| [_discovery/edges.csv](./_discovery/edges.csv) | 267 arestas `app,tipo,alvo,detalhe,evidencia` |
| [domain/domain-model.md](./domain/domain-model.md) | Agregados por serviço e relações entre áreas |
| [domain/domain-glossary.md](./domain/domain-glossary.md) | Linguagem de negócio |
| [areas/checkout/rules-checkout.md](./areas/checkout/rules-checkout.md) | Ingestão, salvar, parcial, cancelamento, atualizar caixa |
| [areas/faturamento/rules-faturamento.md](./areas/faturamento/rules-faturamento.md) | Faturar, reconciliar, etiquetas |
| [areas/integracao-legado-wms/rules-integracao-legado-wms.md](./areas/integracao-legado-wms/rules-integracao-legado-wms.md) | NF de entrada, contagem, produtos, pedido B2C no legado |
| [areas/pedidos-b2b/rules-parametrizacao-por-cliente.md](./areas/pedidos-b2b/rules-parametrizacao-por-cliente.md) | Parametrização por cliente e importação CSV |
| [business/workflow-checkout-faturamento.md](./business/workflow-checkout-faturamento.md) | Da caixa do picking à NF e etiqueta |
| [business/workflow-pedido-b2c.md](./business/workflow-pedido-b2c.md) | Pedido B2C até o WMS legado |
| [business/workflow-recebimento-nf-entrada.md](./business/workflow-recebimento-nf-entrada.md) | NF de entrada e contagem |
| [business/workflow-sincronizacao-produtos.md](./business/workflow-sincronizacao-produtos.md) | Produtos e CUP entre Linx, Estoque e WMS |

## Como rodar

Do `CLAUDE.md` do repositório: `dotnet build AWX.slnx` e `dotnet test AWX.slnx`; os testes de integração exigem Docker (Testcontainers com PostgreSQL, MsSql e RabbitMQ). Chaves de configuração por serviço estão em cada `SECRETS.md` e em [integrations.md](./tech/integrations.md). O `README.md` do repositório está desatualizado (A-12).

## Riscos e dúvidas em aberto

- A fila `awx_checkout_solicitacao` recebe `Produtos` do Full Picking, mas o Checkout lê `Itens`: as solicitações entram sem peças (A-1).
- Credencial RabbitMQ versionada no Worker do ERP Connector: verificar e rotacionar (A-2).
- Contagem concluída na ACL: o INSERT dos itens contados omite colunas obrigatórias. A 1ª chamada falha e deixa a NF CONCLUIDA; a nova tentativa envia ao Linx, mas os itens contados nunca são gravados (A-4).
- Faturamento, PedidosB2B, o Worker do PedidosB2C e a própria ACL chamam serviços protegidos sem API key; seis serviços não têm autenticação (A-3, A-7).
- O Faturamento não devolve resultado ao Checkout, o que deixa inalcançável a retentativa após erro de NF (A-5).
- Lista completa: [_discovery/assumptions-register.md](./_discovery/assumptions-register.md).
