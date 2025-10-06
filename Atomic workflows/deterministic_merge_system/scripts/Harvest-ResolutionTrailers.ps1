
# Scans recent commits for Suggests-Rule trailers and prints a summary (CI could open a PR)
$log = git log --since="14 days ago" --pretty=format:"%H%x09%s" --notes --decorate=short
$commits = (git log --since="14 days ago" --pretty=format:"%H")
$result = @()
foreach ($c in $commits) {
  $msg = git show -s --format=%B $c
  $lines = $msg -split "`n"
  foreach ($ln in $lines) {
    if ($ln -match '^\s*Suggests-Rule:\s*(.+)$') {
      $result += [pscustomobject]@{commit=$c; rule=$Matches[1]}
    }
  }
}
if ($result.Count -gt 0) {
  $result | Format-Table -AutoSize
} else {
  Write-Host "No Suggests-Rule trailers found in last 14 days."
}
