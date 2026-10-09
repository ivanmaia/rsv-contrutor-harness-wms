# PoC SP3: mapa estrutural, Serena e profundidade do índice (descartável)

Executado em 2026-10-05. Responde à seção 9.1 da spec `docs/superpowers/specs/2026-10-05-sp3-grafo-e-navegacao-design.md`. **Nada daqui é código do harness.**

Repos testados, como cópias em `repos/`:
- `industria-logistica.wms.servidor.backend`: legado .NET Framework, 4.209 `.cs`;
- `industria-logistica.wms.awx.monorepo`: .NET 10;
- `industria-logistica.wms.picking.frontend`: Angular.

## 1. Mapa estrutural: codebase-memory-mcp 0.11.0 × Graphify 0.9.77 (só AST)

| Critério | codebase-memory-mcp | Graphify |
|---|---|---|
| Indexa o legado | Sim, em 33 s. Problemas de parse só em `.sql`, `.cshtml` e `.css`; o C# passa | Sim, em 159 s |
| **L**: 30 chamadas método→método do legado, conferidas à mão (`eval/amostra_l.json`) | **29/30** (9,7) | **10/30** (3,3). Não resolve chamadas por campo injetado (`_repositorio.X()`) nem métodos de extensão |
| Precisão das arestas de chamada (amostra) | 13/13 | 20/20 |
| 10 perguntas de navegação (`eval/nav_cbm.txt`, `eval/nav_gfy/`) | 8/10. Errou as 2 do Angular (quem usa um service e quem chama um método dele) | ~9/10. 5 perguntas precisaram de nova consulta por ambiguidade; não devolve código (só a localização) |
| Saída para responder as 10 | ~8 KB (~2 mil tokens) | ~30 KB (~7,5 mil tokens), cerca de 3,6× mais |
| Atualização automática | Daemon com watcher. Só segue raízes git; os subtrees do workspace exigem `watch_non_git` ou indexar a raiz | Manual: `graphify update`, `watch` ou hook de git |
| Windows | **Não roda nativo nesta máquina.** Recusa o perfil porque o grupo `CodexSandboxUsers` (Codex CLI) tem escrita no `C:\Users\<user>` e em `C:\src` (issue aberta #2023; histórico de vários bugs de ACL no Windows). Roda no WSL (Ubuntu), inclusive sobre `/mnt/c` (awx em 55 s, contra 15 s no disco do WSL) | Nativo, sem problemas |
| **N**: rubrica de 4 itens, até 2,5 cada | busca 2,5 · trecho 2,5 · caminhos 2,5 · filtro por repo 2,5 = **10** | busca 1,0 · trecho 0,5 · caminhos 1,5 · filtro por repo 1,5 = **4,5** |
| Desempate 0,55·N + 0,45·L | **9,9** | **4,0** |

## 2. Serena 1.7.0 × edição padrão

Os testes usaram o Claude Code headless (`claude -p`, Sonnet), com uma cópia nova do repo a cada execução. A configuração é `run-task.sh`, as tarefas estão em `tasks.sh` e as saídas em `runs/`.

| Tarefa | Padrão: acerto / tokens / custo | Serena: acerto / tokens / custo | Ferramentas do Serena usadas |
|---|---|---|---|
| T1s: referências no legado | 7/7 · 102k · US$0,15 | 7/7 · 83k · US$0,07 | nenhuma (usou Grep). No piloto usou `find_referencing_symbols` |
| T2s: renomear no legado | ok · 71k · US$0,08 | ok · 128k · US$0,09 | `rename_symbol` |
| T1a: referências no .NET 10 | ok · 105k · US$0,12 | ok · 146k · US$0,14 | nenhuma |
| T2a: renomear no .NET 10 | ok · 142k · US$0,15 | ok · 185k · US$0,15 | `rename_symbol` |
| T3a: substituir corpo no .NET 10 | ok · 104k · US$0,12 | ok · 143k · US$0,13 | `find_symbol` + `replace_symbol_body` |
| T1f: usos no Angular | 4/4 · 89k · US$0,07 | 4/4 · 91k · US$0,07 | nenhuma |
| **Total** | 6/6 · ~613k · **US$0,67** | 6/6 · ~776k · **US$0,64** | |

**Achados do Serena:**
- **Mesmo acerto e mesmo custo.** Cerca de 25% mais tokens, quase todos de cache das definições das ferramentas. Nesta amostra não houve ganho mensurável.
- **Uso irregular.** O agente ignora o Serena nas buscas e usa Grep. Só usa nas edições.
- **Fim de linha.** O Serena **troca o fim de linha do arquivo inteiro de LF para CRLF** ao editar (`line_ending: native`), e o workspace usa `core.autocrlf=false`. Cada edição viraria um diff do arquivo inteiro. Dá para corrigir com `line_ending: lf` no `project.yml`.
- **Encoding.** O legado tem **48 `.cs` em cp1252** (não UTF-8). O health check do Serena falha no `FindReferencingSymbols` quando passa por eles (`UnicodeDecodeError`), porque o projeto aceita um único encoding.
- **Efeitos colaterais.** O Roslyn LS roda restore e gera `obj/` dentro do repo (ignorado pelo `.gitignore` do AWX). O `.serena/` também é criado dentro do repo e precisa estar ignorado em todos os repos, ou bloqueado no `ws push`.
- A edição padrão do Claude preservou bytes, BOM e LF em todos os casos.

## 3. Profundidade e ciclos do índice de impacto (`eval/profundidade.py`)

Os números saem do catálogo de produção (`dependencies.csv` dos 9 bancos) mais as arestas `db-*` e `job` do SP0, com o escopo de procs do SP0 aplicado.
- 5.246 objetos SQL têm dependentes.
- **Afetados por objeto:** mediana 3, p90 24, p99 205. O máximo é `Reserva.dbo.Produtos`, com 975.
- **Objetos com mais de 50 afetados:** 326. O limite de cerca de 50 por página está bem calibrado: cobre 90% sem resumo.
- **Profundidade da propagação forte:** mediana 1, p90 3, máximo 14.
- **Ciclos:** nenhum dentro do escopo. Fora dele há 2 ciclos de 2 nós no LINX. Ciclos HTTP entre serviços não foram medidos, porque dependem do casamento de endpoints do índice.

## O que foi instalado na máquina
- `poc/sp3-atlas/bin*`: binários do codebase-memory-mcp 0.11.0, com checksum conferido.
- WSL Ubuntu: `~/sp3`, com o binário, cópias dos 3 repos e o cache em `~/.cache/codebase-memory-mcp`.
- `uv tool`:
  - `graphifyy[sql]==0.9.77`. A instalação atualizou a skill global `~/.claude/skills/graphify` de 0.8.21 para 0.9.77 e guardou `SKILL.md.bak`.
  - `serena-agent==1.7.0`. Agora o `serena` está no PATH, então o MCP global `serena` do `~/.claude.json` passa a subir em todas as sessões.
- `~/.serena/serena_config.yml`: dashboard desligado. Cópia de antes em `dl/serena_config.yml.antes`.
