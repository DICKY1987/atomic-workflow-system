
param(
  [Parameter(Mandatory=$false)][string]$Branch = $(git branch --show-current),
  [switch]$DryRun
)
$ErrorActionPreference = 'Stop'

function Invoke-Tool($cmd) {
  Write-Host ">> $cmd" -ForegroundColor DarkGray
  & powershell -NoProfile -Command $cmd
  if ($LASTEXITCODE -ne 0) { throw "Command failed: $cmd" }
}

git fetch --all --prune | Out-Null
if (-not $Branch) { $Branch = "$(git branch --show-current)" }

if ($DryRun) {
  Write-Host "Dry-run: would rebase $Branch onto origin/main and apply policies" -ForegroundColor Yellow
  exit 0
}

git checkout $Branch | Out-Null

# Enable rerere (remember conflict resolutions)
git config rerere.enabled true
git config rerere.autoupdate true

# Try to rebase onto main (linear history)
$rebaseOk = $true
try {
  git rebase origin/main
} catch {
  $rebaseOk = $false
}

if (-not $rebaseOk) {
  Write-Host "Attempting deterministic conflict resolution..." -ForegroundColor Cyan

  # First pass: rerere may already fix it
  try { git rebase --continue } catch {}

  if ($LASTEXITCODE -ne 0) {
    # Fallback rules by common generated areas
    git checkout --theirs -- '**/dist/**' '**/build/**' 'package-lock.json' 'poetry.lock' 2>$null
    git add -A

    # Normalize to reduce spurious diffs
    try { pre-commit run --all-files 2>$null | Out-Null } catch {}

    git add -A
    try { git rebase --continue } catch {}
  }
}

# Post-merge verification gates
$failed = $false
function Run-OrFail($label, $cmd) {
  Write-Host "Gate: $label" -ForegroundColor Cyan
  $proc = Start-Process -FilePath "powershell" -ArgumentList "-NoProfile","-Command",$cmd -PassThru -WindowStyle Hidden -Wait
  if ($proc.ExitCode -ne 0) {
    Write-Warning "$label failed"
    $script:failed = $true
  }
}

# JSON Schema validate if schema exists
if (Test-Path ".\schemas\config.schema.json") {
  Get-ChildItem -Path "config" -Recurse -Filter "*.json" -ErrorAction SilentlyContinue | ForEach-Object {
    Run-OrFail "jsonschema $($_.FullName)" "python -m jsonschema -i `"$($_.FullName)`" schemas\config.schema.json"
  }
}
Run-OrFail "ruff" "ruff check --select=F,E9"
Run-OrFail "mypy" "mypy --strict"
Run-OrFail "integration tests" "just test:integration"
Run-OrFail "npm audit (high)" "npm audit --audit-level=high"

if ($failed) {
  # Semantic quarantine
  $qBranch = "needs-human/$Branch-semantics"
  Write-Warning "Semantic verification failed. Quarantining as $qBranch"
  git checkout -b $qBranch
  git commit --allow-empty -m "chore: quarantine $Branch (semantic-conflict)" --trailer "Auto-Merged-By=policy-v1.2"
  git push -u origin $qBranch
  exit 0
}

# Security-sensitive touch detection: Dockerfile -> quarantine
$changed = (git diff --name-only --cached) + (git diff --name-only)
if ($changed -match '(^|/|\\)Dockerfile$') {
  $qBranch = "needs-human/$Branch-security"
  Write-Warning "Security-sensitive file changed. Quarantining as $qBranch"
  git checkout -b $qBranch
  git commit --allow-empty -m "chore: quarantine $Branch (security-sensitive)" --trailer "Auto-Merged-By=policy-v1.2"
  git push -u origin $qBranch
  exit 0
}

# All good → push
git commit --allow-empty -m "chore: auto-merge-train for $Branch" --trailer "Auto-Merged-By=policy-v1.2 (json-struct, theirs-lockfiles, rerere)"
git push --force-with-lease
