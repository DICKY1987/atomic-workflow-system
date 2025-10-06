<# 
PowerShell-Native Git Workflow (one-paste)

- Updates/creates a local clone
- Ensures `main` is up to date
- (Optional) Merges `main` into a feature branch and pushes it
- Works with HTTPS or SSH
- Auto-fixes accidental ".gitb" typo

USAGE EXAMPLES
--------------
# Just update main (no feature branch merge)
powershell -NoProfile -ExecutionPolicy Bypass -Command "& {
  [string]$RawUrl='https://github.com/DICKY1987/CLI_RESTART.gitb';
  [string]$Branch='';
  [string]$Proto='https';  # 'https' or 'ssh'
  <PASTE SCRIPT BODY HERE>
}"

# Merge main into a feature branch and push (HTTPS)
powershell -NoProfile -ExecutionPolicy Bypass -Command "& {
  [string]$RawUrl='https://github.com/DICKY1987/CLI_RESTART.gitb';
  [string]$Branch='feature/simplified-25ops-convo-updates';
  [string]$Proto='https';  # or 'ssh'
  <PASTE SCRIPT BODY HERE>
}"

# Merge main into a feature branch and push (SSH)
powershell -NoProfile -ExecutionPolicy Bypass -Command "& {
  [string]$RawUrl='https://github.com/DICKY1987/CLI_RESTART.gitb';
  [string]$Branch='feature/simplified-25ops-convo-updates';
  [string]$Proto='ssh';
  <PASTE SCRIPT BODY HERE>
}"
#> 

# --------------- SCRIPT BODY STARTS HERE ---------------
$ErrorActionPreference = 'Stop'

function Exec($cmd, [switch]$AllowFail) {
  Write-Host "→ $cmd" -ForegroundColor Cyan
  $global:LASTEXITCODE = 0
  & $env:COMSPEC /c $cmd 2>&1 | ForEach-Object {
    $_
  }
  if (-not $AllowFail -and $LASTEXITCODE -ne 0) {
    throw "Command failed (code $LASTEXITCODE): $cmd"
  }
}

try {
  # --- Inputs (allow inline variables if user set them before paste) ---
  if (-not (Get-Variable RawUrl -Scope 1 -ErrorAction SilentlyContinue)) { $RawUrl   = 'https://github.com/DICKY1987/CLI_RESTART.gitb' }
  if (-not (Get-Variable Branch -Scope 1 -ErrorAction SilentlyContinue)) { $Branch   = '' }
  if (-not (Get-Variable Proto  -Scope 1 -ErrorAction SilentlyContinue)) { $Proto    = 'https' } # 'https' | 'ssh'

  if ($Proto -notin @('https','ssh')) { throw "Proto must be 'https' or 'ssh' (got '$Proto')." }

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
  if ($Branch) { Write-Host "→ Target feature branch: $Branch" -ForegroundColor Green } else { Write-Host "→ No feature branch supplied; will only update main." -ForegroundColor Yellow }

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
  try {
    Exec "git rev-parse --verify main" -AllowFail
    if ($LASTEXITCODE -eq 0) { $hasMain = $true }
  } catch { $hasMain = $false }

  if (-not $hasMain) {
    # Create local main tracking origin/main
    Exec "git checkout -t origin/main"
  } else {
    Exec "git checkout main"
  }

  Exec "git pull --ff-only origin main"

  # --- If no feature branch is provided, stop after updating main ---
  if (-not $Branch) {
    Write-Host ""
    Write-Host "✅ main is up-to-date. To merge into a feature branch, rerun with a Branch value." -ForegroundColor Green
    return
  }

  # --- Checkout or create the feature branch ---
  $localBranchExists = $false
  try {
    Exec "git rev-parse --verify `"$Branch`"" -AllowFail
    if ($LASTEXITCODE -eq 0) { $localBranchExists = $true }
  } catch { $localBranchExists = $false }

  if ($localBranchExists) {
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

} catch {
  Write-Error $_
  exit 1
}
# --------------- SCRIPT BODY ENDS HERE ---------------
