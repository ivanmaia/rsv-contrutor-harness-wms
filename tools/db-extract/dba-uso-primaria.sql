/*
Uso real dos objetos dos bancos do WMS. Rodar na primária do AG (SRV-BD).
Somente SELECT. Sem texto de query, parâmetros ou dados de negócio: só nomes, contadores e datas.
  sqlcmd -S SRV-BD -E -W -s "|" -i dba-uso-primaria.sql -o uso-primaria.txt
*/
SET NOCOUNT ON;

/* 1. Procs e triggers executados */
SELECT DB_NAME(database_id) AS db, OBJECT_SCHEMA_NAME(object_id, database_id) AS [schema],
       OBJECT_NAME(object_id, database_id) AS nome, 'P' AS tipo, execution_count, last_execution_time
FROM sys.dm_exec_procedure_stats
WHERE DB_NAME(database_id) IN ('WMS', 'Reserva', 'ReservaNet', 'WMSTASKS', 'WMS_Produtividade', 'Hub_Produtividade',
                               'Audit', 'Ecommerce', 'LinxFranquia', 'Reserva_Integracao_Anymarket')
UNION ALL
SELECT DB_NAME(database_id), OBJECT_SCHEMA_NAME(object_id, database_id),
       OBJECT_NAME(object_id, database_id), 'TR', execution_count, last_execution_time
FROM sys.dm_exec_trigger_stats
WHERE DB_NAME(database_id) IN ('WMS', 'Reserva', 'ReservaNet', 'WMSTASKS', 'WMS_Produtividade', 'Hub_Produtividade',
                               'Audit', 'Ecommerce', 'LinxFranquia', 'Reserva_Integracao_Anymarket');

/* 2. Tabelas lidas e escritas */
SELECT DB_NAME(database_id) AS db, OBJECT_SCHEMA_NAME(object_id, database_id) AS [schema],
       OBJECT_NAME(object_id, database_id) AS tabela,
       SUM(user_seeks + user_scans + user_lookups) AS leituras, SUM(user_updates) AS escritas,
       MAX(last_user_update) AS ultima_escrita
FROM sys.dm_db_index_usage_stats
WHERE DB_NAME(database_id) IN ('WMS', 'Reserva', 'ReservaNet', 'WMSTASKS', 'WMS_Produtividade', 'Hub_Produtividade',
                               'Audit', 'Ecommerce', 'LinxFranquia', 'Reserva_Integracao_Anymarket')
GROUP BY database_id, object_id;

/* 3. Última execução de cada job */
SELECT j.name AS job, COUNT(h.instance_id) AS execucoes, SUM(CASE WHEN h.run_status = 0 THEN 1 ELSE 0 END) AS falhas,
       MAX(h.run_date) AS ultima_execucao_yyyymmdd
FROM msdb.dbo.sysjobs j
LEFT JOIN msdb.dbo.sysjobhistory h ON h.job_id = j.job_id AND h.step_id = 0
GROUP BY j.name;
