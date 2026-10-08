param([string]$Message = '')
$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $repoRoot
$env:GIT_TERMINAL_PROMPT = '0'
$env:GCM_INTERACTIVE = 'Never'
function Invoke-RepoGit {
    param([string[]]$GitArgs)
    & git @GitArgs
    if ($LASTEXITCODE -ne 0) { throw "Git command failed: $($GitArgs -join ' ')" }
}
$syncDir = Join-Path $repoRoot '.sync'
New-Item -ItemType Directory -Path $syncDir -Force | Out-Null
$lock = $null
try {
    try { $lock = [System.IO.File]::Open((Join-Path $syncDir 'sync.lock'), 'OpenOrCreate', 'ReadWrite', 'None') }
    catch [System.IO.IOException] { Write-Output 'Another sync is running; skipped.'; exit 0 }
    $remote = & git remote get-url origin
    if ($LASTEXITCODE -ne 0 -or $remote -ne 'https://github.com/zyanzhi90-dot/open-project-for-fund.git') { throw 'Unexpected origin; sync stopped.' }
    $branch = & git branch --show-current
    if ($LASTEXITCODE -ne 0 -or $branch -ne 'main') { throw 'Expected main branch; sync stopped.' }
    Invoke-RepoGit -GitArgs @('fetch', 'origin')
    & git show-ref --verify --quiet refs/remotes/origin/main
    if ($LASTEXITCODE -eq 0) {
        & git merge-base --is-ancestor origin/main HEAD
        if ($LASTEXITCODE -ne 0) { throw 'Remote has changes not in local history. Sync stopped; reconcile manually without force push.' }
    }
    Invoke-RepoGit -GitArgs @('add', '--all')
    & git diff --cached --quiet
    $diffCode = $LASTEXITCODE
    if ($diffCode -eq 1) {
        if (-not $Message) { $Message = 'Sync project updates ' + [DateTimeOffset]::Now.ToString('yyyy-MM-dd HH:mm:ss zzz') }
        Invoke-RepoGit -GitArgs @('commit', '--quiet', '-m', $Message)
    } elseif ($diffCode -ne 0) { throw 'Could not inspect staged changes.' }
    Invoke-RepoGit -GitArgs @('push', '-u', 'origin', 'main')
    Write-Output 'GitHub sync completed.'
} finally {
    if ($lock) { $lock.Dispose() }
}
