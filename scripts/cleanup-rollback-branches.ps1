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
