# SP6: pesquisa para a vertente de refactor (2026-10-15)

Pesquisa nos moldes da do SP5 (bugs): tabela A (Spec Kit), tabela B (externas) e contexto interno. Feita por subagentes, só leitura. Marcas: [código] lido no repositório, [validado] testado num venv descartável, [descrição] só README/catálogo, [M] número de marketing.

Os quatro tipos de refactor do time:
1. interno de um projeto num repo;
2. mover código entre projetos ou repos;
3. desacoplamento grande (LINX → AWX ERP Connector + Serviços Integração LINX WMS);
4. migração do legado para o AWX.

## Tabela A: Spec Kit (main `f6e72bc`, release 1.2.0 de 2026-10-13)

**Não há caminho oficial para refactor.** Nada de refactor, migração, brownfield ou strangler em `extensions/`, `workflows/`, `bundles/`, `presets/` nem nos catálogos oficiais [código]. A issue de tech debt #1158 e a de docs brownfield #1173 foram fechadas como not_planned. O guia `docs/guides/existing-projects.md` manda tratar modernização como "slice" de feature, com as compatibilidades escritas na descrição.

O fluxo de feature trava num refactor [código]:
- o `spec-template.md` exige User Scenarios, FR e Success Criteria "technology-agnostic";
- o `specify.md` manda evitar o COMO e para com `ERROR "Cannot determine user scenarios"`.

Novidades desde o SP5:
- trio oficial `assess` (extensão, workflow e bundle): triagem go / needs-clarification / kill antes do specify;
- **1.1.3, PR #4878: os comandos `speckit.bug.*` disparam hooks `before_`/`after_bug_*`.** É o gatilho do lembrete da seção 10 da spec do SP5;
- 1.2.0, #4942: bundles aceitam patch mais novo; deve resolver a falha de pin do bundle `bugfix` (inferido, não testado).

Comunidade (todos com mantenedor único e 0 a 72 estrelas):

| Componente | O que faz | Útil para |
|---|---|---|
| architecture-guard 2.3.6 | Violações de arquitetura em plan, tasks e código; gera tarefas de refactor; hooks opcionais [validado] | 1, 3 |
| improve 1.0.1 | Auditoria só leitura que gera prompts de spec priorizados, com "characterization tests first" [código] | 1 (backlog) |
| fx-to-dotnet 0.8.0 | .NET Fx → .NET em 7 fases; depende do MCP do Copilot Modernization; o preset falha no parser atual [validado] | 4 (parte) |
| aide-in-place 1.0.0 | Migração X→Y com equivalência de comportamento, sobre a extensão `aide` (parada) | 4 (referência) |
| brownfield, brownkit, time-machine | Engenharia reversa e baseline de specs; não executam refactor | baseline |
| golden-demo 0.5.0 | Oráculo de paridade; manifesto do HEAD inválido [validado] | referência |
| spec-kit-mainframe (fora do catálogo) | COBOL→Java com fidelidade de dados e golden master | padrão de referência |

Lacunas que nada cobre:
- template "behavior-preserving";
- strangler fig e ACL;
- mover código entre repos;
- WebForms e SQL Server para .NET 10;
- workflow de refactor com gate humano.

## Tabela B: externas

| Nome | O que faz | Tipos | Observação |
|---|---|---|---|
| `code-modernization` (marketplace oficial da Anthropic) | assess → regras extraídas → brief aprovado → transform → **verify de equivalência** (legado × novo, entradas inventadas, canary) | 3, 4 | Único com prova de equivalência. Assume reescrita lado a lado em `modernized/` |
| GitHub Copilot upgrade (ex-app modernization) | .NET Fx→.NET, SDK-style, WebForms→Blazor; valida só com build e testes existentes | 4 (mecânico) | Substituto do Upgrade Assistant (descontinuado). Sem WCF. Licença Copilot |
| AWS Transform for .NET | Porte .NET Fx→.NET 8/10 com WCF; CLI GA em 09/2026 | 4 | Cota grátis; código processado fora do Brasil |
| Kiro specs | feature e bugfix; a seção "unchanged behavior" do bugfix serve de modelo | formato | Não tem spec de refactor |
| superpowers | Não tem skill de refactor | — | |
| wshobson/agents, skills Mikado | Só prompts, sem verificação | 1, 2 | Referência |
| Serena, Roslyn MCP, ast-grep, `dotnet format` | Refactor mecânico determinístico | 1, 2 | Serena já em uso |
| Verify / ApprovalTests | Caracterização (golden master) | 1–4 | Verify cobra taxa comercial desde ago/set-2026 |
| Scientist.NET | Parallel run (antigo × novo) | 3, 4 | |
| ArchUnitNET / NetArchTest | Teste de fronteira ("só o conector toca o LINX") | 1–4 | O AWX já usa NetArchTest |
| YARP + System.Web adapters | Strangler oficial para ASP.NET Fx | 4 | |
| Pact (message pacts) | Contratos HTTP e de eventos | 3, 4 | |
| DACPAC (Microsoft.Build.Sql), tSQLt, catálogo + msdb | Dependências e regressão no banco | 3 | O catálogo não vê SQL dinâmico |

Descartados:
- Upgrade Assistant e try-convert, descontinuados;
- Moderne para C#, com receitas proprietárias;
- Devin e Sourcegraph, caros e úteis só em lote homogêneo.

Relatos (Airbnb, Google, Spotify): funcionou com unidade pequena, oráculo determinístico no loop, retry e humano revisando PRs pequenos. Nenhum relato trata de desacoplamento de banco.

## Contexto interno

- **O harness não tem caminho de refactor:** o `AGENTS.md` só conhece feature, bug e o fluxo manual. O preset `multirepo` faz `append` sobre o template core, que mantém as seções obrigatórias de comportamento.
- **O que já serve:**
  - regra II (consumidores pelo índice de impacto);
  - regra III (build e testes por repo);
  - regra VI (proíbe refactor fora do escopo, não o refactor que é o escopo);
  - o modelo preset + comandos `ws` do SP5.
- **Atlas:** adia a atualização de mudança só de código interno até 7 dias ou 30 arquivos.
- **LINX:**
  - AWX → ERP Connector (HTTP e RabbitMQ, sem banco) → servicos-linx-wms (HTTP; Dapper e procs direto no `Reserva`; polling de 5 min com tabelas `wmsSync`).
  - Acoplamentos que ficam: 181 sinônimos WMS→Reserva, 7 repos e o SQL Agent escrevendo em `Reserva.dbo`, `FATURAMENTO` com 1.332 afetados.
  - Sem ADR no repo; o `MIGRATION_PLAN.md` não existe.
- **AWX:**
  - constitution 1.3.0: legado só pela ACL, contratos com convivência, ADR aprovado, "Dívidas de Conformidade" a eliminar quando o serviço for tocado;
  - precedente: a migração da pREPA feita como feature (`specs/001-picking-b2c-consumer`).
- **Frequência:** commits rotulados como refactor são cerca de 3–4% no legado e 9% no Fly e no AWX. Mediana de 3 a 13 arquivos por commit, cauda de 100 a 220. Quase sempre num repo só.
