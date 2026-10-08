$ErrorActionPreference='Stop'
$taskWord = New-Object -ComObject Word.Application
$taskWord.Visible = $false
$taskWord.DisplayAlerts = 0
$taskWord.AutomationSecurity = 3
try {
  Get-ChildItem -LiteralPath (Join-Path $PSScriptRoot 'attachments') -Filter '*.doc' | ForEach-Object {
    $taskDoc=$null
    try {
      $taskDoc=$taskWord.Documents.Open($_.FullName,$false,$true,$false)
      $taskText=$taskDoc.Content.Text
      [IO.File]::WriteAllText([IO.Path]::ChangeExtension($_.FullName,'.txt'),$taskText,[Text.UTF8Encoding]::new($false))
      Write-Output ('READ '+$_.Name+' '+$taskText.Length)
    } catch {Write-Output ('FAIL '+$_.Name+' '+$_.Exception.Message)}
    finally {if($null -ne $taskDoc){$taskDoc.Close(0)}}
  }
} finally {$taskWord.Quit();[Runtime.InteropServices.Marshal]::ReleaseComObject($taskWord) | Out-Null}
