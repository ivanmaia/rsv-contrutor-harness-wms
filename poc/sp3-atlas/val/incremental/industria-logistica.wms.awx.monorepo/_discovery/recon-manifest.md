# Recon Manifest

> **Last updated:** 2026-10-06
> **Purpose:** Registra o que alimentou o recon para que execuções futuras detectem defasagem. NÃO é doc de onboarding; estado local de processo, recomenda-se git-ignore.

## Run info

- **Mode:** code-only
- **Target:** `C:\src\wms-workspace\repos\industria-logistica.wms.awx.monorepo` (subtree somente leitura no workspace; split `e495e61`)
- **Recon commit:** `e495e610ed21b42b712dace6a3a05433c73e8731`
- **Previous recon commit:** `af253448ff78e6d5b29b635eedc9638f12b4597a` (base do incremental)
- **Available inputs:** git para freshness: sim · sub-agentes: sim (7 agentes Explore genéricos em paralelo, com a regra de segredos e a de confiança coladas no prompt; os scouts do skill não estão instalados) · stakeholder: não
- **Exclusions in force:** `.gitignore` + `node_modules/`, `bin/`, `obj/`, `dist/`, `packages/`, `build/`, `coverage/`, gerados/minificados, snapshots/designers de migration, lockfiles
- **Navigation tiers used:** A (`AWX.slnx`, `*.csproj`, `Directory.Packages.props`, Dockerfiles, `esteiras/*.yml`) para o grafo de projetos: fato. C (grep e leitura por trecho, via sub-agentes) para rotas, SQL, filas, regras. Extra: catálogo do banco de homologação (`extract/db-hml/{WMS,Reserva}`) para sinônimos, dependências e colunas. B (dotnet), D (AST) e E (LSP) não usados.

## Existing docs read (Phase 0)

| Doc | Path | Last modified |
|---|---|---|
| README raiz | ./README.md | 2026-09-23 (data do clone; mtime não confiável) |
| CLAUDE.md (agent file do time; lido como evidência) | ./CLAUDE.md | idem |
| Constituição | ./.specify/memory/constitution.md | idem |
| Handoff | ./HANDOFF-etiquetas.md | idem |
| READMEs e SECRETS.md por módulo | `src/**/README.md`, `src/**/SECRETS.md`, `src/Integrations/AWX.IntegracaoLegadoWMS/db/README.md` | idem |
| Docs do Checkout | `src/Services/AWX.Checkout/docs/faturamento-pre-checkout-{funcional,tecnico}.md` | idem |
| Specs | `specs/001-picking-b2c-consumer/*`, `specs/002-sku-multiplo-codigo-barra/*` (plan, spec, tasks) | idem |
| Contexto externo | `docs/discovery/sources/contexto-usuario.md`, `repos-inventario.csv`, `icepanel-export.md` (só grep) | 2026-09-23 |

## Coverage ledger

| Area | Paths | Recon depth | Source tier | Interview | Docs written |
|---|---|---|---|---|---|
| checkout | `src/Services/AWX.Checkout` | full (fontes, config, migrations por nome, testes amostrados) | declared + text search | n/a (code-only) | areas/checkout/rules-checkout.md; workflow-checkout-faturamento |
| faturamento | `src/Services/AWX.Faturamento` | full | declared + text search | n/a | areas/faturamento/rules-faturamento.md |
| erp-connector | `src/Integrations/AWX.ERP.Connector` | full | declared + text search | n/a | tech/integrations.md; workflows |
| integracao-legado-wms | `src/Integrations/AWX.IntegracaoLegadoWMS` (+ `db/`) | full (todo o fonte, todos os scripts) | declared + text search + catálogo HML | n/a | areas/integracao-legado-wms/rules-integracao-legado-wms.md |
| estoque | `src/Services/AWX.Estoque` | full | declared + text search | n/a | workflow-sincronizacao-produtos |
| picking | `src/Services/AWX.Picking` | full | declared + text search | n/a | workflow-pedido-b2c |
| pedidos-b2c | `src/Services/AWX.PedidosB2C` | full (`MigrationExtensions.cs` não aberto) | declared + text search | n/a | workflow-pedido-b2c |
| pedidos-b2b | `src/Services/AWX.PedidosB2B` | full | declared + text search | n/a | areas/pedidos-b2b/rules-parametrizacao-por-cliente.md |
| recebimento | `src/Services/AWX.Recebimento` | full | declared + text search | n/a | workflow-recebimento-nf-entrada |
| relatorios | `src/Services/AWX.Relatorios` | full | declared + text search | n/a | tech/* |
| impressao | `src/Integrations/AWX.Impressao` | full | declared + text search | n/a | tech/*, glossary |
| fly-bff | `src/BFFs/AWX.Fly.BFF` | full | declared | n/a | tech/* |
| base compartilhada | `src/BuildingBlocks`, `src/Contracts` | full | declared + text search | n/a | tech/* |
| expedicao | `src/Services/AWX.Expedicao` | full (todo o código novo de `e495e61`: Api, Application, Core, Infra.Data, Infra.Bus, Worker, migration) | declared + text search | n/a | tech/*, workflow-pedido-b2c, domain-model |
| scaffolds | `src/Services/AWX.{AgentOperacao,CrossDocking,Devolucao}` | map only | declared | n/a | tech/current-architecture.md |
| esteiras | `esteiras/` (56 YAML) | map only (3 lidos: checkout-api-validation, checkout-api-release, fly-bff-release; demais por grep) | declared | n/a | tech/current-architecture.md |
| specs e ferramentas de agente | `specs/`, `.specify/`, `.claude/skills/` | map only (specs lidas por plan/spec/tasks; skills não lidas) | declared | n/a | register A-28 |

## Files actually read (Phase 1)

### Incremental 2026-10-06 (`af25344..e495e61`)

Lidos por `git diff` e `git show e495e61:<arquivo>` nesta sessão (sem sub-agentes): todo o diff não-teste de `src/BuildingBlocks/AWX.{EventBus.RabbitMQ,SharedKernel}`, `src/Contracts/**`, `src/Integrations/AWX.ERP.Connector/**` (Application, Core, Infra.Bus, Infra.Http, Api, Worker, appsettings), `src/Integrations/AWX.IntegracaoLegadoWMS/**` (endpoints, Application, Infra.Data, Program, appsettings), `src/Integrations/AWX.Impressao/**`, `src/Services/AWX.Checkout/src/**` (Api, Application, Core, Infra.Data, Worker), `src/Services/AWX.Faturamento/src/**` (Application, Domain, Infrastructure, Ui.WebApi, appsettings), `src/Services/AWX.Expedicao/src/**` (completo), `src/Services/AWX.PedidosB2B/src/AWX.PedidosB2B.Infra.Data/ExternalServices/*`. Testes, Dockerfiles, `.specify/*` e `openapi.json` só listados. Evidência externa: `docs/atlas/industria-logistica.wms.servidor.backend/edges.csv`, `docs/atlas/industria-logistica.wms.ecommerce.backend/edges.csv` (grep da rota `gerar-identificador`).

### Execução inicial (`af25344`)

Com git disponível, não há hash. Leitura por sub-agentes, por trecho; os marcados "principal" foram lidos diretamente nesta sessão para checagem.

| Path | Area |
|---|---|
| `README.md`, `CLAUDE.md`, `AWX.slnx`, `Directory.*.props`, `.specify/memory/constitution.md` (principal), `HANDOFF-etiquetas.md` (início) | estrutura |
| `src/Services/AWX.Checkout/**` (Program.cs, Endpoints, Application/Services, Core/Dtos, Validators, Infra.Data/Configurations, Infra.Bus, Worker, docs, testes amostrados); `Core/Dtos/SolicitacaoMessage.cs` (principal) | checkout |
| `src/Services/AWX.Faturamento/**` (Ui.WebApi, Ui.Consumer, Application/Services, Domain, Infrastructure, Migrations por nome, testes amostrados) | faturamento |
| `src/Integrations/AWX.ERP.Connector/**` (Api, Worker, Application, Infra.Bus, README, SECRETS.md; `Worker/appsettings.json` principal, só tamanho dos valores) | erp-connector |
| `src/Integrations/AWX.IntegracaoLegadoWMS/**` (todo o fonte, `db/*.sql`, README, SECRETS.md, testes); `WmsNotaFiscalRepository.cs:68-80` e `db/007_*.sql` (principal) | integracao-legado-wms |
| `src/Services/AWX.{Estoque,Picking,PedidosB2C,PedidosB2B,Recebimento,Relatorios}/**` | demais serviços |
| `src/Integrations/AWX.Impressao/**`, `src/BFFs/AWX.Fly.BFF/**`, `src/BuildingBlocks/**`, `src/Contracts/**` | integração, BFF, base |
| `src/Services/AWX.{AgentOperacao,CrossDocking,Devolucao,Expedicao}/**` (Program.cs, DI) | scaffolds |
| `esteiras/checkout-api-validation.yml`, `checkout-api-release.yml`, `fly-bff-release.yml`, `impressao-api-validation.yml`; grep em todas | esteiras |
| `specs/00{1,2}-*/{spec,plan,tasks}.md` | specs |
| `repos/industria-logistica.wms.picking.backend/src/Reserva.WMS.Picking.Domain/Entidades/ObjetosDeValor/AwxCheckout/SolicitacaoCheckoutObjetoValor.cs` (principal) | contrato da fila |
| `extract/db-hml/WMS/{objects,dependencies,synonyms,columns}.csv`, `WMS/modules/TR/Recebimento.tr_NOTAFISCAL_Insert.sql`, `Reserva/dependencies.csv` (grep) | banco (evidência externa) |

## Freshness check log

| Date checked | Compared against | Files changed | Docs affected | User's decision |
|---|---|---|---|---|
| — | — | primeira execução | — | — |
| 2026-10-06 | `af25344..e495e61` (plano do Atlas, `val-plano.json`, modo incremental) | 205 no plano (236 no diff, incluindo testes); áreas `.specify/*`, `.trivyignore`, `AWX.slnx`, `src/BFFs`, `src/BuildingBlocks`, `src/Contracts`, `src/Integrations`, `src/Services`. Ruído: `.specify/*`, `.trivyignore`, 26 Dockerfiles (troca de imagem base), `openapi.json`, `.csproj`/`.slnx` | edges.csv, tech/integrations.md, tech/current-architecture.md, business/workflow-{checkout-faturamento,pedido-b2c,recebimento-nf-entrada}.md, domain/domain-{glossary,model}.md, traceability-index.md, assumptions-register.md | incremental decidido pelo plano (sem pessoa) |
