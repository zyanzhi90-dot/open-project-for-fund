$ErrorActionPreference='Stop'
$projectRoot=Split-Path -Parent (Split-Path -Parent (Split-Path -Parent $PSScriptRoot))
Set-Location -LiteralPath $projectRoot
$pythonExe='C:\Users\user\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $pythonExe -X utf8 -c "from pathlib import Path; import hashlib; p=Path('全国机器人开放课题_个人申报台账_分类排序调整版_20261010.xlsx'); assert hashlib.sha256(p.read_bytes()).hexdigest()=='3bf68318f901d401c1d0bca3ec15e1044e6fa2b8c41891207b88f49e9c4dcb95', 'Old workbook changed; reassess before archival'"
if ($LASTEXITCODE -ne 0) { throw 'Source verification failed' }
$archiveDir=Join-Path $projectRoot '90_历史归档\02_旧版与输出记录\20261010_当前申报清理前'
New-Item -ItemType Directory -Path $archiveDir -Force | Out-Null
Move-Item -LiteralPath (Join-Path $projectRoot '全国机器人开放课题_个人申报台账_分类排序调整版_20261010.xlsx') -Destination $archiveDir
Move-Item -LiteralPath (Join-Path $PSScriptRoot '全国机器人开放课题_个人申报台账_当前申报清理版_20261010.xlsx') -Destination $projectRoot
Remove-Item -LiteralPath (Join-Path $PSScriptRoot 'authored.xlsx')
& $pythonExe -X utf8 (Join-Path $PSScriptRoot 'update_delivery_docs.py')
if ($LASTEXITCODE -ne 0) { throw 'Delivery verification failed' }
