
# Registers resilient merge drivers for JSON/YAML using jq/yq when available, fallback to choosing theirs.
$ErrorActionPreference = 'Stop'

git config merge.json-struct.name "JSON structural merge"
git config merge.json-struct.driver 'powershell -NoProfile -Command if (Get-Command jq -ErrorAction SilentlyContinue) { jq -S -s "reduce .[] as `$d ({}; . * `$d)" %O %A %B > %A } else { Copy-Item %B %A }'

git config merge.yaml-struct.name "YAML structural merge"
git config merge.yaml-struct.driver 'powershell -NoProfile -Command if (Get-Command yq -ErrorAction SilentlyContinue) { yq -oy -s ".[0] * .[2]" %O %A %B > %A } else { Copy-Item %B %A }'

git config rerere.enabled true
git config rerere.autoupdate true
