

```powershell
# ----------------- One-Paste PowerShell Git Workflow -----------------
# Behavior:
# - Clones or updates the repo
# - Ensures local 'main' is up to date
# - If BRANCH is provided, merges 'main' into BRANCH and pushes
# - Supports HTTPS or SSH
# - Auto-corrects accidental ".gitb" suffix

param(
  [string]$RawUrl = 'https://github.com/DICKY1987/CLI_RESTART.gitb',
  [string]$Branch = '',  # e.g. 'feature/simplified-25ops-convo-updates' or leave empty to only update main
  [ValidateSet('https','ssh')]
  [string]$Proto  = 'https'
)

$ErrorActionPreference = 'Stop'

function Exec([string]$cmd, [switch]$AllowFail) {
  Write-Host "→ $cmd" -ForegroundColor Cyan
  $global:LASTEXITCODE = 0
  & $env:COMSPEC /c $cmd 2>&1 | ForEach-Object { $_ }
  if (-not $AllowFail -and $LASTEXITCODE -ne 0) {
    throw "Command failed (code $LASTEXITCODE): $cmd"
  }
}

try {
  # --- Sanitize URL (handle accidental .gitb, ensure .git) ---
  $SanitizedUrl = if ($RawUrl -match 'gitb$') { $RawUrl -replace 'gitb$','git' } else { $RawUrl }
  if ($SanitizedUrl -notmatch '\.git$') { $SanitizedUrl = "$SanitizedUrl.git" }

  # --- Extract owner/repo (works for https or ssh forms) ---
  if ($SanitizedUrl -match 'github\.com[:/](.+?)(?:\.git)$') {
    $OwnerRepo = $Matches[1]  # e.g., DICKY1987/CLI_RESTART
  } else {
    throw "Could not parse owner/repo from URL: $SanitizedUrl"
  }

  $HttpsUrl = "https://github.com/$OwnerRepo.git"
  $SshUrl   = "git@github.com:$OwnerRepo.git"
  $RepoUrl  = if ($Proto -eq 'ssh') { $SshUrl } else { $HttpsUrl }
  $RepoName = ($OwnerRepo -split '/')[1]

  Write-Host "→ Using $Proto remote: $RepoUrl" -ForegroundColor Green
  Write-Host "→ Repo name: $RepoName" -ForegroundColor Green
  if ($Branch) { Write-Host "→ Target feature branch: $Branch" -ForegroundColor Green } else { Write-Host "→ No feature branch supplied; will only update 'main'." -ForegroundColor Yellow }

  # --- Ensure Git is available ---
  Exec "git --version"

  # --- Clone if needed ---
  if (-not (Test-Path -Path (Join-Path -Path (Get-Location) -ChildPath $RepoName))) {
    Write-Host "→ Cloning $RepoUrl ..." -ForegroundColor Green
    Exec "git clone `"$RepoUrl`" `"$RepoName`""
  }

  Set-Location -Path $RepoName

  # --- Normalize remote URL to chosen protocol ---
  Exec "git remote set-url origin `"$RepoUrl`""

  # --- Fetch all (prune) ---
  Exec "git fetch origin +refs/heads/*:refs/remotes/origin/* --prune"

  # --- Ensure local main exists and is up-to-date ---
  $hasMain = $false
  Exec "git rev-parse --verify main" -AllowFail
  if ($LASTEXITCODE -eq 0) {
    $hasMain = $true
    Exec "git checkout main"
  } else {
    Exec "git checkout -t origin/main"
  }

  Exec "git pull --ff-only origin main"

  # --- If no feature branch is provided, stop after updating main ---
  if (-not $Branch) {
    Write-Host ""
    Write-Host "✅ 'main' is up-to-date. Provide -Branch '<name>' to merge into a feature branch." -ForegroundColor Green
    return
  }

  # --- Checkout or create the feature branch ---
  Exec "git rev-parse --verify `"$Branch`"" -AllowFail
  if ($LASTEXITCODE -eq 0) {
    Exec "git checkout `"$Branch`""
  } else {
    # Check remote branch
    Exec "git ls-remote --exit-code --heads origin `"$Branch`"" -AllowFail
    if ($LASTEXITCODE -eq 0) {
      Exec "git checkout -t origin/`"$Branch`""
    } else {
      Write-Host "→ Remote branch not found; creating from main: $Branch" -ForegroundColor Yellow
      Exec "git checkout -b `"$Branch`" main"
    }
  }

  # --- Merge main into feature branch ---
  Exec "git merge --no-ff --no-edit main" -AllowFail
  if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Warning "⚠️  Merge conflicts detected."
    Write-Host   "   Resolve them, then run:" -ForegroundColor Yellow
    Write-Host   "     git add -A" -ForegroundColor Yellow
    Write-Host   "     git commit --no-edit" -ForegroundColor Yellow
    Write-Host   "     git push -u origin `"$Branch`"" -ForegroundColor Yellow
    Write-Host ""
    Write-Host   "Help: https://docs.github.com/en/get-started/using-git/resolving-merge-conflicts" -ForegroundColor DarkCyan
    exit 1
  }

  # --- Push the updated branch ---
  Exec "git push -u origin `"$Branch`""

  Write-Host ""
  Write-Host "✅ Done." -ForegroundColor Green
  Write-Host "   - Repo: $RepoUrl"
  Write-Host "   - Branch '$Branch' is merged with main and pushed."
}
catch {
  Write-Error $_
  exit 1
}
# ----------------- End -----------------
```

### How to run with your branch

If you want to merge `main` into `feature/simplified-25ops-convo-updates`:

1. Paste the script as-is, then run:

```powershell
& {
  $RawUrl = 'https://github.com/DICKY1987/CLI_RESTART.gitb'
  $Branch = 'feature/simplified-25ops-convo-updates'
  $Proto  = 'https'  # or 'ssh'
  <paste the script here again>
}
```

**OR**, easiest way:

* Edit the first three lines (`param(...)`) before you paste:

```powershell
param(
  [string]$RawUrl = 'https://github.com/DICKY1987/CLI_RESTART.gitb',
  [string]$Branch = 'feature/simplified-25ops-convo-updates',
  [ValidateSet('https','ssh')]
  [string]$Proto  = 'https'
)
```

…then paste the whole thing and hit Enter.

If anything else breaks, copy the exact red error text and I’ll tweak it.
