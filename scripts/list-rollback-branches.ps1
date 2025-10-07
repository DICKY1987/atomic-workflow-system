param(
  [string]$RepoPath = ".",
  [string]$RegistryPath = "slash_registry_optimized.v2.json"
)

Set-Location -Path $RepoPath
$ErrorActionPreference = "Stop"

# Load registry
$registry = Get-Content $RegistryPath | ConvertFrom-Json
$legacyNames = $registry.branches | ForEach-Object { $_.legacy_names } | Sort-Object -Unique

# Get local branches
$localBranches = git branch --list | ForEach-Object { $_.Trim().Trim("*").Trim() }

# Match against registry
$matches = $localBranches | Where-Object { $_ -in $legacyNames }

Write-Host "`n=== Matching Rollback Branches ==="
$matches | ForEach-Object { Write-Host "• $_" }
