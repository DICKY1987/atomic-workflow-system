
param(
  [Parameter(Mandatory=$true)][string]$Branch,
  [Parameter(Mandatory=$true)][string]$File,
  [Parameter(Mandatory=$true)][string]$ConflictType,
  [Parameter(Mandatory=$true)][string]$RuleApplied,
  [string]$Result = "success",
  [string]$Notes = ""
)
$payload = [ordered]@{
  ts = (Get-Date).ToString("o")
  branch = $Branch
  file = $File
  conflict_type = $ConflictType
  rule_applied = $RuleApplied
  result = $Result
  notes = $Notes
}
$line = [System.Text.Json.JsonSerializer]::Serialize($payload)
Add-Content -Path ".git/merge-audit.jsonl" -Value $line
