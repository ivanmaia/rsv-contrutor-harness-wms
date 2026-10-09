<#
Extrai metadados do catálogo do SQL Server (somente SELECT em sys.*), sem ler dados de negócio.
Saída por banco:
  modules/<TYPE>/<schema>.<name>.sql   definições de procs, views, funções e triggers
  objects.csv       todos os objetos de usuário
  dependencies.csv  sys.sql_expression_dependencies com o tipo do objeto referenciado resolvido
  synonyms.csv      sinônimos e o objeto base
  columns.csv       tabelas/views e suas colunas
  foreign_keys.csv  FKs
  tables.csv        tabelas com nº de linhas (sys.partitions, metadado) e data de modificação
  indexes.csv       índices e colunas-chave
Uso: pwsh tools/db-extract/extract-catalog.ps1 -CredLine 2 -Databases WMS,Reserva,ReservaNet -OutDir extract/db-hml
     pwsh tools/db-extract/extract-catalog.ps1 -Server 10.1.1.3 -Databases WMS,Reserva -OutDir extract/db-prod
     (-Server sem credencial = autenticação integrada do Windows; o arquivo de credenciais não é lido)
#>
param(
  [int]$CredLine = 2,
  [string[]]$Databases = @('WMS', 'Reserva', 'ReservaNet'),
  [string]$OutDir = 'extract/db-hml',
  [string]$CredFile = 'docs/credentials/DatabaseReadOnly.txt',
  [string]$Server
)
$ErrorActionPreference = 'Stop'
$Databases = $Databases -split ',' | ForEach-Object { $_.Trim() } | Where-Object { $_ }
Import-Module SqlServer

if ($Server) {
  $server = $Server
  $auth = @{}
} else {
  $conn = (Get-Content $CredFile)[$CredLine - 1]
  function Get-Part($keys) {
    foreach ($k in $keys) { if ($conn -match "(?i)(^|;)\s*$k\s*=\s*([^;]*)") { return $Matches[2] } }
  }
  $server = Get-Part @('Server', 'Data Source')
  $auth = @{ Username = (Get-Part @('User Id', 'User ID', 'UID')); Password = (Get-Part @('Password', 'PWD')) }
}

function Q($db, $sql) {
  Invoke-Sqlcmd -ServerInstance $server -Database $db @auth `
    -ApplicationIntent ReadOnly -TrustServerCertificate -MaxCharLength 2147483647 `
    -QueryTimeout 600 -Query $sql
}

$objectsSql = @"
SELECT s.name AS [schema], o.name, o.type, o.type_desc, o.create_date, o.modify_date,
       OBJECT_SCHEMA_NAME(o.parent_object_id) AS parent_schema, OBJECT_NAME(o.parent_object_id) AS parent_name
FROM sys.objects o JOIN sys.schemas s ON s.schema_id = o.schema_id
WHERE o.is_ms_shipped = 0 AND o.type IN ('U','V','P','FN','IF','TF','TR','SN')
"@
$modulesSql = @"
SELECT s.name AS [schema], o.name, RTRIM(o.type) AS type, m.definition
FROM sys.sql_modules m JOIN sys.objects o ON o.object_id = m.object_id
JOIN sys.schemas s ON s.schema_id = o.schema_id
WHERE o.is_ms_shipped = 0
"@
$depsSql = @"
SELECT OBJECT_SCHEMA_NAME(d.referencing_id) AS from_schema, OBJECT_NAME(d.referencing_id) AS from_name,
       RTRIM(ro.type) AS from_type,
       d.referenced_server_name AS to_server, d.referenced_database_name AS to_db,
       d.referenced_schema_name AS to_schema, d.referenced_entity_name AS to_name,
       RTRIM(tobj.type) AS to_type, d.is_caller_dependent, d.is_ambiguous
FROM sys.sql_expression_dependencies d
JOIN sys.objects ro ON ro.object_id = d.referencing_id
LEFT JOIN sys.objects tobj ON tobj.object_id = d.referenced_id
"@
$synSql = @"
SELECT s.name AS [schema], sy.name, sy.base_object_name,
       PARSENAME(sy.base_object_name,4) AS to_server, PARSENAME(sy.base_object_name,3) AS to_db,
       PARSENAME(sy.base_object_name,2) AS to_schema, PARSENAME(sy.base_object_name,1) AS to_name
FROM sys.synonyms sy JOIN sys.schemas s ON s.schema_id = sy.schema_id
"@
$colsSql = @"
SELECT s.name AS [schema], o.name AS [table], RTRIM(o.type) AS type, c.column_id, c.name AS [column],
       t.name AS data_type, c.max_length, c.is_nullable, c.is_identity
FROM sys.columns c JOIN sys.objects o ON o.object_id = c.object_id
JOIN sys.schemas s ON s.schema_id = o.schema_id JOIN sys.types t ON t.user_type_id = c.user_type_id
WHERE o.is_ms_shipped = 0 AND o.type IN ('U','V')
"@
$fkSql = @"
SELECT fk.name, OBJECT_SCHEMA_NAME(fk.parent_object_id) AS from_schema, OBJECT_NAME(fk.parent_object_id) AS from_table,
       OBJECT_SCHEMA_NAME(fk.referenced_object_id) AS to_schema, OBJECT_NAME(fk.referenced_object_id) AS to_table
FROM sys.foreign_keys fk
"@
$tablesSql = @"
SELECT s.name AS [schema], t.name, t.create_date, t.modify_date,
       (SELECT SUM(p.rows) FROM sys.partitions p WHERE p.object_id = t.object_id AND p.index_id IN (0,1)) AS row_count
FROM sys.tables t JOIN sys.schemas s ON s.schema_id = t.schema_id
WHERE t.is_ms_shipped = 0
"@
$indexesSql = @"
SELECT OBJECT_SCHEMA_NAME(i.object_id) AS [schema], OBJECT_NAME(i.object_id) AS [table], i.name, i.type_desc,
       i.is_primary_key, i.is_unique,
       STUFF((SELECT ',' + c.name FROM sys.index_columns ic JOIN sys.columns c ON c.object_id = ic.object_id AND c.column_id = ic.column_id
              WHERE ic.object_id = i.object_id AND ic.index_id = i.index_id AND ic.is_included_column = 0
              ORDER BY ic.key_ordinal FOR XML PATH('')), 1, 1, '') AS key_columns
FROM sys.indexes i JOIN sys.objects o ON o.object_id = i.object_id
WHERE o.is_ms_shipped = 0 AND o.type IN ('U','V') AND i.index_id > 0
"@

foreach ($db in $Databases) {
  $dir = Join-Path $OutDir $db
  New-Item -ItemType Directory -Force $dir | Out-Null
  Write-Host "== $db"

  Q $db $objectsSql | Select-Object schema, name, type, type_desc, create_date, modify_date, parent_schema, parent_name |
    Export-Csv (Join-Path $dir 'objects.csv') -NoTypeInformation -Encoding utf8
  Q $db $depsSql | Select-Object from_schema, from_name, from_type, to_server, to_db, to_schema, to_name, to_type, is_caller_dependent, is_ambiguous |
    Export-Csv (Join-Path $dir 'dependencies.csv') -NoTypeInformation -Encoding utf8
  Q $db $synSql | Select-Object schema, name, base_object_name, to_server, to_db, to_schema, to_name |
    Export-Csv (Join-Path $dir 'synonyms.csv') -NoTypeInformation -Encoding utf8
  Q $db $colsSql | Select-Object schema, table, type, column_id, column, data_type, max_length, is_nullable, is_identity |
    Export-Csv (Join-Path $dir 'columns.csv') -NoTypeInformation -Encoding utf8
  Q $db $fkSql | Select-Object name, from_schema, from_table, to_schema, to_table |
    Export-Csv (Join-Path $dir 'foreign_keys.csv') -NoTypeInformation -Encoding utf8
  Q $db $tablesSql | Select-Object schema, name, create_date, modify_date, row_count |
    Export-Csv (Join-Path $dir 'tables.csv') -NoTypeInformation -Encoding utf8
  Q $db $indexesSql | Select-Object schema, table, name, type_desc, is_primary_key, is_unique, key_columns |
    Export-Csv (Join-Path $dir 'indexes.csv') -NoTypeInformation -Encoding utf8

  $n = 0; $nulls = 0
  foreach ($m in (Q $db $modulesSql)) {
    if ($m.definition -is [DBNull]) { $nulls++; continue }
    $tdir = Join-Path $dir "modules/$($m.type)"
    New-Item -ItemType Directory -Force $tdir | Out-Null
    $file = ("$($m.schema).$($m.name)" -replace '[\\/:*?"<>|]', '_') + '.sql'
    [IO.File]::WriteAllText((Join-Path $tdir $file), $m.definition, [Text.UTF8Encoding]::new($false))
    $n++
  }
  Write-Host "   modules written: $n (null definitions: $nulls)"
}
