$ErrorActionPreference = 'Stop'
$taskRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..\..\..')).Path
$taskData = Get-Content -LiteralPath (Join-Path $PSScriptRoot 'prepared_strict.json') -Encoding UTF8 -Raw | ConvertFrom-Json
$taskOldPath = $taskData.current_input
$taskExcel = [Runtime.InteropServices.Marshal]::GetActiveObject('Excel.Application')
$taskTarget = $null
foreach ($taskBook in $taskExcel.Workbooks) {
    if ($taskBook.FullName -eq $taskOldPath) { $taskTarget = $taskBook; break }
}
if (-not $taskTarget) { $taskTarget = [Runtime.InteropServices.Marshal]::BindToMoniker($taskOldPath) }
Write-Output ('Bound name: ' + $taskTarget.Name)
Write-Output ('Bound path: ' + $taskTarget.FullName)
if (-not $taskTarget -or $taskTarget.FullName -ne $taskOldPath) { throw 'Target workbook was not found in active Excel instance.' }
Write-Output ('Target saved: ' + $taskTarget.Saved)
if (-not $taskTarget.Saved) { throw 'Workbook has unsaved edits. It was left open.' }
$taskTarget.Close($false)
Write-Output 'Closed the saved prior workbook for archival. Other workbooks remain open.'
