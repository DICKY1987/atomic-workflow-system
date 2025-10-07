# =====================================================================
# One-shot Rollback Cleanup + Automation Installer (Windows PowerShell 7+)
# - Deletes local+remote rollback branches (rollback/… and rollback-…)
# - Fixes rollback naming to dash-style (rollback-YYYYMMDD_HHMMSS)
# - Installs a cleanup GitHub Action + PS script
# - Commits, pushes, and (optional) opens a PR via GitHub API
# - Writes detailed report JSON & text into repo root
# =====================================================================

param(
  [string]$RepoPath = ".",
  [string]$BaseBranch = "main",
  [string]$GitRemote  = "origin",
  [switch]$SkipNamingFix,
  [switch]$SkipAutomation,
  [string]$PrTitle = "Fix rollback branch naming and automate cleanup",
  [string]$PrBody  = "This PR fixes rollback branch naming (dash-style) and adds a cleanup workflow to delete any rollback branches automatically after merges.",
  [string]$GitUserName,
  [string]$GitUserEmail,
  [string]$GitHubToken,                 # optional, to open PR automatically
  [string]$GitHubRepo                   # optional, e.g. DICKY1987/Atomic (auto-detected if omitted)
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$PSNativeCommandUseErrorActionPreference = $true

# ---------- Helpers ----------

function New-Report {
  [ordered]@{
    started_at   = (Get-Date).ToUniversalTime().ToString("o")
    repo_path    = $RepoPath
    base_branch  = $BaseBranch
    remote       = $GitRemote
    steps        = @()
    summary      = $null
    completed_at = $null
  }
}

function Add-ReportStep {
  param([string]$name, [string]$status, [hashtable]$data)
  $REPORT.steps += [ordered]@{
    name   = $name
    status = $status
    data   = $data
    ts     = (Get-Date).ToUniversalTime().ToString("o")
  }
}

function Fail-Step {
  param($Name, $Ex)
  Add-ReportStep -name $Name -status "error" -data (@{ message=$Ex.Exception.Message; type=$Ex.GetType().FullName; stack=$Ex.ScriptStackTrace })
  throw $Ex
}

function Invoke-Git {
  param([Parameter(ValueFromRemainingArguments=$true)][string[]]$Args)
  $o = & git @Args 2>&1
  if ($LASTEXITCODE -ne 0) { throw "git $($Args -join ' ') failed [$LASTEXITCODE]`n$($o -join [Environment]::NewLine)" }
  $o -join "`n"
}

function Ensure-InRepo {
  if (-not (Test-Path -LiteralPath $RepoPath)) { throw "RepoPath not found: $RepoPath" }
  Set-Location -LiteralPath $RepoPath
  if (-not (Test-Path ".git")) { throw "This folder is not a git repository: $((Resolve-Path .).Path)" }
}

function Get-RemoteRepoFullName {
  param([string]$Remote)
  $url = Invoke-Git remote get-url $Remote
  if ($url -match 'github\.com[:/](?<owner>[^/]+)/(?<repo>[^/\.]+)') {
    return "$($Matches.owner)/$($Matches.repo)"
  }
  return $null
}

function Safe-WriteText([string]$Path, [string]$Content) {
  $dir = Split-Path -Parent $Path
  if ($dir -and -not (Test-Path $dir)) { New-Item -ItemType Directory -Path $dir | Out-Null }
  $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
  [System.IO.File]::WriteAllText($Path, $Content, $utf8NoBom)
}

# ---------- Start transcript (optional) ----------
try {
  Start-Transcript -Path ".\rollback_cleanup_transcript_$(Get-Date -Format 'yyyyMMdd_HHmmss').txt" -ErrorAction SilentlyContinue | Out-Null
} catch {}

# ---------- Step 1: Enter repo & sync ----------
Ensure-InRepo
$REPORT = New-Report
try {
  $syncOut = Invoke-Git fetch --all --prune
  Invoke-Git checkout $BaseBranch | Out-Null
  try {
    Invoke-Git pull --ff-only $GitRemote $BaseBranch | Out-Null
  } catch {
    Invoke-Git pull --rebase $GitRemote $BaseBranch | Out-Null
  }
  Add-ReportStep "sync" "ok" @{ output=$syncOut }
} catch { Fail-Step "sync" $_ }

# ---------- Step 2: Gather and delete rollback branches ----------
$localDeleted = @(); $remoteDeleted = @(); $localList = @(); $remoteList = @()
try {
  # local
  $localList = (& git branch --list "rollback*") | ForEach-Object { $_.Trim().Trim('*').Trim() } | Where-Object {$_}
  foreach ($b in $localList) {
    Invoke-Git branch -D $b | Out-Null
    $localDeleted += $b
  }

  # remote — dynamic remote name
  $rx = '^\s*{0}/rollback[/-]' -f ([regex]::Escape($GitRemote))
  $remoteRaw = (& git branch -r)
  $remoteList = $remoteRaw | Where-Object { $_ -match $rx } | ForEach-Object {
    ($_.Trim() -replace "^\s*${([regex]::Escape($GitRemote))}/",'').Trim()
  }
  foreach ($rb in $remoteList) {
    Invoke-Git push $GitRemote --delete $rb | Out-Null
    $remoteDeleted += $rb
  }

  Invoke-Git remote prune $GitRemote | Out-Null

  Add-ReportStep "cleanup.rollback.branches" "ok" @{
    local_found   = $localList
    local_deleted = $localDeleted
    remote_found  = $remoteList
    remote_deleted= $remoteDeleted
  }
} catch { Fail-Step "cleanup.rollback.branches" $_ }

# ---------- Step 3: Fix naming in gh_rollback workflow (optional) ----------
$modifiedFiles = @()
if (-not $SkipNamingFix) {
  try {
    $yamlPath = Join-Path (Get-Location) ".github/workflows/gh_rollback.yaml"
    if (Test-Path $yamlPath) {
      $orig = Get-Content $yamlPath -Raw
      $fixed = $orig `
        -replace 'rollback/\$\{\{\s*env\.TIMESTAMP\s*\}\}', 'rollback-${{ env.TIMESTAMP }}' `
        -replace 'rollback/\$\{TIMESTAMP\}', 'rollback-${TIMESTAMP}' `
        -replace 'rollback/\$\{timestamp\}', 'rollback-${timestamp}' `
        -replace 'rollback/(\$\(date[^)]*\))', 'rollback-$1'
      if ($fixed -ne $orig) {
        Safe-WriteText $yamlPath $fixed
        $modifiedFiles += $yamlPath
        Add-ReportStep "fix.naming" "ok" @{ file=$yamlPath; changed=$true }
      } else {
        Add-ReportStep "fix.naming" "ok" @{ file=$yamlPath; changed=$false }
      }
    } else {
      Add-ReportStep "fix.naming" "skipped" @{ reason="file not found"; path=$yamlPath }
    }
  } catch { Fail-Step "fix.naming" $_ }
} else {
  Add-ReportStep "fix.naming" "skipped" @{ reason="SkipNamingFix flag" }
}

# ---------- Step 4: Install auto-cleanup (optional) ----------
$branchName = "fix-rollback-cleanup-{0}" -f (Get-Date).ToUniversalTime().ToString("yyyyMMdd-HHmmss")
$createdFiles = @()
if (-not $SkipAutomation) {
  try {
    # script
    $scriptPath = Join-Path (Get-Location) "scripts/cleanup-rollback-branches.ps1"
    $scriptBody = @'
param([switch]$UseGh = $false, [string]$Repo = $env:GITHUB_REPOSITORY)
$ErrorActionPreference = 'Stop'
$PSNativeCommandUseErrorActionPreference = $true

function Delete-With-Git {
  git fetch --all --prune | Out-Null
  $branches = git branch -r | Select-String -Pattern '^\s*origin/rollback[/-]' | ForEach-Object {
    ($_.Line -replace '^\s*origin/','').Trim()
  }
  foreach ($b in $branches) {
    Write-Host "Deleting (git) $b"
    git push origin --delete $b
  }
}

function Delete-With-Gh {
  if (-not $Repo) { throw "Repo not set. Pass -Repo or set GITHUB_REPOSITORY." }
  $list = gh api "repos/$Repo/branches" --paginate --jq '.[].name' 2>$null
  if (-not $list) { return }
  $targets = $list | Where-Object { $_ -match '^rollback[/-]' }
  foreach ($b in $targets) {
    $ref = "heads/{0}" -f [uri]::EscapeDataString($b)
    Write-Host "Deleting (gh) $b"
    gh api -X DELETE "repos/$Repo/git/refs/$ref"
  }
}

if ($UseGh) { Delete-With-Gh } else { Delete-With-Git }
'@
    Safe-WriteText $scriptPath $scriptBody
    $createdFiles += $scriptPath

    # workflow
    $wfPath = Join-Path (Get-Location) ".github/workflows/cleanup-rollback-branches.yml"
    $wfBody = @'
name: Cleanup rollback branches
on:
  push:
    branches: [ main ]
  workflow_dispatch: {}

permissions:
  contents: write

jobs:
  cleanup:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 1

      - name: Delete rollback branches (gh)
        env:
          GITHUB_TOKEN: ${{ github.token }}
          GITHUB_REPOSITORY: ${{ github.repository }}
        shell: pwsh
        run: |
          Set-StrictMode -Version Latest
          $PSNativeCommandUseErrorActionPreference = $true
          ./scripts/cleanup-rollback-branches.ps1 -UseGh -Repo "$env:GITHUB_REPOSITORY"
'@
    Safe-WriteText $wfPath $wfBody
    $createdFiles += $wfPath

    Add-ReportStep "install.automation" "ok" @{ files=$createdFiles }
  } catch { Fail-Step "install.automation" $_ }
} else {
  Add-ReportStep "install.automation" "skipped" @{ reason="SkipAutomation flag" }
}

# ---------- Step 5: Commit, push, and (optional) open PR ----------
$prUrl = $null
try {
  if ($GitUserName) { Invoke-Git config user.name $GitUserName | Out-Null }
  if ($GitUserEmail) { Invoke-Git config user.email $GitUserEmail | Out-Null }

  Invoke-Git checkout -b $branchName | Out-Null

  $toStage = @()
  $toStage += $modifiedFiles
  $toStage += $createdFiles
  $toStage = $toStage | Where-Object { $_ -and (Test-Path $_) } | Sort-Object -Unique

  if ($toStage.Count -gt 0) {
    Invoke-Git add -- $toStage
    Invoke-Git commit -m "Fix rollback naming & add rollback cleanup workflow"
    Invoke-Git push -u $GitRemote $branchName
  }

  if (-not $GitHubRepo) { $GitHubRepo = Get-RemoteRepoFullName -Remote $GitRemote }
  if ($GitHubToken -and $GitHubRepo -and $toStage.Count -gt 0) {
    $body = @{
      title = $PrTitle
      head  = $branchName
      base  = $BaseBranch
      body  = $PrBody
      maintainer_can_modify = $true
      draft = $false
    } | ConvertTo-Json -Depth 5

    $headers = @{
      Authorization = "token $GitHubToken"
      "User-Agent"  = "rollback-cleanup-script"
      Accept        = "application/vnd.github+json"
    }
    $resp = Invoke-RestMethod -Method Post -Uri "https://api.github.com/repos/$GitHubRepo/pulls" -Headers $headers -ContentType 'application/json' -Body $body
    $prUrl = $resp.html_url
  }

  Add-ReportStep "commit.push.pr" "ok" @{
    branch_created = $branchName
    files_staged   = $toStage
    pr_url         = $prUrl
  }
} catch { Fail-Step "commit.push.pr" $_ }

# ---------- Final summary & report ----------
$REPORT.completed_at = (Get-Date).ToUniversalTime().ToString("o")
$REPORT.summary = [ordered]@{
  local_found     = $localList
  local_deleted   = $localDeleted
  remote_found    = $remoteList
  remote_deleted  = $remoteDeleted
  files_modified  = $modifiedFiles
  files_created   = $createdFiles
  branch_created  = $branchName
  pr_url          = $prUrl
}

$ts = (Get-Date).ToUniversalTime().ToString("yyyyMMdd_HHmmss")
$jsonPath = "rollback_cleanup_report_$ts.json"
$txtPath  = "rollback_cleanup_report_$ts.txt"
$REPORT | ConvertTo-Json -Depth 8 | Out-File -FilePath $jsonPath -Encoding utf8

$lines = @()
$lines += "Rollback Cleanup & Automation Report  [$($REPORT.started_at) → $($REPORT.completed_at)]"
$lines += "Repo: $($REPORT.repo_path)"
$lines += "Base branch: $BaseBranch  Remote: $GitRemote"
$lines += ""
foreach ($s in $REPORT.steps) {
  $lines += "- [$($s.status)] $($s.name)"
}
$lines += ""
$lines += "Local rollback found : $($REPORT.summary.local_found.Count)  → deleted: $($REPORT.summary.local_deleted.Count)"
$lines += "Remote rollback found: $($REPORT.summary.remote_found.Count) → deleted: $($REPORT.summary.remote_deleted.Count)"
if ($REPORT.summary.files_modified.Count -gt 0) { $lines += "Files modified: $($REPORT.summary.files_modified -join ', ')" }
if ($REPORT.summary.files_created.Count  -gt 0) { $lines += "Files created : $($REPORT.summary.files_created -join ', ')" }
$lines += "Branch created: $($REPORT.summary.branch_created)"
if ($REPORT.summary.pr_url) { $lines += "PR: $($REPORT.summary.pr_url)" }
$lines -join [Environment]::NewLine | Out-File -FilePath $txtPath -Encoding utf8

Write-Host ""
Write-Host "==== DONE ====" -ForegroundColor Green
Write-Host "JSON report:" (Resolve-Path $jsonPath).Path
Write-Host "Text report:" (Resolve-Path $txtPath).Path
if ($prUrl) { Write-Host "Pull Request:" $prUrl }

# ---------- End transcript ----------
try { Stop-Transcript | Out-Null } catch {}
