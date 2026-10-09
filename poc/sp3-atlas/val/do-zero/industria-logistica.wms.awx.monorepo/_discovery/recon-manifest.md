# Recon Manifest

> **Last updated:** 2026-10-06
> **Purpose:** Registra o que alimentou o recon para que execuções futuras detectem defasagem. NÃO é doc de onboarding; estado local de processo, recomenda-se git-ignore.

## Run info

- **Mode:** code-only
- **Target:** `repos/industria-logistica.wms.awx.monorepo` do workspace WMS (somente leitura; subtree do workspace)
- **Recon commit:** `e495e610ed21b42b712dace6a3a05433c73e8731` · **working tree:** o commit é o `split_atual` do plano do Atlas; a árvore lida é a do workspace na branch `sp3-val-awx`, sem alterações em `repos/industria-logistica.wms.awx.monorepo/`
- **Available inputs:** git para freshness: sim (via plano do Atlas) · sub-agentes: sim (sete scouts genéricos, um por grupo de áreas, só leitura) · stakeholder: não
- **Exclusions in force:** `.gitignore` do repo + `node_modules/`, `bin/`, `obj/`, `dist/`, `packages/`, `build/`, `coverage/`, `graphify-out/`, arquivos gerados ou minificados, migrations geradas (só `*ModelSnapshot` e migrations com SQL bruto consultados) e lockfiles
- **Navigation tiers used:** A (`AWX.slnx`, `*.slnx` por serviço, `Directory.*.props`, Dockerfiles, `esteiras/*.yml`) para o mapa estrutural: fato. C (grep/leitura por trecho, pelos scouts e pelo agente principal) para rotas, SQL, filas, regras e testes. Evidência extra: `docs/atlas/banco/WMS/` (objects, dependencies, synonyms), `docs/atlas/impacto/` e docs dos outros repos em `docs/atlas/`. B (dotnet), D (AST) e E (LSP) não usados.

## Existing docs read (Phase 0)

| Doc | Path | Last modified |
|---|---|---|
| README raiz | ./README.md | 2026-09-25 (mtime do checkout; não confiável) |
| CLAUDE.md | ./CLAUDE.md | 2026-09-29 (idem) |
| AGENTS.md | ./AGENTS.md | 2026-09-29 (idem) |
| Constituição | ./docs/constitution.md | v1.3.0, emendada 2026-09-24 |
| Handoff de etiquetas | ./HANDOFF-etiquetas.md | 2026-09-25 |
| READMEs de módulo | src/BFFs/README.md, src/Services/README.md, src/Contracts/AWX.Contracts.Integration/README.md, src/Integrations/{AWX.ERP.Connector,AWX.Impressao,AWX.IntegracaoLegadoWMS}/README.md, src/Integrations/AWX.IntegracaoLegadoWMS/db/README.md, src/Services/{AWX.Checkout,AWX.Recebimento,AWX.Relatorios}/README.md | 2026-09-25 |

## Coverage ledger

| Area | Paths | Recon depth | Source tier | Interview | Docs written |
|---|---|---|---|---|---|
| checkout | src/Services/AWX.Checkout/ | full | declared + text search | n/a (code-only) | areas/checkout/*, business/workflow-checkout-faturamento.md |
| faturamento | src/Services/AWX.Faturamento/ | full | declared + text search | n/a | areas/faturamento/*, business/workflow-checkout-faturamento.md |
| conector-erp | src/Integrations/AWX.ERP.Connector/ | full | declared + text search | n/a | areas/conector-erp/*, business/* |
| integracao-legado | src/Integrations/AWX.IntegracaoLegadoWMS/ (src, db, tests) | full | declared + text search + catálogo WMS | n/a | areas/integracao-legado/* |
| relatorios | src/Services/AWX.Relatorios/ | full | declared + text search | n/a | tech/integrations.md |
| estoque | src/Services/AWX.Estoque/ | full | declared + text search | n/a | areas/estoque/model-produto.md |
| recebimento | src/Services/AWX.Recebimento/ | full | declared + text search | n/a | areas/recebimento/*, business/workflow-recebimento-nf-entrada.md |
| pedidos-b2c | src/Services/AWX.PedidosB2C/ | full | declared + text search | n/a | areas/pedidos-b2c/*, business/workflow-pedido-b2c.md |
| picking | src/Services/AWX.Picking/ | full | declared + text search | n/a | areas/pedidos-b2c/* |
| pedidos-b2b | src/Services/AWX.PedidosB2B/ | full | declared + text search | n/a | areas/pedidos-b2b/* |
| expedicao | src/Services/AWX.Expedicao/ | full | declared + text search | n/a | areas/expedicao/* |
| impressao | src/Integrations/AWX.Impressao/ | full | declared + text search | n/a | areas/impressao/* |
| fly-bff | src/BFFs/AWX.Fly.BFF/ | full | declared (reverseproxy.json) | n/a | tech/* |
| building-blocks / contracts | src/BuildingBlocks/, src/Contracts/ | full | declared + text search | n/a | tech/current-architecture.md |
| esteiras | esteiras/ | full | declared | n/a | tech/current-architecture.md |
| agent-operacao, cross-docking, devolucao | src/Services/AWX.{AgentOperacao,CrossDocking,Devolucao}/ | map only — esqueletos sem regra | declared | n/a | tech/current-architecture.md |

## Files actually read (Phase 1)

Git disponível, então sem hash. Conjunto de alto sinal por área: `Program.cs` e `DependencyInjection*.cs` de cada host; `Endpoints/*.cs`; `Configurations/*Configuration.cs` e `*ModelSnapshot.cs`; repositórios e `Repositories/*.cs` com SQL; `Application/Services/*.cs` e `Validators/*.cs`; consumers, publishers e workers RabbitMQ; `ExternalServices`/`Http` clients; `appsettings*.json` (só nomes de chave); `SECRETS.md` (só títulos/nomes); testes em torno das regras citadas; `db/*.sql`; `reverseproxy.json`; um par de esteiras por padrão. As evidências exatas estão no [edges.csv](../edges.csv) e no [traceability-index.md](./traceability-index.md).

## Freshness check log

| Date checked | Compared against | Files changed | Docs affected | User's decision |
|---|---|---|---|---|
| 2026-10-06 | — (modo do-zero do Atlas) | — | todos recriados | mapeamento do zero, sem uso dos docs anteriores |
