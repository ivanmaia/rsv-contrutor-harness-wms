# SP3: validação do Atlas

Spec: `docs/superpowers/specs/2026-10-05-sp3-grafo-e-navegacao-design.md`, seção 9.2. Plano: `docs/superpowers/plans/2026-10-05-sp3-atlas.md`, Task 8.

## 9.2.1 Incremental contra do-zero no AWX (2026-10-06)

**Montagem:**
- **Branch e sync.** Branch descartável `sp3-val-awx` a partir de `sp3-atlas`. O AWX foi sincronizado só localmente (fetch raso e `subtree merge --squash`, sem push) até `e495e61`.
- **Commit gravado.** O commit do SP0 para o AWX era `af25344`, de 23/09/2026.
- **Plano manual.** Listou 205 arquivos relevantes no AWX. A estimativa era de 410 mil tokens para o incremental.
- **Mapeamentos.** Os dois foram feitos por subagentes com o prompt `tools/atlas/prompt-mapeamento.md`:
  - **incremental:** sobre os docs do SP0;
  - **do-zero:** com a pasta do repo esvaziada.
- **Resultados.** Ficaram em `poc/sp3-atlas/val/{incremental,do-zero}/`. A branch foi apagada depois, e nada foi publicado.

| | Incremental | Do-zero |
|---|---|---|
| Custo | ~327 mil tokens, 57 chamadas, 9 min | ~427 mil tokens, 96 chamadas, 28 min |
| Linhas do `edges.csv` | 292 | 250 |
| Docs (fora de `_discovery/`) | 56 KB: os mesmos arquivos do SP0, reescritos | 84 KB: os mesmos e mais `areas/` (14 arquivos `rules-*`/`model-*` em 10 áreas) e um workflow novo |
| Afirmações rastreadas | 73 (C-1 a C-73) | 88 (C-1 a C-92) |
| Pendências *needs SME* | 8 | 30 |

**Arestas.** Recall do incremental sobre o do-zero, comparando por tipo e alvo normalizado (rota com verbo no HTTP, `banco.schema.objeto` no SQL):

| Tipo | Do-zero | Incremental | Em ambos | Recall |
|---|---|---|---|---|
| db-read | 27 | 26 | 26 | 96% |
| db-write | 31 | 31 | 31 | 100% |
| db-exec | 12 | 17 | 5 | 42% |
| http-in | 86 | 88 | 86 | 100% |
| http-out | 46 | 48 | 42 | 91% |
| mq-pub | 8 | 11 | 6 | 75% |
| mq-sub | 6 | 6 | 5 | 83% |
| job | 7 | 7 | 7 | 100% |
| **Total** | | | | **93%** |

**De onde vêm as diferenças.** Lidas uma a uma (`poc/sp3-atlas/val/so-no-*.txt`):
- **db-exec:**
  - 7 das 12 arestas só do do-zero são o `__efmigrationshistory` de cada Postgres, que é ruído de migrations do EF;
  - o incremental classifica como `db-exec` escritas na ACL que o do-zero classifica como `db-write`.

  Sem as migrations, os dois concordam.
- **http-out:** a maior parte é notação. O incremental escreve `POST (URL base = ACL api/v1/wms/produtos/sincronizar)` com a chave de config no `alvo`; o do-zero escreve `POST /api/v1/wms/produtos/sincronizar`. É a mesma aresta.
- **mq:** filas de DLQ e retry com placeholders diferentes (`{fila}-dlq` contra `<fila>-dlq`). Num caso, um lado registrou o nome da fila e o outro o da exchange (`iniciar-faturamento` contra `faturamento.nota-fiscal.faturar.requested.v1`).

**Conclusão sobre as arestas:** com a notação e as migrations de lado, o incremental cobre o que o do-zero cobre. O critério da Task 8, recall ≥ 90% em `db-*` e `http-*`, passa em db-read, db-write, http-in e http-out. Ele falha na letra em db-exec, por notação.

**Conclusão sobre os docs:** **o critério não passa.** O incremental mantém a profundidade do mapeamento de origem. O SP0 não tinha `areas/` para o AWX, então o incremental também não tem. O do-zero, com a skill e o prompt atuais, gerou 14 documentos de regras e modelos por área. Também levantou mais divergências entre código e documentação: a ACL grava no WMS legado mas o README diz "somente leitura"; a rota é `importar` no código e `sincronizar` no contrato. Regras de negócio do do-zero não têm equivalente no incremental.

**Achados para a política e para o prompt:**
1. **Filtro de relevância.** Deixou passar ruído: `.specify/` (o Spec Kit do próprio AWX), `.gitignore`, `.trivyignore`, `.nvmrc`, `Dockerfile`, `e2e/` e `playwright.config.ts`. Isso aumenta a lista de arquivos e a estimativa.
2. **Notação.** O prompt deveria fixar o `detalhe` de `http-out` como `MÉTODO /rota` antes de qualquer comentário. Também deveria proibir `db-exec` para escrita em tabela (`db-exec` é só procedure) e mandar ignorar o `__efmigrationshistory`.
3. **Profundidade.** O incremental não aprofunda o que o mapeamento original não cobriu. Para repos mapeados de forma rasa no SP0, um `--do-zero` uma vez (ou por área) nivela a base. Depois disso o incremental mantém o nível.

**Decisão do usuário (2026-10-06):** aprofundar onde o código muda.
- O incremental passa a criar os docs de regras e de modelo das áreas tocadas que ainda não os têm.
- O filtro deixou de considerar o ruído do item 1.
- O prompt fixou a notação do item 2.

Workspace: commit `80842f2`.

## 9.2.2 Features reais (2026-10-06)

**Montagem:**
- **Escolha das features.** Foram 5 features dos últimos 60 dias que cruzaram repos. Saíram dos PRs concluídos no Azure DevOps (`az repos pr list`, só leitura, 244 PRs nos 17 repos), agrupados pelo work item, e o usuário aprovou a lista.
- **Gabarito.** São os arquivos alterados em todos os PRs ligados ao work item, inclusive os de repos fora do workspace. Está em `poc/sp3-atlas/val/features/` (`gabarito-resumo.txt`, `gabarito-arquivos.txt`, `work-items.txt`).
- **Pergunta.** Um subagente por feature recebeu só a descrição de negócio (o texto do work item sem o refinamento técnico, sem nomes de repos nem de objetos). Ele respondeu usando só `docs/atlas/` e a skill `atlas-consultar`, sem código, git ou MCP.
- **Custo.** De 57 a 106 mil tokens por feature, 1 a 2 minutos cada.
- **Vazamento.** O Atlas foi mapeado em 23/09. Por isso D e E, concluídas antes dessa data, podem já estar refletidas nos docs. A, B e C são posteriores.

| | Feature | Repos que mudaram de fato | Resposta do Atlas | Repos | Objetos |
|---|---|---|---|---|---|
| A | 72196 Desacoplar auditoria | servidor.backend, awx.monorepo; fora: servicos-linx-wms | servidor e awx **sim**, conector **talvez**; fora: "APIs Linx" e servicos-linx-wms **talvez** | 2/2, fora 1/1 | Acertou `prInsereMovimentacaoAuditoria`, `MovimentacaoAuditoria`, o job Hangfire, `AuditoriaController` e o padrão ACL → Connector → Linx. |
| B | 72561 Exigência de bip | ecommerce.backend, ecommerce.frontend | os dois **sim**; servidor e awx **talvez** | 2/2 | Acertou a tabela nova em `ReservaNet.checkout`, o GET/PUT no `CheckoutController`, a tela `checkout-parametrizacoes` e o service no padrão do aviso de caixa. Não previu a alteração de 2 procs do checkout (`pr_RESERVANET_ECOMMERCE_DETALHE_PEDIDO_CHECKOUT`, `..._PEDIDO_OBTER_ALERTAS`). |
| C | 72531 Trilha de auditoria | ecommerce.backend, ecommerce.frontend | os dois **sim**; servidor e awx **talvez** | 2/2 | Acertou o GET de histórico e a tela. Supôs uma tabela de log nova; a trilha leu os `_log` criados na feature B. |
| D | 72523 Produto por CUP/SKU | awx.monorepo (Estoque, ERP.Connector, ACL), servidor.backend; fora: servicos-linx-wms | servidor **sim**; awx **talvez** (as rotas já estavam no Atlas: vazamento); fora: servicos-linx-wms "não muda" | 2/2 (1 como talvez), fora 0/1 | No servidor.backend errou o componente: apontou `ProdutoRepositorio` e `/api/Produto`, mas mudaram `NotasController`, `NotaFiscalRepositorio` e `DashboardAuditoria`. |
| E | 72631 Descontinuar Pedido Bloqueado | servidor.backend, ecommerce.backend; fora: erp-dinossauro | servidor **sim**; ecommerce.backend **não**; fora: "On Demand" | 1/2, fora 0/1 | Acertou `PedidoBloqueado`, o sinônimo, o job de fraude e o serviço. Faltaram `PedidoBloqueadoLogAtividade`, `PedidoBloqueadoProcessamento` e `pr_inserir_pedido_bloqueado`: o catálogo do WMS, extraído em 24/09, já não tinha essas tabelas, que tinham caído no deploy de 21/09. |

**Placar:**
- **Repos do workspace:** 9 de 10 identificados (8 como sim e 1 como talvez). Nenhum sim foi errado. Houve 7 talvez a mais, todos com justificativa.
- **Repos fora do workspace:** 1 de 3.

**Achados:**
1. **Repos fora do workspace.** Três das 5 features mexeram em repos que não estão no workspace: `integracoes.wms.servicos-linx-wms.monorepo` em A e D, e `industria-logistica.wms.erp-dinossauro.backend` em E. Para o Atlas eles são só "sistemas externos", e por isso as respostas erram ou ficam vagas.
2. **Proc definida num repo e marcada como fora do escopo.** O `Reserva.dbo.pObterPorPedido` lê `PedidoBloqueado` e está definido em `ecommerce.backend/sql/Pre-Expedicao/CREATE_pObterPorPedido.sql`. Mesmo assim:
   - o `procs-escopo.csv` marca a proc como "fora";
   - o índice de impacto não a lista;
   - nada liga o `.sql` ao repo.

   É por isso que o ecommerce.backend não apareceu em E. A mesma página de impacto também deixou de fora o `PR_RSV_RESERVANET_ONDEMAND_PEDIDO_ANALISE_FRAUDE`.
3. **Precisão de componente dentro do repo.** No nível 1 ela é média: em D, o repo saiu certo e o ponto de entrada saiu errado. Isso é papel do nível 2 (cbm), que este teste não usou de propósito.
4. **Vazamento.** Aconteceu em D, como previsto: as rotas novas já estavam no Atlas, e o agente marcou o awx como talvez ("já existe").

**Decisões do usuário (2026-10-06):**
- **Repos fora do workspace:** ficam como estão. O Atlas continua a tratá-los como sistemas externos.
- **Índice:** corrigir os dois pontos do achado 2, o que foi feito com TDD:
  - as procs fora do escopo aparecem como dependentes, num grupo próprio;
  - a aresta `db-def` liga os `.sql` versionados ao repo;
  - detalhes na spec, seção 6.5.

  **Reteste de E.** A página `wms.dbo.pedidobloqueado.md` passou a listar:
  - o `PR_RSV_RESERVANET_ONDEMAND_PEDIDO_ANALISE_FRAUDE` (fora do escopo, ONDEMAND);
  - o `pObterPorPedido`;
  - o ecommerce.backend, com distância 3 e `db-def` em `sql/Pre-Expedicao/CREATE_pObterPorPedido.sql:4`.

## Task 8, Step 7: ponta a ponta (2026-10-06)

**Ambiente** (descartável):
- **Workspace e origin.** O workspace é `C:\src\wms-workspace-e2e3`. O origin bare é `C:\src\wms-e2e3-origin.git`, com o `main` em `sp3-atlas`.
- **Repos TMS.** `tms.backend` e `tms-finished.backend` apontam para espelhos locais (`C:\src\wms-e2e3-tms*.git`). Os outros 15 repos têm o `atlas.estado` avançado até o commit atual, para o teste mapear só os TMS.
- **Proteção contra push.** Um `pushInsteadOf` bloqueia qualquer push para o Azure DevOps.
- **Execução.** O agente rodou em `claude -p` com o mesmo `session_id` nos passos 1 a 4.
- **Feature de teste:** histórico da integração com a Intelipost, que mexe nos 2 repos TMS. Antes de começar, um commit "de outro time" foi feito no espelho do `tms.backend`.

| Item | Resultado | Observação |
|---|---|---|
| 1. `/speckit-specify`: o hook roda o Atlas `start` e a spec preenche "Repos afetados" | ok, depois de uma correção | **Primeira tentativa:** o `ws start` parou com árvore suja por causa da pasta `.serena/`, que o MCP Serena do usuário cria. O `.gitignore` passou a ignorá-la (commit `742a92eb`, com teste). **Segunda tentativa:** o plano mapeou o `tms.backend`, que tinha o commit do outro time. O mapeamento criou `model-envio-intelipost.md` (aprofundou onde mexeu) e publicou em `atlas/atualizacao`. A feature incorporou essa branch. A spec listou os 2 repos certos e citou o método novo do outro time ("`RegistraTentativa` que ninguém chama"). Custo: US$ 3,04 |
| 2. `/speckit-plan` cita o Atlas e o impacto | ok | O `research.md` (R9, "Contratos e impacto") consulta o `impacto/indice.csv` e os docs dos 2 repos. A tabela é nova, então não há página de impacto a citar. Custo: US$ 1,48 |
| 3. Implementação com o mapa do nível 2 | ok | O agente usou `codebase-memory` (`list_projects` e `trace_path` 3 vezes) para achar quem chama, além de Read, Edit e grep. Os builds dos dois repos passaram |
| 4. `/speckit-converge`: o hook mapeia de novo, faz commit em `docs/atlas/` e o envio é recusado | ok | Commit `c7019832`, só com `docs/atlas/`. Os 2 repos foram mapeados de novo, e a tabela nova liga os dois no índice. Nada foi enviado. Custo dos passos 3 e 4: US$ 6,50 |
| 5. Commit "de outro time" e `/atlas-atualizar` | ok (reexecutado depois de liberar memória) | A primeira execução foi encerrada pelo Claude Code por falta de memória na máquina. Na segunda, o plano manual achou 3 repos com mudanças: o `tms-finished.backend` (commit do outro time, `c50d26d`) e o awx e o backoffice, que andaram no Azure DevOps durante o dia. Os três foram mapeados, cada um com uma área nova em `areas/`, e o `ConsultaPorPedido` (`GET /api/v1/shipment_order/{pedido}`) entrou no `edges.csv`. A branch `atlas/atualizacao` foi publicada no origin (`07af2c94`), e a branch descartável foi apagada. Custo: US$ 12,46 (cerca de 635 mil tokens; a estimativa do plano era de 90 mil) |

**Achados:**
1. **Pasta do Serena.** O `.serena/` travava o `ws start`. Já corrigido.
2. **Nome do projeto no cbm.** O `ws atlas mapas` indexa com `--name <repo>`, o mesmo nome em qualquer checkout. Por isso o índice do `tms-finished` em e2e3 apontava para `C:\src\wms-workspace` (o agente percebeu e conferiu no código). Com dois workspaces na mesma máquina, um sobrescreve o mapa do outro. Depois do teste, é preciso reindexar os TMS no workspace real.
3. **Mensagem do commit do Atlas.** A mensagem lista repos cujo `atlas.estado` só ganhou a linha `arvore=` (o awx, no passo 1), como se tivessem sido mapeados.
4. **Link do PR.** Com um origin que não é do Azure DevOps, o link de "abra o PR" sai inválido (`C:/src/...pullrequestcreate?...`). No origin real o link é válido.
**Correções (2026-10-06):**
- **Achado 1:** commit `742a92eb`.
- **Achado 2:** commits `d15392f5` e `95e5cf73`. O projeto no cbm passou a ser `<pasta do workspace>-<repo>`, e os 13 backends do workspace real foram reindexados com o nome novo.
- **Achado 3:** commit `d15392f5`. Quem só avançou o estado aparece como "estado avançado".
- **Achado 4:** fica como está.
- **Suíte:** 173 ok.

5. **Estimativa de custo.** No item 5, a estimativa do plano ficou cerca de 7 vezes abaixo do real: 90 mil tokens estimados contra uns 635 mil usados. A regra de aprofundar onde mexe cria docs de áreas inteiras, e o `tokens_por_arquivo` (2.000) e o `tokens_minimo_repo` (30.000) não contam com isso.

## 9.2.3 Regressão

Os resultados do incremental e do do-zero ficam em `poc/sp3-atlas/val/` como referência para comparar depois de mudanças no prompt ou na skill.
