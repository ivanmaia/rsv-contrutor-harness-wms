<#
Extrai os jobs do SQL Agent (msdb) com SELECT, sem executar nada.
Saída:
  jobs.csv          jobs, dono, categoria, agenda e resultado da última execução
  steps.csv         passos (subsystem, banco, primeira linha do comando)
  steps/<job>/<n>.txt  comando completo de cada passo
Comandos passam por redação: Password=/PWD=, -P de sqlcmd/bcp e /DECRYPT viram <redacted>.
Uso: pwsh tools/db-extract/extract-jobs.ps1 -Server 10.1.1.3 -OutDir extract/db-prod/_jobs
     (autenticação integrada do Windows)
#>
param(
  [Parameter(Mandatory)][string]$Server,
  [string]$OutDir = 'extract/db-prod/_jobs'
)
$ErrorActionPreference = 'Stop'
Import-Module SqlServer

function Q($sql) {
  Invoke-Sqlcmd -ServerInstance $Server -Database msdb -ApplicationIntent ReadOnly -TrustServerCertificate `
    -MaxCharLength 2147483647 -QueryTimeout 600 -Query $sql
}
function Redact([string]$t) {
  $t = $t -replace '(?i)((password|pwd)\s*=\s*)("[^"]*"|''[^'']*''|[^;"''\s]+)', '$1<redacted>'
  $t = $t -replace '(?<=\s)-P\s*("[^"]*"|\S+)', '-P <redacted>'
  $t -replace '(?i)(/DECRYPT\s+)("[^"]*"|\S+)', '$1<redacted>'
}

$jobsSql = @"
SELECT j.name AS job, j.enabled, SUSER_SNAME(j.owner_sid) AS owner, c.name AS category, j.description,
       j.date_created, j.date_modified,
       STUFF((SELECT '; ' + s.name + ' [' +
                CASE s.freq_type WHEN 1 THEN 'once' WHEN 4 THEN 'daily' WHEN 8 THEN 'weekly' WHEN 16 THEN 'monthly'
                  WHEN 32 THEN 'monthly-rel' WHEN 64 THEN 'agent-start' WHEN 128 THEN 'idle' ELSE CAST(s.freq_type AS varchar) END
                + CASE s.freq_subday_type WHEN 2 THEN ' every ' + CAST(s.freq_subday_interval AS varchar) + 's'
                  WHEN 4 THEN ' every ' + CAST(s.freq_subday_interval AS varchar) + 'min'
                  WHEN 8 THEN ' every ' + CAST(s.freq_subday_interval AS varchar) + 'h' ELSE '' END
                + ' from ' + CAST(s.active_start_time AS varchar) + CASE s.enabled WHEN 0 THEN ' DISABLED' ELSE '' END + ']'
              FROM dbo.sysjobschedules js JOIN dbo.sysschedules s ON s.schedule_id = js.schedule_id
              WHERE js.job_id = j.job_id FOR XML PATH('')), 1, 2, '') AS schedules,
       h.run_date AS last_run_date, h.run_time AS last_run_time, h.run_duration AS last_run_duration,
       CASE h.run_status WHEN 0 THEN 'failed' WHEN 1 THEN 'succeeded' WHEN 2 THEN 'retry' WHEN 3 THEN 'canceled' END AS last_run_status
FROM dbo.sysjobs j
LEFT JOIN dbo.syscategories c ON c.category_id = j.category_id
OUTER APPLY (SELECT TOP 1 run_date, run_time, run_duration, run_status FROM dbo.sysjobhistory
             WHERE job_id = j.job_id AND step_id = 0 ORDER BY instance_id DESC) h
"@
$stepsSql = @"
SELECT j.name AS job, s.step_id, s.step_name, s.subsystem, s.database_name, s.command,
       s.on_success_action, s.on_fail_action, s.last_run_date, s.last_run_outcome
FROM dbo.sysjobsteps s JOIN dbo.sysjobs j ON j.job_id = s.job_id
ORDER BY j.name, s.step_id
"@

New-Item -ItemType Directory -Force $OutDir | Out-Null
Q $jobsSql | Select-Object job, enabled, owner, category, description, date_created, date_modified, schedules,
  last_run_date, last_run_time, last_run_duration, last_run_status |
  Export-Csv (Join-Path $OutDir 'jobs.csv') -NoTypeInformation -Encoding utf8

$rows = foreach ($s in (Q $stepsSql)) {
  $cmd = if ($s.command -is [DBNull]) { '' } else { Redact $s.command }
  $jdir = Join-Path $OutDir ('steps/' + ($s.job -replace '[\\/:*?"<>|]', '_'))
  New-Item -ItemType Directory -Force $jdir | Out-Null
  [IO.File]::WriteAllText((Join-Path $jdir "$($s.step_id).txt"), $cmd, [Text.UTF8Encoding]::new($false))
  [pscustomobject]@{
    job = $s.job; step_id = $s.step_id; step_name = $s.step_name; subsystem = $s.subsystem
    database_name = $s.database_name; first_line = (($cmd -split "`n" | Where-Object { $_.Trim() } | Select-Object -First 1) -as [string]).Trim()
    on_success_action = $s.on_success_action; on_fail_action = $s.on_fail_action
    last_run_date = $s.last_run_date; last_run_outcome = $s.last_run_outcome
  }
}
$rows | Export-Csv (Join-Path $OutDir 'steps.csv') -NoTypeInformation -Encoding utf8
Write-Host "jobs/steps written: $(@($rows).Count) steps"
