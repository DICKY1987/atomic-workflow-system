1) Declare the rules once (repo-local, deterministic)

Create a repo policy file (checked in) that encodes your conflict rules. Keep it short and machine–readable so your hooks/CI can apply it:

# .merge-policy.yaml
version: 1
default_strategy: "recursive"        # git base
weighted_resolution:                  # optional scoring if a smart driver needs it
  timestamp: 3
  author_priority: 5
  branch_priority: 4
  line_age: 1

branch_priority:
  main: 100
  release/*: 90
  dev: 80
  feature/*: 70
  workstream/*: 60

path_strategies:
  # lock files / generated artifacts → take-theirs or binary
  - pattern: "package-lock.json"
    strategy: "theirs"
  - pattern: "poetry.lock"
    strategy: "theirs"
  - pattern: "**/*.png"
    strategy: "binary"

  # union-friendly files (append-only)
  - pattern: "CHANGELOG.md"
    strategy: "union"

  # JSON/YAML: structural merge via custom driver
  - pattern: "**/*.json"
    strategy: "json-struct"
  - pattern: "**/*.{yml,yaml}"
    strategy: "yaml-struct"

author_priority:
  - "you@company.com"         # you (or “merge-captain”) always wins on ties
  - "ci-bot@company.com"

text_norm:
  # ensure fewer diffs before merges
  eol: "lf"
  trim_trailing_whitespace: true
  final_newline: true

2) Teach git (once) via .gitattributes + merge drivers

This makes your rules executable by git—no human in the loop unless a rule says so.

.gitattributes

# normalization to reduce needless conflicts
* text=auto eol=lf

# union merges
CHANGELOG.md merge=union

# binary
*.png binary
*.jpg binary

# take-theirs for lockfiles (they’re generated; latest usually best)
package-lock.json merge=theirs
poetry.lock     merge=theirs

# structural (custom) merges
*.json merge=json-struct
*.yml  merge=yaml-struct
*.yaml merge=yaml-struct


Configure custom drivers (run once per clone):

git config merge.json-struct.name "JSON structural merge"
git config merge.json-struct.driver 'jq -S -s "reduce .[] as $d ({}; . * $d)" %A %O %B > %A || exit 1'

git config merge.yaml-struct.name "YAML structural merge"
git config merge.yaml-struct.driver 'yq -s ".[0] * .[2]" -oy %O %A %B > %A || exit 1'


Notes:

These drivers say: “take base %O, ours %A, theirs %B; deep-merge; write back to %A”.

Replace with any semantic merge you prefer (key-wise precedence, array de-dup, etc.).

On Windows/PowerShell, call jq.exe/yq.exe similarly (use full paths if needed).

3) Record once, reuse forever: enable rerere

This lets git remember how you resolved a specific conflict once; next time it autofixes it.

git config rerere.enabled true
git config rerere.autoupdate true

4) Pre-merge normalization to shrink conflicts

Run formatters before merges so hunks align:

Code: black, ruff --fix, isort, prettier

Data: jq -S for JSON (stable key order), yq -oy for YAML

Text: ensure newline at EOF, strip trailing spaces

Wire these in pre-commit and also in the merge script (idempotent!):

pre-commit run --all-files || true   # never block merges; conflicts are handled by gates

5) Fast, repeatable “merge-train” step per workstream

For each workstream/* branch, your pipeline runs the same tiny sequence:

# scripts/AutoMerge-Workstream.ps1
param(
  [Parameter(Mandatory=$true)][string]$Branch = "$(git branch --show-current)"
)

$ErrorActionPreference='Stop'
git fetch --all --prune

# 1) Rebase onto main to linearize (optional: use merge --no-ff if you prefer)
git checkout $Branch
git rebase origin/main || {
  # 1a) Auto-resolve phase
  # - rerere will try first
  # - custom drivers will run due to .gitattributes
  # - as a fallback, apply deterministic policies by path
  Write-Host "Attempting deterministic conflict resolution..." -ForegroundColor Cyan

  # Example fallback: prefer theirs on generated folders
  git checkout --theirs -- '**/dist/**' '**/build/**' 'package-lock.json' 2>$null
  git add -A

  # Final attempt: run normalization again
  pre-commit run --all-files 2>$null | Out-Null
  git add -A

  git rebase --continue
}

# 2) Verify build/tests (deterministic gates)
just ci:quick || throw "CI quick gate failed"

# 3) Push (or open PR) and label status
git push --force-with-lease


If rebase still stops:

The script creates a quarantine commit per file with an explicit marker (e.g., add “<<<<<<< AUTO-HOLD” around the remaining hunk), pushes a needs-human/<branch> branch, and the CI labels the PR “needs-human”. Your merge train moves on—no stream is blocked for hours.

6) Branch & file fences to avoid conflicts up front

Branch-per-workstream (you already do this) + directory fences: give each stream a home under src/<stream>/… whenever possible.

For shared schemas/config, split by many small files rather than one monolith (configs/*.yaml), so edits don’t collide.

For append-only logs (CHANGELOG, runlogs), use merge=union.

7) Commit trailers for policy hints (author/priority/tags)

Teach your team/agents to include deterministic trailers. Your hook can read them and weight resolutions (use git interpret-trailers):

Example commit message tail:

Conflict-Priority: high
Feature-Owner: you@company.com
Stream: workstream/json-normalizer


Your resolver can map Feature-Owner and Stream against .merge-policy.yaml’s author_priority / branch_priority.

8) CI glue (non-blocking, continuous)

In your Actions (or your “just” recipe):

Job A (merge-train): For each updated workstream/*, run AutoMerge-Workstream.ps1. If unresolved hunks remain, auto-push needs-human/<branch> and label PR “needs-human”. Otherwise, auto-update the PR or fast-forward a staging branch.

Job B (staging-gate): Build/test/lint on a rolling merge-train branch that accumulates successful workstreams. When green, auto-merge to main.

Job C (rerere cache seeding): optional job that trains/exports/imports rerere entries so new machines benefit immediately.

9) “Insta-fix” manual conflicts (when they pop up)

When you do hit a tricky one locally, make the manual fix also feed the machine:

Run the resolver once:

git rebase origin/main
# fix remaining hunks by hand
git add -A && git rebase --continue


Commit goes in, rerere logs it. Next time: it’s automatic.

10) Optional upgrades

git-imerge for truly giant, conflict-heavy rebases (fine-grained, incremental).

Semantic merge tools for specific languages (e.g., Java/C# function-aware merges) if you bring those into the stack.

“Ours/theirs by folder” in .gitattributes for generated SDKs, docs, or vendored code.

Why this fits your rapid, multistream style

Deterministic: The same inputs always produce the same resolution (rules in code + structural drivers + rerere).

Repeatable: Rules live in repo (.gitattributes, .merge-policy.yaml), not in someone’s head.

Non-blocking: The merge train never stalls; worst case a branch is quarantined and labeled while others proceed.

Cheap to extend: Add a new path rule or adjust weights without touching scripts.