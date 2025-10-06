
param([string]$Target="origin/main")
$ErrorActionPreference = 'SilentlyContinue'
$mb = git merge-base HEAD $Target
if (-not $mb) {
  Write-Warning "Cannot compute merge-base with $Target"
  exit 1
}
$out = git merge-tree $mb HEAD $Target
if ($out -match '^[<]{7}') {
  Write-Warning "Predicted conflicts vs $Target"
  $out | Select-String 'diff --git|^[<=>]{7}' | ForEach-Object { $_.Line }
  exit 2
} else {
  Write-Host "No predicted conflicts vs $Target"
  exit 0
}
