# Pedido ao DBA: login somente leitura (2026-09-24)

**Assunto:** Pedido de login somente leitura para mapeamento das integrações do WMS via banco de dados

Olá,

Estamos mapeando como os sistemas do WMS se integram pelo banco de dados: quais tabelas, views, procs, triggers, functions e jobs cada sistema usa, e com que frequência. Para isso, preciso de **um login novo, somente leitura**, nas instâncias de produção: a **primária** do AlwaysOn e a **réplica read-only** (`10.1.1.3`).

O acesso é só para consulta. Não será executada nenhuma proc e não haverá nenhuma escrita ou alteração de objeto. Por isso, **não** preciso de `EXECUTE`, `db_datawriter`, `db_owner`, `ALTER` nem `sysadmin`.

## 1. Permissão de servidor

| Permissão | Justificativa |
|---|---|
| `VIEW SERVER STATE` | Permite consultar as DMVs de execução (`sys.dm_exec_procedure_stats`, `dm_exec_trigger_stats`, `dm_exec_function_stats`) e de uso de índices (`sys.dm_db_index_usage_stats`). Com elas é possível saber quais procs, triggers e functions de fato rodam, quando rodaram pela última vez e quais tabelas cada sistema lê e grava. Isso separa o que está em uso do que está morto. É leitura de estatísticas, sem acesso a dados de negócio, e precisa estar na primária, onde as escritas acontecem. |

## 2. Permissões por banco

Bancos: `WMS`, `Reserva`, `ReservaNet`, `WMSTASKS`, `WMS_Produtividade` e `pd`, que o WMS acessa diretamente, e `Audit`, `Ecommerce`, `LinxFranquia` e `Reserva_Integracao_Anymarket`, que o WMS acessa por sinônimos e procs.

| Permissão | Justificativa |
|---|---|
| role `db_datareader` | Consultar tabelas e views para entender o modelo de dados e confirmar como os sistemas usam cada tabela (por exemplo, status, filas em tabela e chaves de integração). |
| `VIEW DEFINITION` | Ler a estrutura (colunas, chaves, índices) e o código de views, procs, triggers, functions e sinônimos. A integração entre WMS e LINX acontece em boa parte dentro desses objetos, então é a permissão mais importante do pedido. Hoje ela só está disponível na homologação, que pode divergir da produção. |
| `VIEW DATABASE STATE` | Ler o Query Store, onde estiver ligado, com o histórico de execução de procs e queries. Esse histórico complementa as DMVs, que são zeradas quando a instância reinicia. |

## 3. Jobs do SQL Agent (`msdb`)

| Permissão | Justificativa |
|---|---|
| role `SQLAgentReaderRole` | Ver todos os jobs, as agendas e o histórico. Vários fluxos de integração com o LINX rodam em jobs. |
| role `db_datareader` | Consultar `sysjobs`, `sysjobsteps`, `sysjobhistory`, `sysjobactivity` e `sysschedules`, para ler o conteúdo de cada passo (qual proc ou script ele chama) e o resultado e a duração da última execução. A `SQLAgentReaderRole` sozinha não dá acesso ao texto dos passos. |

## 4. SSIS (`SSISDB`), se houver pacotes no catálogo

| Permissão | Justificativa |
|---|---|
| role `ssis_logreader` | Ver o histórico de execução dos pacotes chamados pelos jobs, para entender cargas e integrações feitas via SSIS. |

## Script sugerido (rodar na primária e na réplica)

```sql
USE master;
GRANT VIEW SERVER STATE TO [<login>];

-- Repetir para: WMS, Reserva, ReservaNet, WMSTASKS, WMS_Produtividade, pd,
--               Audit, Ecommerce, LinxFranquia, Reserva_Integracao_Anymarket
USE [WMS];
CREATE USER [<login>] FOR LOGIN [<login>];
ALTER ROLE db_datareader ADD MEMBER [<login>];
GRANT VIEW DEFINITION     TO [<login>];
GRANT VIEW DATABASE STATE TO [<login>];

USE msdb;
CREATE USER [<login>] FOR LOGIN [<login>];
ALTER ROLE SQLAgentReaderRole ADD MEMBER [<login>];
ALTER ROLE db_datareader      ADD MEMBER [<login>];

-- Somente se houver SSIS
USE SSISDB;
CREATE USER [<login>] FOR LOGIN [<login>];
ALTER ROLE ssis_logreader ADD MEMBER [<login>];
```

Se possível, peço também que me informem em quais desses bancos o Query Store está ligado.

Obrigado!
