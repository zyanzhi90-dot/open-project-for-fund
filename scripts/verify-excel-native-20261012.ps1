$ErrorActionPreference = 'Stop'
$repoPath = Split-Path -Parent $PSScriptRoot
$sourcePath = Join-Path $repoPath '全国机器人开放课题_个人申报台账_检索补充版_20261010.xlsx'
$resultPath = Join-Path $repoPath '.sync/excel_20261012/全国机器人开放课题_个人申报台账_检索补充版_20261012.xlsx'
$inputPath = Join-Path $repoPath '.sync/excel_20261012/additions.json'
$inputData = Get-Content -LiteralPath $inputPath -Raw -Encoding UTF8 | ConvertFrom-Json
$app = $null
$original = $null
$result = $null
try {
    $app = New-Object -ComObject Excel.Application
    $app.Visible = $false
    $app.DisplayAlerts = $true
    $app.AskToUpdateLinks = $true
    $original = $app.Workbooks.Open($sourcePath, 0, $true)
    $result = $app.Workbooks.Open($resultPath, 0, $true)
    if ($result.Worksheets.Count -ne 4) { throw 'Sheet count changed' }
    $checked = 0
    for ($k = 1; $k -le 4; $k++) {
        $oldSheet = $original.Worksheets.Item($k)
        $newSheet = $result.Worksheets.Item($k)
        if ($oldSheet.Name -ne $newSheet.Name) { throw 'Sheet name changed' }
        $oldValues = $oldSheet.UsedRange.Value2
        $newValues = $newSheet.UsedRange.Value2
        for ($i = 1; $i -le $oldValues.GetLength(0); $i++) {
            $newRow = $i
            if ($k -eq 1 -and $i -gt 12) { $newRow += 2 }
            for ($j = 1; $j -le $oldValues.GetLength(1); $j++) {
                if ($oldValues[$i,$j] -cne $newValues[$newRow,$j]) { throw "Existing value changed: sheet $k row $i col $j" }
                $checked++
            }
        }
    }
    $detailSheet = $result.Worksheets.Item(3)
    for ($i = 0; $i -lt 2; $i++) {
        $newValues = $detailSheet.Range("A$(403+$i):AA$(403+$i)").Value2
        for ($j = 0; $j -lt 27; $j++) {
            if ($newValues[1,($j+1)] -cne $inputData.details[$i][$j]) { throw "Added value differs: addition $i column $j" }
        }
    }
    if ($result.Worksheets.Item(1).UsedRange.Rows.Count -ne 27) { throw 'Overview row count failed' }
    if ($detailSheet.UsedRange.Rows.Count -ne 404) { throw 'Details row count failed' }
    $report = [ordered]@{
        checked_at = '2026-10-12'
        display_alerts = $app.DisplayAlerts
        normal_open_without_repair_prompt = $true
        readonly = $result.ReadOnly
        all_original_values_equal = $true
        original_cells_checked = $checked
        additions_equal_input = $true
        original_headers_unchanged = $true
        overview_records = 26
        detail_records = 403
    }
    $reportPath = Join-Path $repoPath '02_检索与核验记录/第四步交叉补漏_20261011/main006_20261012/Excel原生打开校验.json'
    $report | ConvertTo-Json | Set-Content -LiteralPath $reportPath -Encoding UTF8
    Write-Output "Excel normal open with DisplayAlerts=true; $checked original values preserved; 2 additions match."
} finally {
    if ($null -ne $result) { $result.Close($false) }
    if ($null -ne $original) { $original.Close($false) }
    if ($null -ne $app) { $app.Quit(); [Runtime.InteropServices.Marshal]::FinalReleaseComObject($app) | Out-Null }
}
