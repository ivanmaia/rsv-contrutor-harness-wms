# SP3: avaliação de ferramentas (proposta)

- **Status:** proposta, aguardando o usuário
- **Dono da decisão:** usuário (Ivan)
- **Data da evidência:** 2026-10-05, pesquisa web em fontes primárias (GitHub, PyPI, NuGet, docs oficiais); nada instalado nem executado
- **Confiança:** média. A direção é clara, mas três pontos só se resolvem com PoC (ver o fim do documento).

## Trabalho a resolver
- **Nível 1, entre repos:**
  - (a) "para a feature X, quais repos mudam e o que muda em cada um?";
  - (b) "se eu mudar a tabela, proc, view ou endpoint Z, quem é afetado?", de forma transitiva, atravessando código e SQL.
- **Atualização do nível 1:** híbrida (decisão do usuário, 2026-10-05). Um extrator determinístico roda a cada sincronização, e o agente atualiza a parte semântica no fim de cada feature. O resultado também serve de memória entre sessões.
- **Nível 2, dentro de cada repo:** navegar e editar código de forma semântica.

## Restrições
- **Código e ambiente:** o código fica local ou self-hosted, nada de SaaS. Tudo precisa rodar no Windows.
- **Licença:** preferência por OSS. Ferramenta comercial só se valer o preço.
- **Agente:** simplicidade e economia de tokens.
- **Stacks:** C# .NET Framework 4.x (csproj antigo), .NET 5–10, Angular, React Native, Next.js e SQL Server.

## O que já existe localmente
- SP0: `edges-consolidado.csv` (2.868 arestas, geradas por LLM) e `edges-sqlagent.csv` (1.117 arestas). O `tools/arch-map/build-map.py` gera o mapa em Markdown e HTML.
- Catálogo do SQL Server de homologação e produção (`extract/`), com os jobs.
- Máquina: VS 2022, Build Tools 2019, pacotes de referência do .NET Framework 3.5–4.8.1, SDKs do .NET 9 e 10, Node 20, Python 3.14, uv e Docker.
- Serena configurado no `~/.claude.json`, mas o executável `serena` não está no PATH; essa é a causa provável do "Connection closed".
- Graphify instalado como skill.

## Nível 1: extração das arestas

**Achado central: nenhuma ferramenta OSS pronta extrai as arestas entre serviços em C#.** Faltam rota ASP.NET ↔ cliente HTTP, SQL dentro do código, EXEC de proc e filas. A tabela mostra onde cada candidato para.

| Candidato | Versão | Disposição e motivo |
|---|---|---|
| Graphify | 0.9.76 (04/10/2026), Apache-2.0 | Fora como extrator. Faz AST estrutural dentro do repo. Não extrai rota ASP.NET, cliente HTTP nem SQL em string C#. Merge entre repos não gera aresta de chamada (issue #3152) |
| codebase-memory-mcp | ~0.11, MIT | Acompanhar. É o único que tenta casar HTTP entre repos, mas não extrai rotas de controller ASP.NET (#1041) e o casamento entre repos teve 37 falsos positivos em 40 (#1459) |
| GitNexus | 2026 | Descartado: licença PolyForm Noncommercial |
| CodeGraphContext, code-graph-rag | 0.5.1 / git, MIT | Sem HTTP nem SQL; nada além do Graphify |
| CodeQL | CLI 2.27.1 | Descartado pela licença: código privado e automação exigem GitHub Advanced Security pago |
| Sourcegraph + SCIP | Enterprise, ~US$16k/ano no mínimo | Caro. Dá navegação entre repos, não arestas HTTP/SQL |
| Sourcebot / Zoekt | 5.1.15 | É busca, não extração. Find references só na versão paga |
| Joern, Glean, Kythe | — | Suporte a C# fraco ou inexistente |
| NDepend, SciTools Understand | pagos | Dependências .NET, sem HTTP nem SQL |
| CAST Imaging | V3, a partir de ~US$10k/ano por aplicação | Único que cobre .NET + SQL Server + MQ + web services de ponta a ponta. Caro para 17 repos. Pode servir de gabarito num trial gratuito |
| **Opengrep** (fork LGPL do Semgrep) | 1.30.0 (07/09/2026) | **Finalista.** Regras YAML próprias para rotas, HttpClient, RestSharp, axios, fetch, SqlCommand, Dapper, `FromSqlRaw` e MQ. Propaga constantes dentro do arquivo. Tem binário Windows |
| ast-grep | 0.45.3, MIT | Alternativa mais simples ao Opengrep, mas sem propagação de constantes |
| **TransactSql.ScriptDom** | 180.117.0 (23/09/2026), MIT, Microsoft | **Finalista para SQL.** Parser oficial de T-SQL. Distingue leitura, escrita e EXEC em strings vindas do C#, em corpos de proc e view e em steps de job |
| sqlglot | 30.21.0, MIT | Plano B ao ScriptDom, se o pipeline for em Python |
| **Roslyn (sintático) + ts-morph** | 5.9.0 / 28.0.0, MIT | **Complemento** só onde as regras não bastam: prefixo `[Route]` + `[controller]`, base URL vinda de configuração, wrappers de HttpClient. Ficam no nível sintático, sem MSBuildWorkspace, para não depender do build do legado |
| Construir tudo do zero (base de comparação) | — | Perde: reescreveríamos à mão o parser de T-SQL e o casamento de padrões, que ScriptDom e Opengrep já entregam |

## Nível 1: armazenamento e consulta

| Candidato | Disposição e motivo |
|---|---|
| **CSV/JSONL canônico em git + CLI (Python)** | **Finalista.** Zero operação, diff legível em PR. Com 50 mil nós, `ancestors`/`descendants` responde em segundos. A CLI devolve só a resposta compacta |
| **SQLite como índice derivado** (fora do git, regenerado) | **Finalista, junto com o anterior.** `WITH RECURSIVE` dá o fecho transitivo e o FTS5 indexa as docs. Sem servidor |
| Neo4j Community + MCP oficial `neo4j/mcp` 1.6.0 | Adiado. Cypher completo, mas é um servidor JVM a mais (GPLv3) e o dump é binário |
| LadybugDB (fork do Kuzu; o Kuzu foi arquivado em 10/10/2025) | Adiado. Embarcado, MIT, muito ativo, mas fork com menos de um ano e API 0.x |
| DuckDB + DuckPGQ | Descartado. A própria doc o chama de projeto de pesquisa, e ele fica preso ao DuckDB 1.4.4 |
| FalkorDB, Memgraph, CozoDB | Descartados: SSPL, BSL e manutenção duvidosa, respectivamente |
| Graphiti, Cognee, mem0, Letta, MCP "memory" de referência | Descartados. São memória de chat extraída por LLM, não determinística. O MCP de referência não faz travessia |
| Backstage, Structurizr | Descartados como modelo. Custo alto (Backstage) ou só diagramas (Structurizr) |
| Docs: Markdown + índice + grep | Mantém. O time do Claude Code relata que a busca agêntica superou RAG. `qmd` (BM25 + vetor, local) só se aparecer falha por sinônimos |

## Nível 2: navegação e edição

| Candidato | Versão | Disposição e motivo |
|---|---|---|
| **LSP nativo do Claude Code + plugins `csharp-lsp` (csharp-ls) e `typescript-lsp`** | csharp-ls 0.28.0 (13/09/2026), MIT | **Finalista.** Sem MCP extra. Dá definição, referências, implementações, call hierarchy e símbolos, com diagnóstico automático após cada edição. O csharp-ls declara suporte a .NET Framework 4.8. Não faz rename nem edição por símbolo |
| **ast-grep** | 0.45.3, MIT | **Finalista como complemento.** Busca e reescrita estrutural sem build. Garante cobertura no legado |
| Serena | 1.7.0 (09/08/2026), GPL-3 | Condicional ao PoC. Fecha a lacuna de rename e edição por símbolo. Usa o Roslyn LS, sem promessa para .NET Framework. Tem atritos no Windows, e a própria doc admite que o Claude Code a usa pouco |
| SharpLensMcp | 1.6.3, MIT | Plano B só para C#. Usa MSBuildWorkspace e não documenta csproj antigo |
| cclsp, mcp-language-server | — | Só serviriam para rename. O segundo está pouco ativo |
| Evidência sobre tokens | — | O ganho do LSP aparece em referências e impacto. Em busca simples é nulo ou negativo (arXiv 2608.13568, benchmark de 936 execuções) |

## Recomendação (combinar)
1. **Extrator do nível 1, em três peças:**
   - Opengrep com regras próprias para C# e TS;
   - ScriptDom, que normaliza todo o SQL em `db.schema.objeto` com o tipo de acesso;
   - Roslyn sintático e ts-morph só para os casos difíceis.

   O catálogo do banco e os jobs continuam saindo do `sys.*`, com os steps passando pelo ScriptDom.
2. **Armazenamento:** arestas em CSV/JSONL canônico no git do workspace (`docs/sistemas/`). Um índice SQLite derivado, fora do git, é regenerado a cada sincronização. Uma CLI no `tools/ws` (por exemplo, `impacto` e `vizinhos`) é exposta ao agente por skill.
3. **Camada semântica:** os discoveries por repo em `docs/sistemas/<repo>/` mais um índice. O agente atualiza essa camada no hook `after_converge`, só nos repos que a feature tocou.
4. **Nível 2:** LSP nativo (csharp-lsp + typescript-lsp) e ast-grep. Serena entra só se o PoC mostrar ganho com rename e edição por símbolo.
5. **Graphify sai do caminho principal.** Não cobre as arestas que importam, e o LSP já cobre a navegação.

**Argumento mais forte contra:** a solução é feita por nós. Regras do Opengrep, normalizador ScriptDom e casamento de URL entre repos viram código nosso para manter. O CAST Imaging entregaria isso pronto, mas por dezenas de milhares de dólares ao ano.

**O que mudaria a decisão:**
- o codebase-memory-mcp passar a suportar controllers ASP.NET com casamento entre repos confiável;
- o PoC mostrar que as regras recuperam muito menos que as arestas do SP0;
- a empresa já ter licença de GHAS (CodeQL) ou de CAST.

## PoC proposto (descartável)
1. **Recall do extrator.** Rodar Opengrep + ScriptDom em 2–3 repos (servidor.backend, picking.backend, AWX) e comparar com as arestas do SP0 desses repos, que funcionam como gabarito.
   - Sucesso: recall ≥ 80% em http-in, http-out e db-*.
   - Tempo: 1 dia.
2. **LSP no legado.** Testar o csharp-ls no servidor.backend (.NET Framework) e num repo .NET moderno: referências, call hierarchy e diagnóstico.
   - Sucesso: o projeto carrega e as referências batem com o grep.
3. **Serena** (opcional): instalar o executável e repetir o item 2 com rename.

## Reavaliar quando
- Houver uma release do codebase-memory-mcp que feche a issue #1041.
- A Anthropic publicar o plugin oficial do Roslyn LS (issue #463 de `claude-plugins-official`).
- O Opengrep v2 trouxer análise entre arquivos.
- O índice SQLite deixar de bastar para as consultas.

## Fontes
- **Graphify:** https://pypi.org/project/graphifyy/ · https://github.com/Graphify-Labs/graphify/issues/3152
- **codebase-memory-mcp:** https://github.com/DeusData/codebase-memory-mcp/issues/1041 · https://github.com/DeusData/codebase-memory-mcp/issues/1459
- **CodeQL (licença):** https://github.com/github/codeql-cli-binaries/blob/main/LICENSE.md
- **Opengrep:** https://github.com/opengrep/opengrep/releases
- **ast-grep:** https://github.com/ast-grep/ast-grep
- **ScriptDom:** https://www.nuget.org/packages/Microsoft.SqlServer.TransactSql.ScriptDom
- **Roslyn:** https://github.com/dotnet/roslyn/issues/82931
- **CAST Imaging (preços):** https://www.castsoftware.com/imaging/pricing
- **Sourcegraph (preços):** https://sourcegraph.com/pricing
- **Kuzu e LadybugDB:** https://github.com/kuzudb/kuzu · https://github.com/LadybugDB/ladybug
- **DuckPGQ:** https://duckdb.org/community_extensions/extensions/duckpgq
- **Neo4j MCP:** https://github.com/neo4j/mcp/releases
- **MCP memory de referência:** https://github.com/modelcontextprotocol/servers/tree/main/src/memory
- **Code intelligence no Claude Code:** https://code.claude.com/docs/en/plugins/code-intelligence
- **csharp-ls:** https://github.com/razzmatazz/csharp-language-server
- **Serena:** https://github.com/oraios/serena · https://github.com/oraios/serena/issues/898
- **SharpLensMcp:** https://github.com/pzalutski-pixel/sharplens-mcp
- **Benchmarks de tokens:** https://arxiv.org/html/2608.13568v1 · https://dev.to/neko1313_4/how-much-does-context-cost-an-ai-coding-agent-grep-vs-graph-vs-lsp-measured-across-936-runs-33m8
