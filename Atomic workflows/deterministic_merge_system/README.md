# Deterministic Merge & Conflict-Resolution System

This bundle implements the full blueprint we discussed starting from **“1) Declare the rules once (repo-local, deterministic)”** through advanced upgrades:
- Repo-level rules (`.merge-policy.yaml`, `.gitattributes`)
- Custom JSON/YAML merge drivers (jq/yq) with resilient fallbacks
- `git rerere` learning
- Merge-train script with verification gates, quarantine, and audit logging
- Pre-flight conflict prediction, security-sensitive handling, ownership routing

## Quick Start

```bash
# from repo root
# 1) add files
#   copy contents of this folder into your repo (preserve paths)
# 2) one-time setup (register merge drivers)
pwsh ./scripts/setup-merge-drivers.ps1
# 3) enable rerere (remember manual fixes)
git config rerere.enabled true
git config rerere.autoupdate true
# 4) try the merge train on your current branch
pwsh ./scripts/AutoMerge-Workstream.ps1
```

## Files

- **.merge-policy.yaml** — Declarative rules: branch priority, path strategies, verification gates, fences.
- **.gitattributes** — Maps file types/paths to merge strategies (union/ours/theirs/custom).
- **scripts/setup-merge-drivers.ps1** — Registers JSON/YAML merge drivers with fallbacks; enables rerere.
- **scripts/AutoMerge-Workstream.ps1** — Rebase onto main, auto-resolve via rules, run verification gates, push or quarantine.
- **scripts/Write-MergeAudit.ps1** — Append structured JSON lines to `.git/merge-audit.jsonl`.
- **scripts/PreFlight-Check.ps1** — Predicts conflicts using `git merge-tree`.
- **scripts/Harvest-ResolutionTrailers.ps1** — Surfaces human resolution trailers to evolve rules.
- **.github/workflows/merge-train.yml** — CI job to run merge train on every `workstream/**` push.
- **.github/CODEOWNERS** — Auto-ownership for quarantine routing.

## Notes

- **jq/yq** are assumed present. If missing, the drivers fall back to choosing incoming (`theirs`) to keep the train moving; you can harden as needed.
- Security-sensitive files (`Dockerfile`, `requirements.txt`) are handled conservatively; lockfiles prefer `theirs` then re-normalize in CI.
- Add schema files under `schemas/` to activate JSON schema verification.
- To pause automation, remove or ignore the CI job and run `AutoMerge-Workstream.ps1 -DryRun` locally.

## Conversation Summary (from “Declare rules once” onward)

1. **Repo rules**: deterministic policies stored in repo (.gitattributes + .merge-policy.yaml).  
2. **Custom drivers**: JSON/YAML structural merges via jq/yq; binary/lockfiles use simple policies.  
3. **rerere**: Git remembers manual fixes and replays them automatically next time.  
4. **Merge train**: Non-blocking pipeline—resolve or quarantine; never stall other streams.  
5. **Upgrades**: Observability (audit logs), post-merge semantic checks, security handling, pre-flight prediction, ownership routing, fallback drivers, fences, and a big-red-button to pause automation.

This keeps multistream development rapid, deterministic, and observable—conflicts are either auto-resolved or cleanly quarantined with receipts.
