# SP3: Atlas (grafo de arquitetura) e navegação de código no workspace WMS (design)

- **Status:** aprovada pelo usuário em 2026-10-05 (com os nomes Atlas e mapeamento)
- **Subprojeto:** SP3. Depende do SP1 (ADR 0001, `tools/ws`) e do SP2 (Spec Kit multi-repo, hooks `before_specify`/`after_converge`, `docs/sistemas/`, renomeado aqui para `docs/atlas/`)
- **Evidências:**
  - `docs/discovery/sp3-avaliacao-ferramentas.md`: pesquisa de cerca de 40 candidatos. Parte das recomendações foi substituída pelas decisões da seção 2.
  - `docs/discovery/estado-da-sessao.md`: decisões em ordem cronológica.
- **Refinamentos do plano (2026-10-05):** o estado por repo fica em `atlas.estado` (não no `recon-manifest.md`); a política fica em `relevancia.ini` (INI, sem dependência de YAML); as pendências aparecem no topo do `project-readme.md`; o `after_converge` passa a ser o comando obrigatório `speckit.ws.converge`, que roda o Atlas e oferece o `/speckit-ws-commit-push`. Plano: `docs/superpowers/plans/2026-10-05-sp3-atlas.md`
- **Onde se implementa:** no workspace (`C:\src\wms-workspace` ou um workspace refeito do zero), não nesta pasta de discovery

## 1. Objetivo e critério de sucesso

O agente que trabalha no workspace tem dois níveis de conhecimento, sempre atualizados, que também servem de memória entre sessões:
- **Nível 1 (visão geral):**
  - (a) para a feature X, quais repos mudam e o que muda em cada um;
  - (b) se a tabela, proc, view, endpoint ou fila Z mudar, quem é afetado, inclusive de forma transitiva.
- **Nível 2 (visão por repo):** navegação e edição de código dentro de cada repo.

O SP3 está pronto quando:
1. O `ws start` detecta repos que mudaram desde a último mapeamento (por commit, não importa quem mudou), atualiza só o necessário pela política da seção 5 e incorpora o resultado à branch da feature.
2. O `after_converge` atualiza os docs dos repos tocados pela feature, na branch da feature.
3. `/atlas-atualizar` atualiza todos os repos com mudança, sem limite. `/atlas-atualizar --do-zero` refaz o mapeamento do zero.
4. O índice de impacto responde (b) com uma página por objeto: propagação forte e fraca, distância, caminho e ciclos.
5. No `/speckit-specify` e no `/speckit-plan`, o agente usa o nível 1 para preencher "Repos afetados" e listar os dependentes.
6. Na implementação, o agente usa o mapa estrutural do repo (codebase-memory-mcp, ou Graphify nos frontends, conforme o registro) e edita com as ferramentas padrão + ast-grep.
7. A validação da seção 9 passa.

## 2. Decisões tomadas com o usuário (2026-10-05)

| Tema | Decisão |
|---|---|
| Nomes | **Atlas** é o conhecimento mantido (mapa, docs por repo, índice de impacto): `docs/atlas/`, `ws atlas`, `/atlas-atualizar`, `/atlas-consultar`, `atlas/atualizacao`. **Mapeamento** é o processo que o mantém (incremental ou do zero). "Discovery" fica reservado à descoberta de features. A skill de terceiros mantém o nome `codebase-discovery`, e a pasta `_discovery/` que ela gera também |
| Renomeações do SP2 | Entram no SP3: `docs/sistemas/` → `docs/atlas/`, `tools/sistemas/` → `tools/atlas/`, `importa-discovery.sh` → `importa-mapeamento.sh` (e o teste dele), mais as referências no `AGENTS.md`, `docs/workspace.md`, constitution, preset `multirepo` (comando `specify` e templates de spec, plan e tasks) e skills geradas (seção 6.8) |
| Extratores próprios (Opengrep, ScriptDom, Roslyn) | **Não.** "Não manter código" significa não manter extratores. Lógica no `tools/ws` e no `build-map.py` é aceitável |
| CAST Imaging e outros produtos pagos | Fora de cogitação |
| Fonte do nível 1 | A skill `codebase-discovery` (modo code-only, prompt v2 do SP0), rodada de forma incremental pela freshness check por commit do `recon-manifest.md` |
| Gatilhos de atualização | `ws start` (com verificação esperta), `after_converge` e o comando manual, que é completo e sem limite e tem a opção de refazer do zero. Um agendamento pode vir depois (gatilho "agendado + `ws start`"), se for preciso |
| Limite por `ws start` | max(3, nº de repos afetados pela feature) |
| Commits das atualizações | `ws start` e manual: branch fixa `atlas/atualizacao`, com um PR aberto que acumula commits (o `main` do workspace exige PR). `after_converge`: branch da feature |
| A feature vê os docs atualizados | O `ws start` faz merge de `atlas/atualizacao` na branch da feature |
| Consulta do nível 1 | Índice de impacto pré-calculado pelo `build-map.py`, sem LLM. Propagação forte até o fim; propagação fraca mostrada e não expandida |
| Nível 2: mapa estrutural | Escolhido pelo PoC (`poc/sp3-atlas/README.md`): **codebase-memory-mcp 0.11.0**, rodando **no WSL** (o binário Windows recusa máquinas onde o grupo `CodexSandboxUsers` tem escrita no perfil, issue #2023). **Graphify só AST nos 4 frontends** (picking.frontend, app.frontend, ecommerce.frontend, Fly), onde o codebase-memory-mcp errou os usos via DI/imports |
| Desempate do mapa | Nota = 0,55 × N (ferramental de navegação para agentes) + 0,45 × L (cobertura no legado). Suporte a T-SQL não desempata, porque foi verificado que as duas usam a mesma gramática genérica e nenhuma extrai EXEC, escrita ou SQL em string C# |
| Nível 2: edição | **Edição padrão + ast-grep em todos os repos.** O Serena não foi adotado: teve o mesmo acerto e o mesmo custo no PoC, troca LF→CRLF, falha nos `.cs` em cp1252 do legado e cria `obj/` e `.serena/` nos repos. Reavaliar quando houver suporte a encodings mistos ou um plugin oficial do Roslyn LS |
| Plugins LSP nativos, Graphify como nível 1, extratores, agendamento | Fora do escopo do SP3 |

## 3. Estrutura do workspace depois do SP3

O que já existe e não muda fica marcado com "(SP2)".

```
<workspace>/
  AGENTS.md                         (SP2) + seção curta "Atlas" (6.6)
  .mcp.json                         MCPs do workspace: codebase-memory-mcp (via WSL) e Graphify dos frontends (6.7)
  .claude/skills/
    codebase-discovery/             skill trazida desta pasta de discovery, versão fixada
    atlas-atualizar/             comando manual (6.4)
    atlas-consultar/             como consultar o nível 1 e a ponte para o nível 2 (6.6)
  tools/ws/lib/atlas.sh          ws atlas plano | concluir (6.2, 6.3)
  tools/atlas/
    importa-mapeamento.sh            (SP2) passa a importar também o manifest e o traceability index
    build-map.py, build-viz.py      trazidos de tools/arch-map desta pasta; ganham o índice de impacto (6.5)
    relevancia.ini                  política do filtro e das áreas de contrato (5.2), lida com configparser
    prompt-mapeamento.md             prompt v2 do SP0, adaptado ao modo incremental
  docs/atlas/
    mapa-arquitetura.md, *.csv      (SP2) regenerados a cada atualização
    impacto/<objeto>.md             índice de impacto, uma página por objeto
    impacto/ciclos.csv
    ferramentas-por-repo.yml        registro do nível 2: qual mapa cada repo usa (6.7)
    <repo>/                         (SP2) domain, business, tech, project-readme, edges.csv
    <repo>/_discovery/recon-manifest.md       novo: o manifest da skill (commit do recon, áreas lidas)
    <repo>/_discovery/atlas.estado            novo: split=, arvore= e data=, gravado só pelo ws atlas concluir
    <repo>/_discovery/traceability-index.md   novo: ponte regra → arquivo:linha
```

## 4. Fluxos

### 4.1 Início de feature (`/speckit-specify` → hook `before_specify` → `ws start`)
1. Antes do hook, o agente consulta o mapa e o índice com a descrição da feature e escolhe os repos prováveis.
2. O hook passa esses repos para o `ws start` com `--repos`.
3. O `ws start` sincroniza os repos, como no SP1.
4. `ws atlas plano --gatilho start --repos <...>` devolve JSON com a lista de repos a atualizar, as áreas de cada um, os repos adiados e a estimativa de custo (5.4).
5. Se a lista não estiver vazia, o agente mostra o custo estimado e roda o mapeamento incremental (skill `codebase-discovery`) em cada repo, com subagentes em paralelo. Não pede confirmação.
6. `ws atlas concluir --gatilho start`:
   - roda o `build-map.py`;
   - atualiza os manifests, inclusive os repos que só avançaram de commit;
   - faz commit e push em `atlas/atualizacao`;
   - cria a branch da feature a partir do `main` e faz merge de `atlas/atualizacao` nela.
7. O `specify` segue, com o nível 1 atualizado.

### 4.2 Fim de feature (`after_converge`)
1. `ws atlas plano --gatilho converge` lista os repos tocados pela feature (diff da branch contra o `main`), sem aplicar intervalo nem limite.
2. O agente roda a mapeamento incremental nesses repos, sobre o código da branch.
3. `ws atlas concluir --gatilho converge` regenera o nível 1 e faz commit **na branch da feature**. O push segue com o `ws commit-push` do SP2.

### 4.3 Atualização manual (`/atlas-atualizar [--do-zero]`)
- **Sem opção:** `plano --gatilho manual` traz todos os repos com mudança relevante, sem intervalo nem limite. Mapeamento incremental, depois `concluir`, com commit e push em `atlas/atualizacao`.
- **`--do-zero`:** o `plano` ignora os manifests e lista todos os repos. O mapeamento roda do zero, sem freshness check. O agente **pede confirmação** antes, porque o custo fica na casa dos milhões de tokens (o SP0 completo custou cerca de 4,7 milhões).
- O comando manual roda fora de uma feature, a partir do `main` atualizado.

### 4.4 Ciclo da branch `atlas/atualizacao`
Revisado depois da revisão final do plano (2026-10-06): com commits acumulados, os derivados (consolidado, índice de impacto) conflitavam com o `main` a cada converge, e o PR mergeado com squash não era reconhecido.
- **Remontada a cada publicação.** O `concluir` monta a branch sobre o `origin/main`, num commit só, com:
  - as pastas `docs/atlas/<repo>/` que o PR aberto ainda carrega, se o `main` não mexeu nelas desde então. Se mexeu, vale o `main`;
  - as pastas dos repos mapeados agora. Se outra pessoa publicou o mesmo repo depois da versão que a feature tem, fica a dela, e o repo volta a ficar pendente;
  - os derivados regenerados.
- **Push com `--force-with-lease`.** O PR continua o mesmo e se atualiza. Um PR já mergeado, normal ou com squash, simplesmente deixa de carregar o que entrou.
- **Abertura do PR:** à mão, como no SP2. O `concluir` mostra o link da primeira vez.
- **Feature:** o merge de `atlas/atualizacao` na feature só traz `docs/atlas/`. O resto da árvore fica como está na feature, e `docs/atlas/` fica igual ao da branch do Atlas. O que a feature tinha mudado em `docs/atlas/` é refeito pelo mapeamento do `converge`.

## 5. Política de atualização (`ws atlas plano`)

### 5.1 Detecção (sempre roda, sem custo)
- Para cada repo, compara o commit de origem atual com o gravado no manifest.
- No workspace, o commit de origem sai da mensagem do squash do subtree (`git-subtree-split`).
- Se forem iguais, o repo não muda.

### 5.2 Filtro de relevância (sem custo)
- Calcula `git diff --name-only <gravado>..<atual>` no repo de origem, ou o equivalente no prefixo do workspace.
- Descarta as exclusões do manifest e os padrões de `relevancia.ini`: testes, assets, lockfiles, docs, pipelines e gerados.
- Se não sobrar nada, o repo só avança o commit no manifest, com o registro "mudança irrelevante".

### 5.3 Decisão
- **Atualiza agora** se:
  - a mudança relevante toca área de contrato, ou seja, casa com os padrões de caminho ou com as palavras-chave nas linhas do diff de `relevancia.ini` (`Controllers/`, `*Client*`, `Repositor*`, `*.sql`, `appsettings*`, `web.config`; `[Http`, `[Route`, `HttpClient`, `axios`, `SqlCommand`, `EXEC`, `Publish` etc.); ou
  - o repo está em `--repos`.
- **Adia**, nos outros casos. Atualiza quando passar o intervalo mínimo desde a última atualização (padrão de 7 dias) ou quando os arquivos relevantes acumulados passarem de um limiar (padrão de 30). As duas constantes ficam em `relevancia.ini`.

### 5.4 Limite e saída
- **No `ws start`:** atualiza no máximo max(3, nº de repos em `--repos`). A prioridade é: primeiro os de `--repos`, depois os que tocam área de contrato e depois os adiados vencidos. Os restantes ficam pendentes.
- **No `converge` e no manual:** sem limite.
- **Saída:** JSON com, por repo, a ação (`atualizar`, `avançar`, `adiar`, `pendente`), as áreas alteradas, o número de arquivos e a estimativa de tokens. A estimativa usa uma faixa por arquivo relevante calibrada com o custo do SP0 e é ajustada depois da validação.
- **Pendências:** ficam gravadas no manifest e aparecem no topo do `docs/atlas/<repo>/project-readme.md` como aviso.

## 6. Componentes

### 6.1 Mapeamento incremental (skill `codebase-discovery`)
- **Skill.** A `codebase-discovery` é copiada para `.claude/skills/codebase-discovery/` do workspace com a versão fixada. Atualizá-la é uma ação explícita.
- **Execução.** Modo code-only. O output root é `docs/atlas/<repo>/` e o alvo é `repos/<repo>/`, em leitura.
- **Prompt.** `prompt-mapeamento.md` é o prompt v2 do SP0 com três ajustes:
  - usa o manifest do workspace;
  - roda só as áreas passadas pelo `plano`;
  - grava o commit de origem.
  - **aprofunda onde mexe** (decisão do usuário após a validação 9.2.1, 2026-10-06): cria os docs de regras e de modelo (`areas/`) das áreas tocadas que ainda não os têm. A base vai ganhando a profundidade de um mapeamento do zero só onde o código muda;
  - fixa a notação das arestas (verbo e rota primeiro no HTTP; `db-exec` só para procedure; sem tabelas de controle como `__EFMigrationsHistory`).
- **Saída por repo:** docs atualizados, `edges.csv`, `recon-manifest.md` e `traceability-index.md`. Os outros arquivos de `_discovery/` continuam fora do workspace, como no SP2.

### 6.2 `ws atlas plano`
Implementa a seção 5. É só shell e git, sem LLM e sem rede além da que o `ws start` já usou.

### 6.3 `ws atlas concluir`
- Roda o `build-map.py` e o filtro de segredos do `importa-mapeamento.sh` sobre os arquivos alterados.
- Atualiza os manifests e faz commit com a mensagem `atlas: atualiza mapeamento de <repos>`, sem atribuição do Claude.
- Push conforme o gatilho:
  - **start e manual:** push em `atlas/atualizacao`. Se for rejeitado: fetch, rebase e nova tentativa, até 3 vezes.
  - **converge:** só o commit; o push segue com o `ws commit-push`.
- **No start:** cria a branch da feature e faz merge de `atlas/atualizacao` nela.
- Os casos de erro estão na seção 7.

### 6.4 Skill `/atlas-atualizar`
Orquestra plano → mapeamento (com subagentes) → concluir. Recebe `--do-zero` e `--repos <lista>` (opcional, para atualizar só alguns repos à mão).

### 6.5 Índice de impacto (`build-map.py`)
- **Entrada:** os `edges.csv` dos repos, o `edges-sqlagent.csv` e as dependências do catálogo do banco (`sys.sql_expression_dependencies`, já extraídas), filtradas pelo escopo do banco do SP0.
- **Propagação forte**, seguida até o fim, sem limite de profundidade:
  - objeto SQL → views, procs e funções que o referenciam → jobs e código que leem, escrevem ou executam esses objetos;
  - endpoint → clientes HTTP;
  - fila → quem publica e quem consome.
- **Propagação fraca:** de um app atingido para os endpoints e filas que ele expõe. A página lista o app, mas não expande. O agente decide se o contrato dele muda e abre a página do endpoint.
- **Página `impacto/<objeto>.md`:**
  - cada afetado aparece uma vez, na menor distância, com o caminho mais curto, o tipo de acesso e a evidência (`arquivo:linha`), agrupados por repo;
  - acima de cerca de 50 itens, mostra um resumo por repo e manda a lista completa para `impacto/<objeto>.completo.md`;
  - o limite é calibrado pela medição do PoC (seção 9.1).
- **Ciclos:** marcação de visitados na busca e componentes fortemente conexos. Seção "Ciclos" na página e `impacto/ciclos.csv`. Mudar um membro de um ciclo marca o ciclo inteiro, com aviso.
- **Quais objetos ganham página:** todo objeto com pelo menos um dependente. Os nomes de arquivo são normalizados (`db.schema.objeto`, `METODO-rota`).
- **Ajuste da validação 9.2.2 (2026-10-06):**
  - **Procs fora do escopo.** As procs que dependem do objeto e estão fora do escopo (`procs-escopo.csv`) aparecem no grupo `banco X, fora do escopo`, com o motivo. A propagação só segue delas até os repos que as executam ou versionam. Um objeto cujos afetados são todos procs fora do escopo não ganha página.
  - **Aresta `db-def`.** Um `CREATE`/`ALTER` de proc, view, função ou trigger em `repos/<repo>/**/*.sql` liga o objeto ao repo. O objeto precisa estar no catálogo, e o `USE` do arquivo desempata o banco. O resultado vai para `edges-sqldef.csv`.
  - **Efeito.** O índice passou de 5.509 para 5.604 páginas, e a pasta de 25 MB para 38 MB. A mediana de afetados foi de 2 para 4, o p90 de 24 para 46, e o maior caso tem 2.024 afetados.
- **Adendo (2026-10-07): só objetos tocados pelo WMS.** Substitui a regra "todo objeto com pelo menos um dependente".
  - **Regra.** Um objeto só ganha página se a propagação dele chega a pelo menos um repo ou job em escopo. Nas páginas que ficam, todos os dependentes continuam listados.
  - **Triggers (opção B do usuário).** Uma trigger em tabela que um repo ou job grava diretamente (`db-write`) liga o que ela referencia a quem grava (acesso `db-write em <tabela> (trigger)`). Gravação feita dentro de procs não conta, porque o catálogo não separa leitura de escrita `[assumption]`. As opções descartadas foram ignorar triggers (1.370 páginas) e seguir a cadeia completa (5.394).
  - **`banco/`** continua completo: é entrada do `build-map.py`, e o fechamento precisa do catálogo inteiro para enxergar um uso novo.
  - **Efeito.** O índice caiu de 5.604 para 2.156 páginas, e a pasta de 38 MB para 21 MB. O LinxFranquia foi de cerca de 1.600 para 36 páginas, e o Audit de 234 para 62. A mediana de afetados é 3, o p90 é 94 e o máximo é 2.027.

### 6.6 Uso pelo agente (`AGENTS.md` e skill `atlas-consultar`)
- **`AGENTS.md`:** uma seção de poucas linhas que aponta para a skill. Nada do grafo é carregado de antemão.
- **No `/speckit-specify`:** mapa + docs de domínio dos repos candidatos → "Repos afetados" com o que muda em cada repo.
- **No `/speckit-plan`:** página de impacto de cada objeto alterado. Dependentes fortes viram tarefa ou risco; fracos viram ponto a confirmar.
- **Repo pendente:** aviso com as áreas desatualizadas.
- **Ponte para o código:** regra ou fluxo → `traceability-index.md` → `arquivo:linha` → ferramentas do nível 2.

### 6.7 Nível 2
- **codebase-memory-mcp (repos de backend).** Versão fixada (0.11.0, checksum conferido), binário Linux executado no WSL. O `.mcp.json` o chama por `wsl.exe`, e ele lê o workspace por `/mnt/c/...`.
  - Cada `repos/<repo>` é um projeto indexado com o nome do repo.
  - Os subtrees não são raízes git, então o watcher precisa de `watch_non_git true`.
  - O índice fica no cache do WSL, fora do git.
  - `ws atlas` ganha um passo de bootstrap que confere o WSL e o binário e indexa os repos que faltam.
  - Responde "quem chama X" (`trace_path`), "código de X" (`get_code_snippet`), busca (`search_code`) e consultas Cypher (`query_graph`).
- **Graphify (4 frontends).** Versão fixada (`graphifyy[sql]` 0.9.77), só AST, sem LLM. Os 4 grafos são juntados com `graphify merge-graphs` num único grafo servido por um MCP (`graphify-mcp`). O grafo é regenerado pelo `ws atlas concluir` e pelo `ws start` (`graphify update`, alguns segundos por frontend) e fica fora do git.
- **Edição.** Ferramentas padrão do Claude Code + ast-grep, em todos os repos. No PoC, preservaram bytes, BOM e LF.
- **`ferramentas-por-repo.yml`.** Uma entrada por repo: `mapa: cbm|graphify`. Um repo muda de mapa quando um novo teste passa, por exemplo se o codebase-memory-mcp passar a resolver usos via DI no Angular.
- **SQL.** A dependência proc ↔ tabela vem do índice de impacto (catálogo do banco), não dos `.sql` dos repos.

### 6.8 Renomeações do SP2
- Os caminhos e nomes são renomeados de uma vez, num commit próprio, antes dos outros componentes:
  - `docs/sistemas/` → `docs/atlas/` (inclui `mapa-arquitetura.md`, CSVs e as pastas por repo);
  - `tools/sistemas/importa-discovery.sh` → `tools/atlas/importa-mapeamento.sh`;
  - `tools/ws/tests/test_importa_discovery.sh` → `test_importa_mapeamento.sh`.
- Referências a atualizar:
  - `AGENTS.md`, `docs/workspace.md` e `.specify/memory/constitution.md`;
  - fonte do preset em `tools/speckit/multirepo/` (comando `speckit.specify.md` e templates de spec, plan e tasks), reinstalado com `ws speckit` para regenerar `.specify/presets/` e `.claude/skills/speckit-*`.
- **Verificação:** `grep -rn "sistemas"` fora de `repos/` e de `specs/` não acha mais referências ao nome antigo, e a suíte do `tools/ws` continua passando.
- Se o workspace for refeito do zero, os nomes novos já entram desde o início e esta seção vira só a verificação.

## 7. Tratamento de erros

| Situação | Comportamento |
|---|---|
| Mapeamento de um repo falha ou estoura o tempo | O manifest daquele repo não avança, o repo fica pendente e a feature segue com aviso. A atualização nunca bloqueia a feature |
| Push em `atlas/atualizacao` rejeitado | Fetch, rebase e nova tentativa (até 3). Conflito no mesmo doc: descarta a versão local daquele repo e o deixa pendente |
| Merge de `atlas/atualizacao` na feature | Não conflita: só `docs/atlas/` vem da branch do Atlas (4.4). Se o git falhar mesmo assim, cancela, avisa e a feature segue com os docs do `main` |
| `--do-zero` interrompido | Os repos que terminaram entram e os outros ficam pendentes |
| Commit de origem gravado não existe mais (rebase ou force-push no repo) | Trata o repo como "refazer do zero" e avisa |
| Arquivo com padrão de segredo na saída do mapeamento | Não entra no commit e é listado |
| MCP do mapa não sobe (WSL desligado, versão divergente, ACL) | O agente avisa e cai para grep e ast-grep naquele repo |

## 8. Testes
Mesmo estilo da suíte bash do `tools/ws`, com fixtures locais, TDD e sem rede, salvo onde indicado.
- **`ws atlas plano`:**
  - commit igual → nada;
  - só arquivos irrelevantes → `avançar`;
  - área de contrato por caminho e por palavra-chave → `atualizar`;
  - mudança interna recente → `adiar`;
  - intervalo vencido e limiar de arquivos → `atualizar`;
  - limite max(3, n) com prioridade;
  - `--repos`;
  - gatilhos `converge` e `manual` sem limite;
  - `--do-zero` lista tudo;
  - commit gravado inexistente;
  - JSON válido em todos os casos.
- **`ws atlas concluir`:**
  - commit em `atlas/atualizacao`, que é criada ou recriada depois do merge do PR;
  - nova tentativa com push rejeitado (origin local);
  - merge na feature;
  - cancelamento do merge em conflito;
  - gatilho `converge` faz commit na branch da feature e não faz push;
  - filtro de segredos.
- **Índice de impacto:** grafo de teste com cadeia forte de 4 níveis, aresta fraca não expandida, distância e caminho mínimo, ciclo de 2 e de 3 nós, resumo acima do limite, nomes normalizados.
- **Validação manual de ponta a ponta:**
  - uma feature de teste com `ws start` que dispara atualização, `specify` e `plan` usando o índice, implementação usando o nível 2 e `after_converge` atualizando os docs;
  - depois, `/atlas-atualizar` num repo com mudança feita à mão fora do harness.

## 9. PoC e validação

### 9.1 PoC descartável, antes do plano de implementação (`poc/sp3-*`): **executado em 2026-10-05**, resultados em `poc/sp3-atlas/README.md`
1. **Mapa estrutural:** codebase-memory-mcp contra Graphify só AST, em servidor.backend (legado .NET Framework), um repo .NET moderno e um Angular.
   - **Critérios:** funcionar no legado, acertar cerca de 10 perguntas de navegação conferidas à mão, tokens por resposta, atualização automática e estabilidade no Windows.
   - **Desempate:** 0,55 × N + 0,45 × L, numa escala de 0 a 10.
     - **N:** rubrica de 4 itens, cada um valendo até 2,5: busca de código, trecho de símbolo, caminhos de chamada, filtro por repo.
     - **L:** % de uma amostra de cerca de 30 símbolos e chamadas do servidor.backend, conferidos à mão, que a ferramenta encontra.
2. **Serena:** instalar o executável e desligar o dashboard. Nos mesmos 3 repos, rodar 3 tarefas: achar referências, renomear símbolo e substituir corpo de método. Comparar tokens e acerto com a edição padrão.
   - **Resultado:** não adotado (ver seção 2).
3. **Profundidade e ciclos:** calcular o índice sobre as arestas atuais e o catálogo para calibrar o limite de cerca de 50 itens e contar os ciclos.

### 9.2 Validação do nível 1, depois de implementado
1. **Incremental contra completa:** no AWX (com mudanças desde 23/09/2026), comparar arestas e docs da atualização incremental com os de uma rodada completa. Custo único de cerca de 300–500 mil tokens.
2. **Features reais:** 3 a 5 mudanças recentes que cruzaram repos (PRs do Azure DevOps), propostas pelo agente e corrigidas pelo usuário. O nível 1 precisa apontar os repos e objetos que os PRs mudaram.
3. **Regressão:** os casos ficam guardados para quando o prompt, a skill ou `relevancia.ini` mudarem.

## 10. Fora do escopo
- Extratores determinísticos próprios (Opengrep, ScriptDom, Roslyn, ts-morph) e produtos pagos (CAST Imaging, Sourcegraph).
- Plugins LSP nativos do Claude Code e Serena: podem ser reavaliados depois, com os achados do PoC.
- Graphify como fonte do nível 1.
- Atualização agendada: pode ser somada depois.
- Bancos de grafo (Neo4j, LadybugDB) e MCPs de memória de chat (Graphiti, mem0, Cognee).
- Correção de bugs, segurança ou segredos encontrados nos repos.

## 11. Riscos
- **A precisão da mapeamento incremental se desgasta com o tempo.** Mitigações: a validação 9.2.1, a regressão e o `--do-zero` periódico.
- **Custo em tokens no `ws start`.** Mitigações: a política da seção 5, o limite max(3, n) e a estimativa mostrada antes de rodar.
- **Hooks são instruções, não execução automática.** O agente pode pular a atualização. Mitigação: o mesmo tratamento do SP2 (`optional: false`, `AGENTS.md`). Como a detecção é por commit, o próximo `ws start` recupera o que foi pulado.
- **Ferramentas 0.x (codebase-memory-mcp, Graphify).** Mitigações: versão fixada, a degradação da seção 7 e o registro por repo.
- **Dependência do WSL.** O codebase-memory-mcp só roda no WSL nas máquinas com o sandbox do Codex. Mitigações: o bootstrap confere o WSL; a issue #2023 é acompanhada; quando ela for corrigida, o binário Windows pode substituir o WSL sem mudar o resto.
- **PR de docs esperando aprovação por muito tempo.** Mitigação: o `concluir` avisa quando o PR carrega mais de 10 repos ou tem um repo mapeado há mais de 7 dias (`pr_max_repos` e `pr_max_dias` em `relevancia.ini`).
