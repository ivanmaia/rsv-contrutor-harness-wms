# Sondagem de acesso aos bancos (2026-09-23)

Só foram feitas consultas ao catálogo (`sys.*`). Nenhuma escrita e nenhuma leitura de dados de negócio.

## Servidor
- `10.1.1.3` = **SRV-ALW01**, SQL Server 2019 Enterprise CU20. O nome sugere AlwaysOn / produção (**a confirmar**).

- **Réplica somente leitura**, confirmada pelo usuário e por `DATABASEPROPERTYEX(...,'Updateability') = READ_ONLY` em WMS, Reserva, ReservaNet e WMSTASKS. As permissões de escrita do login não têm efeito nesta instância.

## Credencial `docs/credentials/DatabaseReadOnly.txt` (login `lwms`, `Application Name=WmsApi`)
O login tem permissões de escrita (é a credencial de aplicação do WMS3.API), mas a instância é READ_ONLY. O bloqueio real é a **falta de VIEW DEFINITION**.

| DB | VIEW DEFINITION | INSERT/UPDATE | EXECUTE | db_datawriter |
|---|---|---|---|---|
| WMS | não | **sim** | **sim** | **sim** |
| Reserva | não | **sim** | **sim** | **sim** |
| ReservaNet | não | não | **sim** | não |
| WMSTASKS | não | **sim** | não | **sim** |
| WMS_Produtividade | sem acesso | | | |
| msdb (jobs) | SELECT negado em sysjobs/sysjobsteps | | | |

Consequências:
- `sys.sql_modules.definition` volta **NULL** para todos os módulos (WMS 419, Reserva 8.802, ReservaNet 108), então os corpos de procs, views e triggers não podem ser lidos.
- `sys.sql_expression_dependencies` volta **0 linhas**, então as dependências não são visíveis.
- Os jobs do SQL Agent não são visíveis.

## Volumetria (objetos de usuário)
| DB | Tabelas | Views | Procs | Funções | Triggers | Sinônimos |
|---|---|---|---|---|---|---|
| WMS | 360 | 89 | 183 | 26 | 121 | 187 |
| Reserva | 4.533 | 2.024 | 3.801 | 782 | 2.164 | 100 |
| ReservaNet | 172 | 2 | 74 | 3 | 29 | 81 |
| WMSTASKS | 11 | 0 | 0 | 0 | 0 | 0 |

## Acoplamento entre bancos via SINÔNIMOS (evidência já obtida)
- **WMS →** Reserva (181), ReservaNet (3), Ecommerce (2), Reserva_Integracao_Anymarket (1)
- **ReservaNet →** RESERVA (59), WMS (21), Reserva_Integracao_Anymarket (1)
- **Reserva →** SINCLOJA (33), AUDIT (29), SistemasReserva (23), **WMS (7)**, ReservaNet (2), salescloud, SAE, distributioncenter (1 cada), servidor linkado `AUDIT` (2)

Isso confirma, com dados, o acoplamento WMS↔LINX (Reserva) via banco: 181 sinônimos do WMS apontam para o Reserva.

## Homologação: fonte das definições (2026-09-23)
- `10.11.0.5` = **SRV-HML-SQL** (SQL Server 15.0.4430). Bancos em **READ_WRITE**. A conexão usa `ApplicationIntent=ReadOnly`, e **só são executados SELECTs em `sys.*`**.
- Credencial: linha 2 de `docs/credentials/DatabaseReadOnly.txt`. Tem `VIEW DEFINITION` em WMS, Reserva e ReservaNet. **msdb (jobs) continua negado.**
- Extrator reprodutível: `tools/db-extract/extract-catalog.ps1`. Saída em `extract/db-hml/<DB>/` (153 MB, fora do versionamento).

| DB | Módulos (.sql) | Objetos | Dependências | Sinônimos | Colunas | FKs |
|---|---|---|---|---|---|---|
| WMS | 406 | 952 | 2.205 | 186 | 3.982 | 327 |
| Reserva | 8.707 | 13.346 | 65.647 | 100 | 119.890 | 3.350 |
| ReservaNet | 110 | 367 | 667 | 81 | 1.213 | 86 |

Observações:
- 54 módulos do Reserva têm definição NULL (provavelmente `WITH ENCRYPTION`). Há uma pequena diferença entre as contagens de `sys.sql_modules` e os arquivos gravados (1 no WMS, cerca de 45 no Reserva), possivelmente por objetos `is_ms_shipped` ou colisão de nomes sem distinção de maiúsculas. Não é relevante agora.
- Os nomes de banco aparecem em caixas mistas (`Reserva`/`reserva`/`RESERVA`), então **é preciso normalizar** no grafo.
- Referências cross-DB que saem do WMS (diretas ou via sinônimo) vão para Reserva (cerca de 150 a 175 objetos do WMS), Audit, LinxFranquia, ReservaNet, Reserva_Integracao_Anymarket, TI_TEMP e até **`reserva_dsv`**, um provável resíduo de ambiente de dev na homologação.
- As referências cross-DB do Reserva vão para PITAGORAS_BD (1.248), Audit (403), rsv_integracao_arezzo (383), LinxFranquia (535), RESERVANET (220) etc.
- **Risco:** a homologação pode divergir da produção. Comparar `objects.csv` (HML) com o catálogo da réplica de produção, que também permite listar objetos e datas de modificação.
- **Pendência:** jobs do SQL Agent (msdb). É preciso `SQLAgentReaderRole` ou um export dos jobs feito pelo DBA.

## Produção via autenticação integrada (2026-09-24)
- Acesso: sessão `runas /netonly` com o usuário de domínio do Ivan (`RESERVA\...`), em `10.1.1.3` = **SRV-ALW01**, réplica secundária do AG **`RSV_AG`** (o outro nó é **SRV-BD**, provável primária; papel não confirmado sem `VIEW SERVER STATE`). Só SELECT em `sys.*` e `msdb`, `ApplicationIntent=ReadOnly`. Nenhuma credencial em arquivo é usada.
- Permissões efetivas: `VIEW ANY DEFINITION` no servidor + `db_datareader` nos 9 bancos abaixo e no `msdb`. **Sem** `VIEW SERVER STATE` e `VIEW DATABASE STATE` (DMVs de uso indisponíveis). Query Store **desligado em todos os bancos**. `Hub_Produtividade` sem acesso. O banco `pd` do pedido ao DBA **não existe** nesta instância.
- Extratores: `tools/db-extract/extract-catalog.ps1 -Server 10.1.1.3` e `tools/db-extract/extract-jobs.ps1`. Saída em `extract/db-prod/` (231 MB, fora do versionamento). Agora inclui `tables.csv` (nº de linhas por `sys.partitions`) e `indexes.csv`.

| DB | Tabelas | Views | Procs | Funções | Triggers | Sinônimos | Dependências | FKs | Módulos ilegíveis |
|---|---|---|---|---|---|---|---|---|---|
| WMS | 357 | 89 | 182 | 26 | 121 | 187 | 2.230 | 325 | 0 |
| Reserva | 4.533 | 2.024 | 3.801 | 784 | 2.164 | 100 | 65.964 | 3.356 | 43 |
| ReservaNet | 172 | 2 | 74 | 3 | 29 | 81 | 658 | 86 | 0 |
| WMSTASKS | 11 | 0 | 0 | 0 | 0 | 0 | 6 | 2 | 0 |
| WMS_Produtividade | 6 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Audit | 263 | 2 | 11 | 1 | 0 | 0 | 21 | 0 | 0 |
| Ecommerce | 33 | 1 | 7 | 1 | 6 | 0 | 25 | 19 | 0 |
| LinxFranquia | 2.128 | 931 | 1.250 | 458 | 1.196 | 0 | 28.459 | 3.007 | 74 |
| Reserva_Integracao_Anymarket | 33 | 14 | 15 | 0 | 10 | 1 | 263 | 13 | 0 |

### Jobs do SQL Agent (`extract/db-prod/_jobs/`)
- 494 jobs (321 habilitados), 1.520 passos: TSQL 1.507, SSIS 8, CmdExec 3, PowerShell 2. Sem `SSISDB` na instância. Passos por banco: Reserva 818, master 576, WMS 26, SistemasReserva 25, Monitoramento 21, outros.
- Comandos gravados com redação (`Password=`/`PWD=`, `-P`, `/DECRYPT` → `<redacted>`); varredura pós-extração sem ocorrência não redigida.
- Os jobs existem nos dois nós. O passo 1 chama `master.dbo.fn_hadr_group_is_primary N'RSV_AG'` e para o job fora da primária, por isso 285 aparecem como `canceled` aqui. **Definições valem; histórico real de execução está no SRV-BD.**
- 44 jobs tocam WMS, ReservaNet ou os fluxos de e-commerce/Intelipost (ex.: `RSV_WMS_FINALIZA_NF`, `RSV_POPULA_SIGLA_PEDIDO` a cada 1 min, `WMS - vwCrossdocking` e `VOLO_WMS_ATUALIZA_CAIXA_EMBALADA` a cada 3 min, `WMS_PROCESSA_FILA_ECOMMERCE`, `RSV_WMS_REPROCESSA_ENDERECAMENTO_PEDIDOS`). Nenhum deles aparece nos `edges.csv` dos repos: são arestas "banco → banco" que o mapa ainda não tem.
- Servidores vinculados: cerca de 300, a maioria lojas próprias e franquias (`RSV_*`, `FRQ_*`, `OFC_*`, `MINI_*`), mais `AUDIT`/`IntegrationHub` (`10.1.1.62\EMF`), `RSV_LEITURA` (a própria réplica) e um provedor Jet apontando para um `.xls` num perfil de usuário.

### Homologação × produção (`tools/db-extract/compare-catalogs.py` → `extract/diff-hml-prod/`)
| DB | Objetos HML | Objetos prod | Só HML | Só prod | Módulos comuns | Módulos diferentes |
|---|---|---|---|---|---|---|
| WMS | 952 | 962 | 26 | 36 | 396 | 14 |
| Reserva | 13.346 | 13.406 | 124 | 184 | 8.626 | 519 |
| ReservaNet | 367 | 361 | 6 | 0 | 108 | 10 |

- **WMS, só em HML:** schemas da ACL do AWX (`pedido.Pedidos`, `pedido.PedidosItem`, `Produtos.Produto`, `Recebimento.NotaFiscal*`), `dbo.ProdutosCup`, tabelas de devolução e-commerce novas. Ou seja, **a ACL do AWX sobre o WMS ainda não está em produção** (ou está com outro nome) `[unverified]`.
- **WMS, só em prod:** triggers de auditoria (`tr_*auditoria*`, `tr_usuario_*`, `tr_perfil_*`, `tr_notafiscal_*` em `dbo`), `dbo.NotaFiscal` como tabela (em HML é sinônimo), `Recebimento.vwTriangulacaoFiscal`, `prAtualizaCabecalhoPicking` (2026-08-05).
- **WMS, definição diferente:** 14 módulos, entre eles `vwPicking`, `vwEstoqueDisponivelEnderecado`, os triggers de `ItemProdutoPickingEcommerce` e `checkout.ObterDadosVolumeExpedicao`.

### Objetos citados pelos repos que não existem em produção
Cruzamento das 1.096 arestas de banco (WMS, Reserva, ReservaNet, WMS_Produtividade) do `edges-consolidado.csv` com `objects.csv` de prod:

| Objeto | Existe em HML | Repo |
|---|---|---|
| `WMS.pedido.Pedidos`, `PedidosItem`; `WMS.Produtos.Produto`; `WMS.Recebimento.NotaFiscal`, `NotaFiscalItem`, `NotaFiscalItemContagem`; `WMS.dbo.ProdutosCup` | sim | wms.awx.monorepo (Recebimento.NotaFiscal também servidor.backend) |
| `WMS.Produtos.CodigoBarraSku` | não | wms.awx.monorepo |
| `WMS.dbo.PainelEntrada`, `PedidoBloqueado`, `TipoCrossdockingTipoPedido`, `vwAuditoriaItem` | não | wms.servidor.backend |
| `ReservaNet.dbo.OndaEcommerce`, `PedidoOndaEcommerce`, `PecaPedidoOndaEcommerce` | não | wms.ecommerce.backend |
| `Reserva.dbo.pr_Cancelar_Pedido`, `pr_Cancelar_Pedido_Parcial`, `pr_RESERVANET_ECOMMERCE_PECA_PEDIDO`, `pr_RSV_ECOMMERCE_OBTER_ROMANEIO_EXPEDICAO_POR_LOTE_PRE_EXPEDICAO` | não | wms.ecommerce.backend |
| `Reserva.dbo.P_RSV_TRANSFERE_SOBRA_ESTOQUE` | não | wms.servidor.backend |
| `ReservaNet.dbo.AspNetUserRoles` | não | reserva-net.autenticacao.monolito |
| `ReservaNet.HangFireB2B.*` | não | reserva-net.b2b.backend (schema criado pelo Hangfire em runtime?) |

Cada um é código morto, feature não publicada, objeto em outro banco/servidor ou erro de extração do discovery `[unverified]`, a confirmar por repo.

### O que ainda falta
- DMVs de uso (procs/triggers/índices realmente executados) e histórico dos jobs no SRV-BD: **negados pelo DBA em 2026-09-24** (`VIEW SERVER STATE` e `msdb` considerados perigosos). Alternativas sem essas permissões na seção seguinte.
- `Hub_Produtividade`: segundo o usuário (2026-09-24), só tem tabelas, sem procs, views ou outros módulos. Continua sem acesso, então colunas e volumes não foram extraídos.
- Banco `pd`: **não existe** (confirmado pelo usuário em 2026-09-24); sai da lista.

### Uso real sem `VIEW SERVER STATE` (alternativas)
> **Premissa adotada (usuário, 2026-09-24): todo objeto existente em produção é considerado em uso.** As alternativas abaixo ficam só como referência. Não se aplica aos 22 objetos citados pelos repos que não existem em produção: esses continuam a confirmar.

1. **Snapshots de `sys.partitions`** na réplica (já permitido): o `tables.csv` de 2026-09-24 é o primeiro. Um segundo snapshot dias depois mostra quais tabelas crescem ou encolhem (INSERT/DELETE; UPDATE não aparece).
2. **Última atividade por tabela** com `db_datareader`: `MAX()` da coluna de data de criação/alteração de cada tabela. Só um agregado por tabela, sem linhas de negócio.
3. **Consulta executada pelo DBA** no SRV-BD (**não realizada**: o DBA respondeu que a informação não existe no ambiente; o usuário decidiu seguir sem a visão de uso em 2026-09-24; pedido em `docs/discovery/pedido-dba-consulta-uso.md`, script `tools/db-extract/dba-uso-primaria.sql`, compilado e seção de jobs testada na réplica), entregue como CSV: resumo de `sysjobhistory` e um snapshot de `sys.dm_exec_procedure_stats`/`dm_exec_trigger_stats`/`dm_db_index_usage_stats`. Não exige conceder permissão.
4. **Tabelas de log dos próprios sistemas** (bancos `Audit`, `Monitoramento`, tabelas `*_LOG`): já legíveis com `db_datareader`.
- **Limites das DMVs** (observação do DBA, 2026-09-24, e comportamento documentado do SQL Server): `dm_exec_procedure_stats`/`trigger_stats` só listam o que está no plan cache, então ausência não prova que o objeto está morto (só a presença prova uso). `dm_db_index_usage_stats` não depende do cache, mas zera em restart e failover do AG. `sysjobhistory` é tabela, limitada pela retenção do Agent (na réplica, cerca de 8 dias).
