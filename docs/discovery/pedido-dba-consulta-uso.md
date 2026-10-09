# Pedido ao DBA: consulta de uso na primária (2026-09-24, versão reduzida)

**Assunto:** Consulta somente leitura na primária do AG para o mapeamento das integrações do WMS

Olá,

Reduzi a consulta ao mínimo. São 3 SELECTs, que só retornam nomes de objetos, contadores e datas dos bancos do WMS. Não trazem texto de query, parâmetros nem dados de negócio, e não alteram nem executam nada.

| # | Fonte | Colunas | Para quê |
|---|---|---|---|
| 1 | `sys.dm_exec_procedure_stats`, `sys.dm_exec_trigger_stats` | banco, objeto, nº de execuções, última execução | Separar procs e triggers em uso dos mortos |
| 2 | `sys.dm_db_index_usage_stats` | banco, tabela, nº de leituras e escritas, última escrita | Saber quais tabelas cada fluxo realmente lê e grava |
| 3 | `msdb.dbo.sysjobs` + `sysjobhistory` | job, nº de execuções, falhas, data da última execução | Saber quais jobs rodam de fato |

Arquivo em anexo: `dba-uso-primaria.sql`. Para rodar:

```
sqlcmd -S SRV-BD -E -W -s "|" -i dba-uso-primaria.sql -o uso-primaria.txt
```

Só preciso também da **data do último restart** da instância, que pode vir por texto mesmo. Sem ela, não consigo saber se um objeto "sem execução" está morto ou só não rodou desde o restart.

Obrigado!
