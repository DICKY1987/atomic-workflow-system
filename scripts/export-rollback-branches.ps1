param(
  [string]$RepoPath = ".",
  [string]$RegistryPath = "slash_registry_optimized.v2.json",
  [string]$OutputPath = "rollback_branches_from_registry.txt"
)

Set-Location -Path $RepoPath
$registry = Get-Content $RegistryPath | ConvertFrom-Json
$legacyNames = $registry.branches | ForEach-Object { $_.legacy_names } | Sort-Object -Unique
$localBranches = git branch --list | ForEach-Object { $_.Trim().Trim("*").Trim() }
$matches = $localBranches | Where-Object { $_ -in $legacyNames }

$matches | Set-Content -Encoding UTF8 -Path $OutputPath
Write-Host "Exported $($matches.Count) rollback branches to: $OutputPath"
