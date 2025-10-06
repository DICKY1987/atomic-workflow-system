## 1) Observability: structured merge audit

Add a tiny helper and call it from your merge-train script.

**scripts/Write-MergeAudit.ps1**

```powershell
param(
  [Parameter(Mandatory)][string]$Branch,
  [Parameter(Mandatory)][string]$File,
  [Parameter(Mandatory)][string]$ConflictType,
  [Parameter(Mandatory)][string]$RuleApplied,
  [string]$Result = "success",
  [string]$Notes = ""
)
$line = [System.Text.Json.JsonSerializer]::Serialize([ordered]@{
  ts = (Get-Date).ToString("o")
  branch = $Branch
  file = $File
  conflict_type = $ConflictType
  rule_applied = $RuleApplied
  result = $Result
  notes = $Notes
})
Add-Content -Path ".git/merge-audit.jsonl" -Value $line
```

**Call from merge-train** (whenever you auto-resolve or quarantine):

```powershell
.\scripts\Write-MergeAudit.ps1 -Branch $Branch -File $f -ConflictType "text-overlap" -RuleApplied "json-struct"
```

## 2) Post-merge verification (semantic)

Extend your policy and gates.

**.merge-policy.yaml (new block)**

```yaml
verification:
  json_schemas:
    - path: "config/**/*.json"
      schema: "schemas/config.schema.json"
  static_analysis:
    - "ruff check --select=F,E9"
    - "mypy --strict"
  integration_tests:
    - "just test:integration"
  security_checks:
    - "npm audit --audit-level=high || exit 1"
```

**Merge-train (after resolving, before push):**

```powershell
# JSON schema validate (python jsonschema or ajv)
if (Test-Path .\schemas\config.schema.json) {
  Get-ChildItem config -Recurse -Filter *.json |
    ForEach-Object { python -m jsonschema -i $_.FullName schemas\config.schema.json }
}
ruff check --select=F,E9
mypy --strict
just test:integration
npm audit --audit-level=high
```

## 3) Cross-file semantic conflicts label

If the verification suite fails, push to quarantine with a distinct label.

```powershell
git checkout -b "needs-human/$Branch-semantics"
git commit --allow-empty -m "chore: quarantine $Branch (semantic-conflict)"
git push -u origin "needs-human/$Branch-semantics"
# Optional: create an issue/PR label via gh
gh issue create --title "Semantic conflict: $Branch" --body "See merge-audit.jsonl" --label "semantic-conflict"
```

## 4) Rollback / “big red button”

A repo switch to suspend auto-merging.

**.merge-train.flag** (present = enabled; absent = manual only)

In your script:

```powershell
if (-not (Test-Path ".merge-train.flag")) {
  Write-Warning "Merge-train disabled; sending branch to quarantine."
  # push current state to needs-human and exit 0
  exit 0
}
```

Commit trailers for traceability:

```
Auto-Merged-By: policy-v1.2 (json-struct, theirs-lockfiles, rerere)
```

## 5) Conflict prediction (pre-flight)

**scripts/PreFlight-Check.ps1**

```powershell
param([string]$Target="origin/main")
$mb = git merge-base HEAD $Target
$out = git merge-tree $mb HEAD $Target
if ($out -match '^[<]{7}') {
  Write-Warning "Likely conflicts vs $Target"
  $out | Select-String 'diff --git|^[<=>]{7}' | ForEach-Object { $_.Line }
  exit 2
}
```

Run this nightly on long-lived workstreams; if non-zero, auto-rebase during off-hours.

## 6) Security-sensitive files

Tighten policy and force manual or audited merges.

**.gitattributes**

```
requirements.txt merge=theirs
Dockerfile merge=manual
```

**Merge-train guard:**

```powershell
if (git diff --name-only --cached | Select-String -Quiet 'Dockerfile') {
  throw "Security-sensitive file touched; forcing quarantine"
}
```

## 7) Human feedback → rule tuning

Capture how humans resolved and create auto-PRs to evolve policy.

**Post-quarantine resolution commit message trailers:**

```
Conflict-Resolution: config.json prefer-key=service.port theirs
Suggests-Rule: **/config/*.json json-struct key-precedence=theirs(service.port)
```

**scripts/Harvest-ResolutionTrailers.ps1**

```powershell
$entries = git log --since="7 days ago" --pretty=format:"%H%x09%s" --numstat --notes | Select-String "Suggests-Rule:"
# generate a PR editing .merge-policy.yaml accordingly (use gh API)
```

## 8) Ownership & notifications

Auto-assign via CODEOWNERS and ping Slack.

**.github/CODEOWNERS**

```
/src/json/**   @you
/config/**     @platform-team
```

**Workflow step (GitHub Actions)**

```yaml
- name: Notify Slack on quarantine
  if: failure() || contains(steps.merge_train.outputs.status, 'quarantine')
  run: |
    curl -X POST "$SLACK_WEBHOOK" -H 'Content-type: application/json' \
      --data "{\"text\":\"🚧 Quarantine: $GITHUB_REF — owners: $(gh pr view --json reviewRequests --jq '.reviewRequests[].login' || echo n/a)\"}"
```

## 9) Harden custom drivers (fallbacks)

Make json/yaml drivers resilient when tools are missing or files malformed.

**Bash setup**

```bash
git config merge.json-struct.driver '
  if command -v jq >/dev/null 2>&1; then
    jq -S -s "reduce .[] as $d ({}; . * $d)" %O %A %B > %A || { cp %B %A; }
  else
    cp %B %A
  fi'
git config merge.yaml-struct.driver '
  if command -v yq >/dev/null 2>&1; then
    yq -oy -s ".[0] * .[2]" %O %A %B > %A || cp %B %A
  else
    cp %B %A
  fi'
```

**PowerShell (Windows)**

```powershell
git config merge.json-struct.driver 'powershell -NoProfile -Command ^
  if (Get-Command jq -ErrorAction SilentlyContinue) { ^
    jq -S -s "reduce .[] as `$d ({}; . * `$d)" %O %A %B > %A ^
  } else { Copy-Item %B %A }'
```

## 10) Monorepo fences

Block auto-merges that cross a stream’s sandbox.

**.merge-policy.yaml (new block)**

```yaml
workstream_fences:
  workstream/json-normalizer:
    allowed_paths:
      - "src/json/**"
      - "tests/json/**"
    cross_fence_conflicts: quarantine
```

**Merge-train enforcement:**

```powershell
$changed = git diff --name-only --merge
$fence = Get-Content .merge-policy.yaml | ConvertFrom-Yaml
if ($Branch -match '^workstream/json-normalizer' -and
   ($changed | Where-Object { $_ -notlike "src/json/*" -and $_ -notlike "tests/json/*" })) {
  throw "Cross-fence change detected → quarantine"
}
```

---

# Medium-impact polish (optional but sweet)

* **Parallel merge-train**: shard workstreams by fence; run 3–5 in parallel runners.
* **Cache parsed trees**: write `%A.hash` → merged output; reuse if `(O,A,B)` hashes repeat.
* **Dry-run mode**: `AutoMerge-Workstream.ps1 -DryRun` prints the rules that would trigger.
* **Training sandbox**: synthetic conflict branches to practice resolutions and seed `rerere`.

---

# Minimal checklist to wire it up

1. Commit `.merge-policy.yaml` updates + `.gitattributes` tweaks.
2. Configure merge drivers (jq/yq) with fallbacks.
3. Enable `rerere` and add `scripts/Write-MergeAudit.ps1`.
4. Extend merge-train with: audit logging → verification gates → quarantine paths → trailers.
5. Add PreFlight check to a nightly workflow.
6. Add Slack notify + CODEOWNERS ownership.
7. (Optional) Add the big-red-button `.merge-train.flag`.

This keeps your pipeline **deterministic, observable, and self-tuning**, while preserving the core principle: *conflicts never block the highway—worst case, they exit to the quarantine lane with receipts.*
