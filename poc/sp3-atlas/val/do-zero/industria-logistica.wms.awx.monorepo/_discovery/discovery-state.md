# Discovery State

> **Last updated:** 2026-10-06
> **Purpose:** Memória de trabalho desta extração. NÃO é doc de onboarding; estado local, recomenda-se git-ignore.

## Run

- **Mode:** code-only
- **Options as resolved:** code-only · saída `docs/atlas/industria-logistica.wms.awx.monorepo/` · README do repo vira `project-readme.md` · sem CLAUDE.md/AGENTS.md · pular `business/user-personas.md` e `business-requirements.md` · exclusões padrão do Atlas · modo do-zero (docs anteriores ignorados como fonte) · consentimentos não concedidos (A-30)
- **Available inputs:** git (via plano do Atlas): sim · sub-agentes: sim · stakeholder: não
- **Output root (agreed with user):** `docs/atlas/industria-logistica.wms.awx.monorepo/` (definido pelo prompt do Atlas)
- **Docs-site tooling detected:** nenhum no workspace para esta pasta — nav/sidebar: n/a
- **Pre-existing files at target paths:** nenhum (pasta esvaziada de propósito); `_discovery/atlas.estado` não foi tocado

## Facts (accepted, unmarked)

Todos os fatos foram para os docs; nada pendente aqui.

## Unknowns / open questions

Ver `assumptions-register.md` (A-1 a A-30). Prioridade alta: A-2, A-3, A-4, A-18, A-9.

## Interview queue (top 5)

- **Progress:** 0 addressed · 30 open · code-only, sem entrevista

| # | Item | Impact | Confidence | Evidence | Why it matters |
|---|---|---|---|---|---|
| 1 | A-2 scripts do legado e dedup | H | H | `src/Integrations/AWX.IntegracaoLegadoWMS/db/README.md` | DBA aplica ordem errada |
| 2 | A-3 rota do Recebimento | H | H | `RecebimentoEndpoints.cs:17` | Recebimento quebra |
| 3 | A-18 cancelamento não cancela picking | H | H | edges.csv | Pedido cancelado é separado |
| 4 | A-4 status B2C sem API key | M | M | `PedidoB2CStatusAlteradoConsumer.cs:119` | Fila em loop |
| 5 | A-9 slnx incompleto | M | H | `AWX.slnx` | Build da raiz não cobre 3 projetos |

## Decisions

- Verificação (Fase 4) rodada por sub-agente isolado: 33 claims e 229 arestas conferidas; 2 claims errados (C-9, C-24), IDs ausentes nos workflows, 21 arestas faltando (migrations, retry/DLQ, um job) e uma rota com verbo errado, todos corrigidos numa rodada de ajuste. Veredito: go para uso como contexto do Atlas, com as pendências do register — context: code-only — validated by: ninguém
- Postgres nomeado `pg-<serviço>.<schema>.<tabela>` no edges.csv, seguindo a convenção do índice de impacto — context: nomes reais ausentes (A-6)
- `FATURAMENTO`/`FATURAMENTO_PROD` atribuídos a `Reserva.dbo` — context: query sem qualificação; índice de impacto já liga ao Reserva (A-7)

## Existing-doc claims (from Phase 0)

| Claim | Source doc | Status after recon |
|---|---|---|
| Services/ e BFFs/ são placeholders; só o ERP Connector é implantável | README.md | [outdated] (A-21) |
| 12 serviços em src/Services, Fly.BFF YARP, layout Core/Application/Infra.*/Api/Worker | CLAUDE.md | accepted (C-6) |
| Faturamento e Relatorios com layout Domain/Infrastructure/Ui.*; teste único em Checkout/Faturamento/Relatorios | CLAUDE.md | accepted (C-6) |
| Migrations aplicadas no boot fora de Development | CLAUDE.md | accepted, com exceção do Picking Worker (C-7) |
| `dotnet build AWX.slnx` constrói o repo | CLAUDE.md | [contradicted] (A-9) |
| Serviços de borda autenticam com API key; ErrorOr→HTTP no SharedKernel | constitution.md | accepted para borda (C-11); tradução ainda duplicada, como a própria constituição admite (C-12) |
| Filas `awx_checkout_*` alimentadas por produtor externo | constitution.md | accepted para `awx_checkout_solicitacao` (C-91); [unverified] para `awx_checkout_volume_expedicao` (A-11) |
| ACL somente leitura, 2 endpoints, POST em lote | AWX.IntegracaoLegadoWMS/README.md | [outdated] (A-1) |
| Ordem e lista de scripts; ACL não deduplica | db/README.md | [contradicted] (A-2) |
| Rota `/sincronizar`, códigos de erro, stateless, worker sem consumidores | AWX.Recebimento/README.md | rota [contradicted] (A-3); demais accepted (C-80, C-81) |
| Fila `checkout.resultado-faturamento`, eventos FaturarCaixa/Resultado | AWX.Checkout/README.md | [outdated] (A-22) |
| Rotas `{erp}`, 5 blocos, 4 ApiUrl obrigatórias | AWX.ERP.Connector/README.md | [outdated] (A-23) |
| Triangulação em lote | AWX.Relatorios/README.md, Contracts.Integration/README.md | [outdated] (A-24) |
| Bodies, Flurl, EtiquetaServico | AWX.Impressao/README.md | [outdated] (A-25) |
| Rotas e chave de etiqueta | HANDOFF-etiquetas.md | [outdated] (A-26) |
