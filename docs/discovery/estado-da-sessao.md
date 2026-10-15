# Estado do discovery (handoff entre sessões)

Atualizado em 2026-09-24. **Leia este arquivo primeiro ao retomar.**

## Objetivo
Esta pasta serve para **discovery, análise de alternativas e decisão** (ADRs e PoCs descartáveis) sobre um harness de desenvolvimento assistido por IA no ecossistema WMS. **Não** é aqui que o harness será implementado. Premissas: SDD com Spec Kit, ferramentas de grafo (Graphify), simplicidade e eficiência de tokens.

Subprojetos:
- **SP0** Descoberta da arquitetura ✔ concluído em 2026-09-23
- **SP1** Estrutura do Workspace ✔ concluído em 2026-09-25
- **SP2** SDD / Spec Kit multi-repo
- **SP3** Harness: grafo de arquitetura (HTTP, mensageria, banco) e navegação/edição semântica de código (Serena etc.)

Processo: skill `superpowers:brainstorming`, caminho **arquitetural** (spec escrita → aprovação → writing-plans). Nenhuma spec foi escrita ainda.

## Decisões tomadas
| Decisão | Valor |
|---|---|
| Escopo do SP0 | 16 repos do inventário mais o Fly (`integracoes.core.plataforma.backoffice.frontend`). Excluídos: deflator-estoque, erp-dinossauro, ondemand.gestao-producao.*, servicos-linx-wms.monorepo, Logistica.Integrada.BFF, Helix |
| Clones | `repos/`, somente leitura, blobless. `core.longpaths=true` em ecommerce.frontend, servidor.backend e Fly |
| Banco | Definições extraídas da **homologação** `10.11.0.5` (linha 2 de `docs/credentials/DatabaseReadOnly.txt`), só SELECT em `sys.*`, ApplicationIntent=ReadOnly. HML ≠ prod é aceito. Réplica de prod `10.1.1.3` é READ_ONLY, mas sem VIEW DEFINITION |
| Jobs do SQL Agent | Adiados (msdb negado nos dois servidores) |
| Discovery por repo | Skill `/codebase-discovery`, modo **code-only** (entrevista consolidada depois), saída **fora dos repos** em `docs/discovery/repos/<repo>/`, sem CLAUDE.md/AGENTS.md |

## Artefatos
- `docs/discovery/sources/`: inventário CSV, contexto validado pelo usuário, export do IcePanel
- `docs/discovery/db-acesso-sondagem.md`: acessos, volumetria, acoplamento via sinônimos
- `tools/db-extract/extract-catalog.ps1` → `extract/db-hml/{WMS,Reserva,ReservaNet}/`
- `docs/discovery/repos/industria-logistica.wms.picking.backend/`: **piloto concluído** (custo real: cerca de 313 mil tokens, 115 chamadas de ferramenta, 21 min)

## Execução concluída (2026-09-23)
Os 16 repos + retrofit do piloto rodaram com o prompt v2 (`docs/discovery/prompt-discovery-por-repo.md`), 4 agentes em fluxo contínuo. Custo ≈ 4,7 M tokens de subagentes (120–410 mil por repo).
- `docs/discovery/repos/<repo>/`: 17 discoveries code-only, todos com `_discovery/edges.csv`.
- `docs/discovery/edges-consolidado.csv`: 2.868 arestas (coluna extra `repo`); SFTP normalizado para `other-out`. Tipos: http-in 876, http-out 749, db-read 687, db-write 339, db-exec 147, job 32, mq-pub 22, mq-sub 8, other-out 8.
- `docs/discovery/segredos-para-rotacao.md`: locais de segredos versionados (sem valores). Grep nos docs gerados não achou valor de credencial.
- Lacuna conhecida: `GET/PUT /api/Configuracoes` do WMS3 faltam no edges.csv do servidor.backend.

## SP0 — fechamento (2026-09-23)
- Mapa cross-repo: `docs/discovery/arquitetura/mapa-arquitetura.md` (gerado por `tools/arch-map/build-map.py` a partir do `edges-consolidado.csv`; CSVs de apoio na mesma pasta).
- Núcleo: `wms.servidor.backend` (14 vizinhos) e `wms.ecommerce.backend` (10). Acoplamento do legado é sobretudo por banco (6 repos escrevem em `Reserva.dbo`); a plataforma nova (AWX, hub, trakta) liga-se ao legado por filas e pela ACL no banco WMS.
- Fora de escopo: corrigir bugs/segurança/segredos (achados só registrados).

## SP1 — Estrutura do Workspace (concluído em 2026-09-25)
Fatos do SP0 relevantes: 17 repos independentes no Azure DevOps (ARECO), todos em `main`, `.git` de 1 a 39 MB; stacks .NET Framework/.NET 5–10, Angular, React Native, Next.js; pipelines por repo (`esteiras/`). Arquivos de agente já existentes: awx.monorepo (`CLAUDE.md`, `.claude/`, `.specify/`, `specs/`), Fly (`CLAUDE.md`, `.claude/`), servidor.backend (`AGENTS.md`, `.github/`). Windows exige `core.longpaths` em 3 repos.
Decisões do usuário: repos continuam independentes; **git subtree `--squash`**; branch no workspace e `subtree push` no fim; sincronia por script antes de cada branch; push por script e PR manual; layout plano `repos/<nome-completo>/`; harness só no workspace, e nos repos só `docs/convencoes.md` e `docs/adr/`. A constitution e o CLAUDE.md/AGENTS.md raiz explicitam essa regra.
- ADR: `docs/adr/0001-workspace-git-subtree.md` (**aceita em 2026-09-24**). PoC descartável: `poc/sp1-subtree/`.
- Plano de implementação: `docs/superpowers/plans/2026-09-24-sp1-workspace-multi-repo.md`. O usuário aprovou o plano, o repo `industria-logistica.wms.workspace` e a pasta `C:\src\wms-workspace`, com execução native.
- **Tasks 1 a 7 concluídas** em `C:\src\wms-workspace`, branch `feat/sp1-ws-tools`, ainda não mergeada no `main`. Suíte: 48 testes ok.
  - A revisão final achou 1 Critical e 2 Important, todos corrigidos. Ver o adendo 2 da ADR: o rejoin real não é usado.
  - 10 minors adiados, registrados no ledger `C:\src\wms-workspace\.superpowers\sdd\2026-09-24-sp1-workspace-multi-repo\progress.md`.
  - **Task 8 concluída em 2026-09-25**, exceto o Step 7. O workspace está publicado em `industria-logistica.wms.workspace` (`main` `6f7005b04`) e a branch foi mergeada no `main` local antes.
  - Medidas e achados em `docs/discovery/sp1-bootstrap.md`: `ws add` em 189 s; `ws start` em cerca de 3 min; o `.git` local cresce de 65 MB para 253 MB no primeiro `ws start`.
  - Step 7 executado: o `ws push` real a partir de um clone novo funcionou, e a branch de teste foi apagada.
  - **SP1 concluído em 2026-09-25.** As decisões da execução estão em `sp1-bootstrap.md`.
  - Achados do bootstrap e os 10 minors do `tools/ws` **resolvidos em 2026-09-25**. O fetch raso deixou o `ws start` em cerca de 15–35 s e o `.git` em cerca de 65 MB. Ver o adendo 3 da ADR e `sp1-bootstrap.md`. O smoke test de push a partir de um clone raso não foi repetido, porque o usuário não pediu.
  - Próximo: **SP2** (Spec Kit multi-repo, constitution, migração dos arquivos de agente).

## SP2 — Spec Kit multi-repo (em andamento)
- Design aprovado em conversa em 2026-09-28. Spec escrita: `docs/superpowers/specs/2026-09-28-sp2-speckit-multirepo-design.md` (**aprovada em 2026-09-29**; marcador de tarefa `[workspace]`). PoC: `poc/sp2-speckit/README.md`.
- Decisões:
  - Claude Code como principal e `AGENTS.md` como fonte única.
  - Specs em `specs/NNN-*` na raiz, numa sequência única, com living spec por feature.
  - Constitution curta.
  - Discovery em `docs/sistemas/`.
  - Transição: os repos mantêm as instruções deles, subordinadas ao harness; o AWX perde só `.specify/`, `speckit-*` e `specs/`.
  - Spec Kit 1.0.12 com a extensão local `ws` (hooks `before_specify` e `after_converge`) e o preset local `multirepo`.
  - Adendo 4 à ADR 0001: a guarda do `ws push` passa a bloquear só `.specify/`, `specs/` e `speckit-*`.
- Plano: `docs/superpowers/plans/2026-09-29-sp2-speckit-multirepo.md`. **Executado (native) até a Task 9, aguardando a decisão de publicação.**
  - **Branch:** `sp2-speckit` no workspace local, em `27ff727`, ainda não publicada. Suíte: 109 testes offline e 6 de rede, todos ok.
  - **AWX:** branch `sp2-speckit` enviada (migração do Spec Kit para a raiz). O PR é aberto à mão. O usuário pretende refazer tudo do zero depois.
  - **Validação de ponta a ponta:** `docs/discovery/sp2-validacao.md`, com todos os itens ok depois de duas rodadas de correção (commit-push, sem atribuição do Claude, revisão de feature não mergeada, branch sem spec, "feat NNN", português, não propor mudança no harness).
  - **Pontos menores adiados e decisões:** no ledger `C:\src\wms-workspace\.superpowers\sdd\2026-09-29-sp2-speckit-multirepo\progress.md`.
  - **Ambientes descartáveis a apagar pelo usuário:** `C:\src\wms-workspace-e2e`, `C:\src\wms-e2e-origin.git`, `C:\src\wms-workspace-e2e2` e `C:\src\wms-e2e2-origin.git`.
- Desvio registrado no adendo da seção 4 da ADR: marcador de split próprio para os prefixos sem mudança local.
- Ferramentas de memória e indexação (Graphify, Serena etc.) ainda **não foram avaliadas**; isso fica para o SP3. Ponto de partida para o grafo de arquitetura: `edges-consolidado.csv` e `tools/arch-map/`.

## Produção extraída via autenticação integrada (2026-09-24)
- Terminal `runas /netonly` com o usuário de domínio + `claude --continue`; `sqlcmd -E` / `Invoke-Sqlcmd` sem credencial. Réplica `10.1.1.3` (SRV-ALW01, AG `RSV_AG`, outro nó SRV-BD). Tem `VIEW ANY DEFINITION` + `db_datareader`; falta `VIEW SERVER STATE`.
- Extraídos: catálogo de 9 bancos em `extract/db-prod/` e 494 jobs em `extract/db-prod/_jobs/`. Diff HML × prod em `extract/diff-hml-prod/`. Resultados em `docs/discovery/db-acesso-sondagem.md` (seção "Produção").
- Achados: ACL do AWX sobre o WMS (`pedido`, `Produtos`, `Recebimento.NotaFiscal*`) existe só em HML; 22 objetos citados pelos repos não existem em prod; 44 jobs do Agent tocam WMS/ReservaNet e ainda não estão no mapa.
- DBA **negou** `VIEW SERVER STATE` e `msdb` na primária (2026-09-24). Alternativas listadas em `db-acesso-sondagem.md` ("Uso real sem VIEW SERVER STATE").
- `Hub_Produtividade`: só tabelas, segundo o usuário; sem acesso. Banco `pd` não existe.
- **Escopo do banco (usuário, 2026-09-24):** ONDEMAND fora **exceto objetos do banco WMS** (correção do usuário); procs do WMS/ReservaNet ficam; de outros bancos só se alcançam (dependências de produção) objeto do WMS ou ReservaNet, ou se os repos as chamam diretamente, ou se uma proc do WMS as chama diretamente (regras confirmadas pelo usuário). Reserva: 208 de 3.801 procs; jobs 401 → 114 (os 12 jobs SSIS/CmdExec/PowerShell descartados pelo usuário). Só chamadas diretas (sem cadeia); os 12 jobs que entram só por chamar as procs de e-mail ficam. `tools/db-extract/scope.py` → `arquitetura/procs-escopo.csv`; aplicado em `jobs-edges.py` e `build-map.py`. Seção "Escopo do banco" no `mapa-arquitetura.md`.
- **Jobs no mapa (2026-09-24):** `tools/db-extract/jobs-edges.py` → `docs/discovery/edges-sqlagent.csv` (1.117 arestas após o escopo, nó `sqlagent`) + `arquitetura/jobs-sqlagent.csv`; `build-map.py` lê os dois CSVs. Seção "Jobs do SQL Agent" no `mapa-arquitetura.md`: 14 jobs escrevem em tabelas do WMS usadas pelos repos (REPA → picking; `RSV_EXPORTA_NOTA_FISCAL_WMS3` → NF/caixa). 12 jobs SSIS/CmdExec/PowerShell não analisados.
- **Visão de uso real abandonada** (decisão do usuário, 2026-09-24): o DBA não vai rodar `tools/db-extract/dba-uso-primaria.sql`. Mapa de banco fica só com catálogo e definições de jobs; **premissa: todo objeto existente em produção é considerado em uso** (decisão do usuário, 2026-09-24). Alternativas sem DBA (snapshots de `sys.partitions`, `MAX()` de datas) continuam possíveis se for retomado.

## Acesso ao banco de produção (2026-09-24, pedido original ao DBA)
- Pedido pronto em `docs/discovery/pedido-dba-permissoes.md`: 1 login novo, read-only, na primária do AlwaysOn e na réplica `10.1.1.3`. Servidor: só `VIEW SERVER STATE`. Por banco (WMS, Reserva, ReservaNet, WMSTASKS, WMS_Produtividade, pd, Audit, Ecommerce, LinxFranquia, Reserva_Integracao_Anymarket): `db_datareader` + `VIEW DEFINITION` + `VIEW DATABASE STATE`. msdb: `SQLAgentReaderRole` + `db_datareader`. SSISDB: `ssis_logreader`, se houver SSIS.
- Quando chegar: extrair o catálogo de produção (`tools/db-extract/extract-catalog.ps1` com a nova linha de credencial), os jobs do msdb, as DMVs de execução e o Query Store, e comparar com a homologação.
- Objetos criptografados (homologação): 54, todos no `Reserva` (`extract/db-hml/encrypted.csv`, gerado por `tools/db-extract/list-encrypted.ps1`). São o LINX (NF-e/SEFAZ, LGPD, DDL, perfis) e o grupo `SS_` (volumetria WMS, TMS/CT-e). Nenhum dos 17 repos chega a eles; só procs internas do LINX.

## Como retomar
Atualizado em 2026-10-05.

1. **SP2 encerrado em 2026-10-05.** Decisão de publicação (Task 9): **não publicar agora**, porque o usuário vai refazer tudo do zero. A branch `sp2-speckit` fica só local em `C:\src\wms-workspace` (`27ff727`); a do AWX segue enviada, sem PR. Pontos menores e decisões estão em `docs/discovery/sp2-validacao.md`.
   - Limpeza **a cargo do usuário** (o modo automático bloqueou a remoção): a pasta do ledger `C:\src\wms-workspace\.superpowers\sdd\2026-09-29-sp2-speckit-multirepo\` e os ambientes `C:\src\wms-workspace-e2e`, `C:\src\wms-e2e-origin.git`, `C:\src\wms-workspace-e2e2` e `C:\src\wms-e2e2-origin.git`.
2. **Banco:** se o acesso do DBA tiver chegado, fazer a extração de produção descrita acima.
3. **SP3 em andamento** (brainstorming iniciado em 2026-10-05, caminho arquitetural). Fatos levantados: o Serena está configurado no `~/.claude.json` (`serena start-mcp-server --context=claude-code --project-from-cwd`), mas não conectou na sessão de 2026-10-05; a skill `graphify` está instalada em `~/.claude/skills/graphify`, sem nenhum `graphify-out/` gerado ainda; o workspace já tem `docs/sistemas/` com os CSVs de arestas, o `mapa-arquitetura.md` e o `grafo.html`; repos de 98 KB a 105 MB.
   - Requisitos do usuário (2026-10-05):
     - **nível 1** entre repos: quais repos mudam numa feature e o que muda em cada um, e o impacto de mudar tabela, proc, view ou endpoint;
     - **nível 2**: navegação e edição de código dentro de cada repo;
     - tudo atualizado, servindo de memória entre sessões.

     Atualização **híbrida** (extrator determinístico + agente no `after_converge`).
   - Avaliação de ferramentas (proposta, aguardando o usuário): `docs/discovery/sp3-avaliacao-ferramentas.md`. Recomendação:
     - nível 1: Opengrep + ScriptDom + Roslyn/ts-morph sintáticos, com CSV/JSONL em git, índice SQLite e CLI;
     - nível 2: LSP nativo (csharp-lsp + typescript-lsp) + ast-grep, e Serena só se o PoC passar;
     - Graphify fora do caminho principal.
   - **Decisões do usuário após a avaliação (2026-10-05):**
     - **Descartados:** CAST Imaging e manter código próprio de extração (Opengrep, ScriptDom etc.).
     - **Nível 1:** a skill `codebase-discovery` em modo incremental, pela freshness check por commit do `recon-manifest.md`, integrada ao workflow.
     - **Nível 2:**
       - codebase-memory-mcp como coadjuvante, onde suportar a linguagem e o framework;
       - Serena testado como ferramenta de edição no lugar das ferramentas padrão;
       - docs da `codebase-discovery` como memória onde o codebase-memory-mcp não suportar.
     - **Atualização:** independente de quem mudou o código, porque a detecção é por commit.
     - **Quando atualizar:** no `ws start` (o agendamento fica para depois, se necessário) **e** no `after_converge` (o usuário quer os dois). Também a qualquer momento, por comando manual, de forma **completa e sem limite de repos**.
     - **Verificação no `ws start`, esperta:**
       - detecção por commit, sem custo;
       - filtro de relevância (exclusões, testes, assets, lockfiles, docs, pipelines) → só avança o SHA;
       - roda agora se tocar áreas de contrato (rotas, clientes HTTP, SQL e repositórios, filas, config de URL e conexão) ou se o repo for provável na feature;
       - o resto acumula até o intervalo mínimo (ex.: 7 dias) ou um volume de arquivos;
       - limite por execução = **max(3, nº de repos afetados pela feature)**; o restante fica pendente, com aviso ao consultar.
     - **Commits das atualizações:** numa **branch só de docs, com PR próprio** (o `main` do `industria-logistica.wms.workspace` exige PR).
     - **Estado:** `docs/sistemas/<repo>/_discovery/recon-manifest.md`, versionado (importar e mapear o SHA de origem para o subtree).
     - "Não manter código" = não manter **extratores**. Lógica no `tools/ws` e no `build-map.py` é aceitável.
     - **Branch de docs:** fixa, `sistemas/atualizacao`, com um PR aberto que acumula commits. O `ws start` faz merge dela na branch da feature (opção 1). Suposição apresentada: o `after_converge` faz commit na própria branch da feature (o usuário não contestou).
     - **Consulta do nível 1:** o `build-map.py` gera um índice de impacto pré-calculado, uma página por objeto (0 token para gerar; ~200–2 mil tokens por consulta).
       - **Propagação forte**, até o fim e sem limite: definição SQL (tabela → view/proc → job/código), endpoint → clientes, fila → pub/sub.
       - **Propagação fraca** (atravessar um app): mostrada, não expandida; o agente decide.
       - Distância e caminho mais curto por item; resumo por repo acima de ~50 itens.
       - Ciclos: conjunto de visitados + SCC, seção "Ciclos" na página e `ciclos.csv`.
       - Primeiro passo do plano: medir a profundidade real e os ciclos para calibrar o limite.
     - **Nível 2, ferramentas por repo:** um registro no workspace diz, para cada repo, se a edição usa Serena ou a padrão + ast-grep, e se o codebase-memory-mcp cobre o repo ou se a memória fica só com os docs da discovery. O PoC preenche a lista inicial, e um repo muda de grupo quando um teste novo passa.
     - **Validação do nível 1 (opção 1):**
       - incremental × completa em 1 repo com drift desde o SP0 (ex.: AWX), ~300–500 mil tokens uma vez;
       - 3–5 features reais cross-repo (PRs do Azure DevOps) como gabarito, propostas por mim e corrigidas pelo usuário;
       - os mesmos casos viram regressão.
     - **Design apresentado:**
       - Seção 1, visão geral: aprovada. Inclui a opção `--do-zero` no comando manual.
       - Seção 2, execução e falhas: aprovada.
         - O `ws` só calcula e aplica (`ws sistemas plano` / `ws sistemas concluir`); a discovery é rodada pelo agente da sessão, com subagentes.
         - Manual = skill `/sistemas-atualizar [--do-zero]`.
         - Branch fixa `sistemas/atualizacao` mantida para `ws start` e manual; o `after_converge` faz commit na branch da feature.
     - **Nível 2, revisado:**
       - Os docs da discovery não têm granularidade de nível 2. A ponte nível 1 → código é o `traceability-index.md`, que será importado.
       - Navegação ao vivo: Serena.
       - Mapa estrutural gravado: **uma ferramenta só para todos os repos**, escolhida no PoC entre codebase-memory-mcp e Graphify só AST. Critérios: funcionar no legado, eficácia em perguntas de navegação, tokens por resposta, auto-atualização e estabilidade no Windows.
       - **Desempate (usuário):** se o codebase-memory-mcp não for bem melhor, vence o Graphify por suportar T-SQL. A outra ferramenta só entra onde a vencedora falhar.
       - Suporte a T-SQL **verificado no código** (2026-10-05): empate. As duas usam a gramática genérica DerekStride; nenhuma extrai EXEC, escrita, GO ou SQL em string C#. O Graphify deixa as procs `AS BEGIN…END` só como nó, sem arestas. O desempate por T-SQL caiu; proc ↔ tabela vem do catálogo do banco (nível 1).
       - **Novo desempate (usuário):** nota = 0,55 × N + 0,45 × L.
         - **N** = ferramental de navegação para agentes, nota 0–10 por rubrica: busca de código, trecho de símbolo, caminhos de chamada, filtro por repo.
         - **L** = cobertura no legado (servidor.backend), 0–10 pela % de uma amostra de símbolos e chamadas encontrados.
   - **Nomes (usuário, 2026-10-05):**
     - **Atlas** é o conhecimento mantido: `docs/atlas/`, `ws atlas`, `/atlas-atualizar`, `/atlas-consultar`, branch `atlas/atualizacao`;
     - **mapeamento** é o processo; "discovery" fica para features;
     - a skill `codebase-discovery` mantém o nome;
     - as renomeações do SP2 (`docs/sistemas/`, `tools/sistemas/`, `importa-discovery.sh`) entram no SP3 (seção 6.8 da spec), e a spec do SP2 ganhou um adendo.
   - **Spec do SP3 revisada e aprovada pelo usuário, com os nomes novos aplicados.**
   - **PoC 9.1 executado em 2026-10-05:** resultados em `poc/sp3-atlas/README.md`.
     - **Mapa estrutural:** o codebase-memory-mcp vence. L 29/30 contra 10/30; desempate 9,9 contra 4,0; cerca de 3,6× menos tokens. Mas não roda nativo nesta máquina (ACL do CodexSandboxUsers, issue #2023), só no WSL, e errou os usos no Angular.
     - **Serena:** mesmo acerto e mesmo custo que a edição padrão. Problemas: converte LF→CRLF (corrigível), 48 `.cs` cp1252 no legado quebram as referências, gera `obj/` e `.serena/` dentro dos repos.
     - **Índice:** mediana de 3 afetados por objeto, p90 24, máximo 975; 326 objetos com mais de 50; profundidade p90 3, máximo 14; nenhum ciclo no escopo.
   - **Decisões do usuário após o PoC (2026-10-05):**
     - codebase-memory-mcp **no WSL**;
     - **Graphify AST nos 4 frontends**;
     - **Serena não adotado**: edição padrão + ast-grep.

     A spec foi atualizada (seções 1, 2, 3, 6.7, 7, 9.1, 10, 11). Próximo: writing-plans.
   - **Plano escrito em 2026-10-05:** `docs/superpowers/plans/2026-10-05-sp3-atlas.md`, com 8 tasks.
     - O código foi validado numa cópia descartável do `tools/` no scratchpad da sessão.
     - A spec ganhou a linha "Refinamentos do plano": `atlas.estado`, `relevancia.ini`, pendência no `project-readme.md` e hook `speckit.ws.converge`.
     - **Executado em modo nativo (2026-10-06)** no workspace, branch `sp3-atlas` (saiu de `sp2-speckit` `27ff727`; **não publicada**).
       - Tasks 1 a 7 concluídas; revisão final (opus) com 2 Critical e 4 Important corrigidos; suíte 168 ok. Minors M7 a M14 adiados no ledger `.superpowers/sdd/2026-10-05-sp3-atlas/progress.md`.
       - Task 8, Steps 1 a 4: dados importados (`60cdfed`), cbm no WSL com 13 repos indexados, Graphify nos frontends, MCPs funcionando.
       - Task 8, Step 5 (incremental contra do-zero no AWX): arestas com recall de 93%; docs sem `areas/` no incremental. Decisão: **aprofundar onde mexe** + filtro de ruído + notação fixa (commit `80842f2`). Detalhes em `docs/discovery/sp3-validacao.md`.
       - Task 8, Step 6 (features reais, 5 work items): repos do workspace 9/10, fora 1/3. Correção do índice (procs fora do escopo + `db-def`), commit `19e27027d`. O PAT do Azure DevOps fica guardado no `az devops login` (revogar com `az devops logout`).
       - Task 8, Step 7 (ponta a ponta em `C:\src\wms-workspace-e2e3`): os 5 itens ok. Achados corrigidos em `742a92eb`, `d15392f5` e `95e5cf73` (`.serena/`, nome do projeto no cbm, mensagem do commit do Atlas). Suíte 173 ok. Achado em aberto: a estimativa de custo do plano ficou cerca de 7 vezes abaixo do real.
       - **Recalibração da estimativa de custo** (`1e75f463`): mínimo por repo de 200 mil tokens e do-zero de 450 mil.
       - **SP3 concluído em 2026-10-06.**
         - **Publicação (Step 8):** não publicar agora. A `sp3-atlas` fica local, sobre a `sp2-speckit` (`27ff727`), também local. As duas devem ser publicadas juntas mais tarde.
         - **Ledger:** arquivado em `docs/discovery/sp3-ledger-execucao.md`; o workspace SDD do plano foi apagado.
         - **Minors M7 a M14:** resolvidos depois do fechamento (commit `f2310280d`, suíte 180 ok).
       - **Adendo ao SP2 (2026-10-07): AWX mantém o Spec Kit e a constitution, subordinados ao workspace.** Spec `docs/superpowers/specs/2026-10-07-sp2-adendo-harness-awx-subordinado-design.md`, plano `docs/superpowers/plans/2026-10-07-sp2-adendo-awx-subordinado.md`.
         - Commits `24ff8fdd`, `b7ad5477`, `09ff7f75` e `e3a12018` na `sp3-atlas`, mais `16bfbb00` com os minors; a branch termina em `16bfbb00`.
         - O AWX voltou a ser idêntico ao repo dele. As features do workspace passam a ser `ws-NNN`, e a subordinação fica no `AGENTS.md`, na constitution 1.1.0, no plan e no adendo 5 da ADR 0001.
         - Validação de ponta a ponta 5/5 ok (`docs/discovery/sp2-validacao.md`). Revisão final com 2 Important e 2 Minor regraduados, todos corrigidos. Os dois minors também foram resolvidos (ledger `docs/discovery/sp2-adendo-awx-ledger.md`).
       - **Ambientes descartáveis a apagar pelo usuário:** `C:\src\wms-workspace-e2e3`, `C:\src\wms-e2e3-origin.git`, `C:\src\wms-e2e3-tms.git`, `C:\src\wms-e2e3-tms-finished.git`, `C:\src\wms-workspace-e2e4`, `C:\src\wms-e2e4-origin.git` e `C:\src\wms-e2e4-awx.git`.
       - **Índice de impacto enxuto (2026-10-07):** só ganha página o objeto que chega a um repo ou job; trigger em tabela gravada diretamente liga ao gravador (opção B). 5.604 → 2.156 páginas. Adendo na seção 6.5 da spec do SP3. Mudança em `tools/atlas/impacto.py` + testes (suíte 191 ok) na branch `atlas/impacto-so-tocados` (saiu do `origin/main` `ff5412af8`; commits `f5b2a9c46` código e `ac13471bf` páginas), enviada ao origin e **integrada no `main`** (2026-10-08).
       - **Publicado em 2026-10-07:** branch `sp3-atlas` (contém a `sp2-speckit`) enviada ao origin do workspace no Azure DevOps. Nenhum repo em `repos/` difere do upstream, então não há `ws push`. **Integrado no `main` pelo PR 16927 (`ff5412af8`).**
   - (Histórico) Seções 3 e 4 aprovadas; spec revisada; PoC (9.1) feito.
   - (Histórico) Seção 3 precisava ser reapresentada com o nível 2 revisado; depois a seção 4 (validação e PoC) → spec.
   - (Histórico) Apresentar o design por seções (arquitetura, gatilhos, agente, nível 2, validação) → spec.
   - (Resolvido) Pergunta pendente, a retomar depois da avaliação: o conjunto de referência para validar o nível 1. Proposta: as arestas do SP0 como gabarito de recall, mais 5 features reais e cerca de 10 objetos críticos.
5. **SP4: documentação em camadas do harness** (brainstorming em 2026-10-08, caminho arquitetural). Design aprovado em conversa; spec escrita em `docs/superpowers/specs/2026-10-08-sp4-documentacao-harness-design.md`, **aprovada pelo usuário em 2026-10-08**. Plano escrito: `docs/superpowers/plans/2026-10-08-sp4-documentacao-harness.md` (8 tasks; verificador validado numa cópia descartável no scratchpad), executado em 2026-10-08 (modo Native) na branch `harness/docs-camadas` do workspace (9 commits a partir de `868b5f0a5`, último `63cf87818`; suíte 212 ok, 0 falha). Revisão final feita (5 correções com teste, 5 menores adiados); branch enviada ao origin. **Mergeado no `main` pelo PR 16940 (`0cbac04e5`) em 2026-10-08.** Piloto preparado em `docs/discovery/sp4-piloto.md` (roteiro e registro; depende de um dev novo), e o subprojeto da apresentação: spec `docs/superpowers/specs/2026-10-08-sp4-apresentacao-harness-design.md`, plano `docs/superpowers/plans/2026-10-08-sp4-apresentacao-harness.md`, **deck publicado em https://claude.ai/artifact/GJjEDbZtoBLRLthKn4KxxC** (24 slides, 39 min de notas, com 3 slides de comandos; fontes em `docs/discovery/sp4-apresentacao/`, revisão final feita). **Apresentação feita ao time; o dev piloto foi escolhido nela** e vai rodar o fluxo completo numa demanda real e depois dar o feedback. Próximo: acompanhar o piloto e registrar em `docs/discovery/sp4-piloto.md`; cada linha com ação vira PR de acompanhamento no workspace. **Primeiro relato recebido em 2026-10-13** (sessão de 2026-10-09, ciclo parcial: só o passo 1, travado pelo repo do Linx fora do workspace). Os 8 itens foram tratados na branch `harness/piloto-sp4-ajustes` (7 commits a partir de `6df2664fe`, último `7048be2a5`, suíte 247 ok); o usuário decidiu mergear logo, antes de o dev retomar, e manter a política de contrato do Atlas no start. Detalhes e pendências no `sp4-piloto.md`. Em 2026-10-14 o item 2 foi refeito na mesma branch: o agente não pergunta a pasta ao dev, oferece seguir com o sistema como externo ou parar e pedir a inclusão, e a feature parada é sincronizada com o `main` em vez de refeita. A branch, com o Atlas do repo do Linx mapeado nela, foi mergeada no `main` do workspace pelo PR 17070 (`34dcabb7c`) em 2026-10-14; o dev pode retomar sincronizando a feature com o `main`. **Segundo relato (2026-10-14):** o `ws push` caiu no HTTP/2 do Azure DevOps ao enviar o `servidor.backend` (item 9 do `sp4-piloto.md`); correção mergeada no `main` do workspace pelo PR 17072 (merge `6af58e659`; `ws push` com HTTP/1.1 e buffer de 500 MB, camada 2 atualizada, suíte 249 ok). **Conferência do Atlas do Linx (2026-10-14):** a incorporação da `atlas/atualizacao` atrasada apagava o Atlas do Linx no início da feature; correção mergeada pelo PR 17073 (merge `dbc94c3dc`; detalhes no `sp4-piloto.md`).
6. **SP5: vertente de bugs e incidentes** (brainstorming de 2026-10-09 a 2026-10-11, caminho arquitetural).
   - Spec escrita: `docs/superpowers/specs/2026-10-11-sp5-bugs-design.md`, **aprovada em 2026-10-11** e revista no mesmo dia (sem bundle e sem hooks; ver abaixo).
   - Decisões:
     - extensão `bug` e workflow `bugfix` oficiais, instalados separadamente: o bundle falha no 1.0.12 e no 1.0.13 (pin 1.0.1 contra 1.0.0 publicado);
     - preset `bugs` com `prepend` que leva os relatórios para `bugs/<slug>/`;
     - slug `<work item>-<desc>` ou `inc-<AAAAMMDD>-<desc>`;
     - branch `hotfix/<slug>`;
     - três comandos mecânicos na `ws` (`bug-start`, `bug-sem-correcao`, `bug-enviar`), chamados pelo preset (`prepend`/`append`), porque a extensão `bug` publicada (1.0.0) não tem hooks;
     - **LEMBRETE do usuário:** revisar quando o Spec Kit lançar a extensão `bug` 1.0.1 (hooks nativos e bundle). Seção 10 da spec;
     - regra II da constitution valendo para bug (seção Impacto);
     - SELECT opcional só com acesso próprio do dev;
     - validação ponta a ponta descartável.
   - A tabela B (skills externas de debug) e a rota para o `/speckit-specify` ficaram fora. A documentação das features existentes como specs fica para depois.
   - Entrega: branch `harness/bugs`. A regra de mergear só depois do piloto do SP4 foi **derrubada pelo usuário em 2026-10-12**, porque o piloto pode demorar.
   - **Executado em 2026-10-11 (modo Native)** pelo plano `docs/superpowers/plans/2026-10-11-sp5-bugs.md` (7 tasks), na branch `harness/bugs` do workspace, saindo do `main` `333500954`. São 9 commits; o último é `5ffb5a630`.
     - Suíte offline com 239 ok e 0 falha; testes de instalação com rede com 9 ok.
     - O executor decidiu pôr no `.gitignore` o cache dos catálogos e a trava da instalação de workflows do Spec Kit.
     - A revisão final (subagente) achou 2 problemas importantes, e 2 menores subiram de grau. Os 4 foram corrigidos com teste: o slug pela branch no fix e no test, a guarda do registro, a ordem das checagens do `bug-start` e a entrada "sobrescrever" na camada 2. Outros 6 menores ficaram adiados e foram **corrigidos em 2026-10-12** (`2b0235287` e a reinstalação `cb64780b7`): mensagem com `git switch` para a branch do bug só local, `bug-sem-correcao` sem origin, comentário da regra do slug, testes de slug com acento e de árvore suja numa feature, espaços no `speckit.sh` e "contando o que ainda não foi commitado" no `bug-enviar`.
     - Validação com LLM em `docs/discovery/sp5-bugs-validacao.md`: os itens 1 a 4 do PoC e os 4 casos de ponta a ponta deram ok, por cerca de US$ 12. A correção do slug pela branch veio depois e não foi revalidada com LLM.
     - Suíte offline com 243 ok em `cb64780b7`. Push da `harness/bugs` feito pelo usuário (a permissão automática negou o push pelo agente). **Mergeado no `main` do workspace pelo PR 17012 (`6df2664fe`) em 2026-10-13.** O `main` local do workspace foi atualizado e a branch local `harness/bugs` apagada.
     - Ambientes descartáveis para o usuário apagar: `C:\src\wms-workspace-e2e5`, `C:\src\wms-e2e5-origin.git`, `C:\src\wms-e2e5-tms.git`, `C:\src\wms-e2e5-*` (JSON, logs, script) e os projetos de PoC em `%TEMP%` (`sp5-poc`, `sp5-poc13`, `sk-bug`).
7. **Sincronização pela branch `ws/sync`** (brainstorming em 2026-10-15, caminho arquitetural; sem número de SP, entra como adendo 6 do ADR 0001).
   - Origem: um `/speckit-bug-assess` falhou porque o `ws start` faz push direto no `main`, e o `main` ganhou em 2026-10-13 e 2026-10-14 duas políticas de revisão bloqueantes (criadas pelo usuário). A mensagem culpava outro dev e mandava um `git pull` que não resolve.
   - Decisões: nada chega ao `main` sem PR, nem a sincronização (contra dar bypass aos devs); a sincronização vai para uma branch compartilhada `ws/sync`, enviada sem PR e só com fast-forward, com PR próprio para o `main` (contra levar a sincronização em cada branch de feature, que gera conflitos e linhas paralelas de squash); `WS_BASE=ws/sync` e `WS_DESTINO=main`.
   - Spec escrita: `docs/superpowers/specs/2026-10-15-ws-sync-design.md`, **aprovada pelo usuário em 2026-10-15**. Ao escrever o plano, entrou o comando `ws sync` (seção 4.1.1 da spec): uma branch aberta que precisa do que entrou no `main` se atualiza pela `ws/sync`, não pelo `main`, para o `ws push` não enviar repos que a feature não mudou.
   - Plano: `docs/superpowers/plans/2026-10-15-ws-sync.md` (8 tasks), aprovado; executado em 2026-10-15 no modo Native na branch `harness/ws-sync` do workspace (a partir de `dbc94c3dc`, último commit `ca6afe9ba`). Suíte completa com 272 ok e 0 falha.
   - Revisão final (subagente opus): 4 achados importantes corrigidos com teste: o `ws add` volta a rodar só na `ws/sync` (um squash do PR de uma branch do harness apagaria os trailers do subtree e quebraria o sync de todos); o lembrete do PR da `ws/sync` compara árvores (some depois de squash); `ws sync` e `ws start` voltam à branch na falha e alinham a `ws/sync` local com o origin; o Atlas cai para o `main` quando a `origin/ws/sync` está atrás dele. A spec foi atualizada com esses pontos. Seis menores ficaram anotados (descarte silencioso de commits locais da `ws/sync`, `TF401028` sem retry, `ls-remote` por sufixo, mensagem de conflito em erro interno, teste do `ls-remote` com falha, doc residual).
   - Próximo: o usuário envia a branch e abre o PR; depois do merge, a validação no Azure DevOps real (seção 7.2 da spec).
4. **Próximo subprojeto: SP3** (grafo de arquitetura, navegação semântica e, se for o caso, memória). As ferramentas de memória e indexação (Graphify, Serena etc.) ainda não foram avaliadas. Ponto de partida: `docs/sistemas/` no workspace e `tools/arch-map/` aqui.

## Próximo passo (histórico, antes da execução)
Rodar `/codebase-discovery` nos **16 repos restantes** (ou só nos 6 centrais primeiro: servidor.backend, awx.monorepo, ecommerce.backend, conector.backend, app.frontend, Fly), com os ajustes do piloto:
1. Criar `_discovery/edges.csv` com as colunas `app,tipo,alvo,detalhe,evidencia`. Valores de tipo: db-read, db-write, db-exec, http-in, http-out, mq-pub, mq-sub, job.
2. Seções fixas no `tech/integrations.md`: BD (R/W por objeto), HTTP in/out, filas, jobs, "quem mais toca o meu schema" (via extrato do banco).
3. Pular `user-personas.md` e requisitos. Fases 0 e 5 mínimas (execução sem ninguém para responder: consentimentos → *needs SME*).
4. Lotes de 4 agentes em paralelo. Repos grandes leem por camadas (o que o repo declara, depois os hotspots).
5. Segredos: registrar só o local. Consolidar uma lista para rotação.
O prompt do piloto está reproduzido na seção seguinte e serve de base.

## Achados de segurança (rotacionar)
- `repos/industria-logistica.wms.picking.backend/src/Reserva.WMS.Picking.API/appsettings.Development.json` — connection string com usuário/senha versionada.
- A senha do login `lwms` (réplica de prod) apareceu no histórico da sessão de 2026-09-23.

## Base do prompt por repo (usado no piloto)
Seguir `.agents/skills/codebase-discovery/SKILL.md`. Target: `repos/<repo>` (não modificar). Modo code-only. Output root: `docs/discovery/repos/<repo>/` (confirmado pelo usuário). README → `project-readme.md` no output root. Agent file retido. Exclusões: node_modules, bin, obj, dist, packages, gerados. Sem ninguém para responder: consentimentos → *needs SME*. Evidência extra: `docs/discovery/sources/contexto-usuario.md`, IcePanel (só grep), `extract/db-hml/`. Relatório final ≤ 350 palavras: arquivos, sistema, integrações, pendências, segurança, notas.
