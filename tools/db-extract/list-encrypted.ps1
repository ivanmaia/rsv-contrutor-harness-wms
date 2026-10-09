<#
Lista módulos (procs, views, funções, triggers) criptografados (WITH ENCRYPTION) — somente SELECT em sys.*.
Uso: pwsh tools/db-extract/list-encrypted.ps1 -CredLine 2 -Databases WMS,Reserva,ReservaNet
#>
param(
  [int]$CredLine = 2,
  [string[]]$Databases = @('WMS', 'Reserva', 'ReservaNet'),
  [string]$CredFile = 'docs/credentials/DatabaseReadOnly.txt'
)
$ErrorActionPreference = 'Stop'
$Databases = $Databases -split ',' | ForEach-Object { $_.Trim() } | Where-Object { $_ }
Import-Module SqlServer

$conn = (Get-Content $CredFile)[$CredLine - 1]
function Get-Part($keys) {
  foreach ($k in $keys) { if ($conn -match "(?i)(^|;)\s*$k\s*=\s*([^;]*)") { return $Matches[2] } }
}
$server = Get-Part @('Server', 'Data Source')
$user = Get-Part @('User Id', 'User ID', 'UID')
$pass = Get-Part @('Password', 'PWD')

$sql = @"
SELECT DB_NAME() AS db, s.name AS [schema], o.name, o.type_desc, o.create_date, o.modify_date,
       OBJECT_NAME(o.parent_object_id) AS parent
FROM sys.sql_modules m
JOIN sys.objects o ON o.object_id = m.object_id
JOIN sys.schemas s ON s.schema_id = o.schema_id
WHERE m.definition IS NULL AND OBJECTPROPERTY(o.object_id, 'IsEncrypted') = 1
ORDER BY o.type_desc, s.name, o.name
"@
foreach ($db in $Databases) {
  Invoke-Sqlcmd -ServerInstance $server -Database $db -Username $user -Password $pass `
    -ApplicationIntent ReadOnly -TrustServerCertificate -Query $sql |
    Select-Object db, schema, name, type_desc, create_date, modify_date, parent
}
