# Deterministic GitHub Operations Module

## Philosophy
**Git/GitHub operations are 100% deterministic and should be invisible to users. The system handles all branching, merging, conflict resolution, and synchronization automatically at configurable save points.**

---

## CORE DETERMINISTIC COMMANDS

### **COMMAND: `gh-checkpoint`**
```yaml
purpose: Atomic save point - commits and syncs current state to remote
frequency: Can be called at ANY point in ANY pipeline
replaces_concepts:
  - Manual git add/commit/push
  - Branch management decisions
  - Commit message writing
usage_patterns:
  - After each workstream completes
  - After validation passes
  - Before/after merge operations
  - On demand via --checkpoint flag
implementation:
  script: |
    1. Validate working directory is clean or has trackable changes
    2. Stage all changes (git add -A)
    3. Generate conventional commit message from:
       - Pipeline phase context
       - Modified file summary
       - Validation results
    4. Create atomic commit with metadata
    5. Push to remote with --force-with-lease (safe force)
    6. Verify remote sync
    7. Tag checkpoint with timestamp and context
    8. Update checkpoint registry
  commands:
    - git status --porcelain
    - git add -A
    - git commit -m "chore(phase): ${CONTEXT} [skip ci]"
    - git push --force-with-lease origin HEAD
    - gh api repos/:owner/:repo/git/refs/heads/$BRANCH --field sha=$COMMIT_SHA
  bash: ./.det-tools/scripts/gh_checkpoint.sh
  pwsh: ./.det-tools/scripts/GH-Checkpoint.ps1
outputs: .det-tools/out/checkpoint.json
success_criteria:
  - Changes committed locally
  - Remote synchronized
  - Checkpoint registered
  - No conflicts
error_handling:
  - If remote diverged: fetch, rebase, retry
  - If conflicts: auto-resolve or flag for resolution command
  - If push fails: exponential backoff retry (3 attempts)
```

### **COMMAND: `gh-init-workspace`**
```yaml
purpose: Initialize isolated workspace with proper branch strategy
replaces_concepts:
  - Manual git clone/init
  - Branch creation decisions
  - Remote configuration
called_by: Pipeline initialization, workstream setup
implementation:
  script: |
    1. Detect if repo already cloned, clone if needed
    2. Configure git identity (from config or CI environment)
    3. Set up remote tracking
    4. Create or checkout base branch (main/master)
    5. Fetch latest state
    6. Create feature branch with naming convention: 
       - feature/${PIPELINE_ID}/${WORKSTREAM_ID}/${TIMESTAMP}
    7. Set up git worktree if parallel workstreams
    8. Configure git hooks (if using pre-commit)
    9. Validate workspace ready
  commands:
    - gh repo clone $REPO_URL --depth 1 || git pull
    - git config user.name "$GIT_USER"
    - git config user.email "$GIT_EMAIL"
    - git checkout -B $BASE_BRANCH origin/$BASE_BRANCH
    - git worktree add ../$WORKSTREAM_DIR $FEATURE_BRANCH || git checkout -B $FEATURE_BRANCH
    - gh repo set-default
  bash: ./.det-tools/scripts/gh_init_workspace.sh
  pwsh: ./.det-tools/scripts/GH-Init-Workspace.ps1
outputs: .det-tools/out/workspace.json
success_criteria:
  - Workspace directory exists
  - Git configured correctly
  - Branch created and checked out
  - Remote tracking established
  - JSON contains: {workspace_dir, branch, remote_url, worktree_path}
```

### **COMMAND: `gh-sync-remote`**
```yaml
purpose: Bidirectional sync - fetch remote changes and push local state
frequency: Before major operations (merge, validation, deployment)
replaces_concepts:
  - Manual git fetch/pull/push
  - Merge conflict anxiety
  - Stale branch issues
implementation:
  script: |
    1. Stash any uncommitted changes (with identifier)
    2. Fetch all remotes with prune
    3. Check if remote branch exists
    4. If remote exists:
       - Compare local vs remote state
       - If diverged: attempt auto-merge or rebase
       - If conflicts: use conflict resolution strategy
    5. Push local commits with --force-with-lease
    6. Pop stashed changes if any
    7. Verify sync state
  commands:
    - git stash push -u -m "auto-sync-${TIMESTAMP}"
    - git fetch --all --prune --tags
    - gh api repos/:owner/:repo/commits/$BRANCH || echo "new branch"
    - git rebase origin/$BASE_BRANCH || git merge --strategy-option=theirs origin/$BASE_BRANCH
    - git push --force-with-lease origin $BRANCH
    - git stash pop || echo "no stash"
  bash: ./.det-tools/scripts/gh_sync_remote.sh
  pwsh: ./.det-tools/scripts/GH-Sync-Remote.ps1
outputs: .det-tools/out/sync_status.json
success_criteria:
  - Local and remote in sync
  - No untracked conflicts
  - Push successful
  - JSON contains: {commits_pulled, commits_pushed, conflicts_resolved}
conflict_strategy:
  - Auto-resolve: Accept "theirs" for config files, "ours" for generated code
  - Document conflicts in conflict_report.json
  - If critical conflicts: pause pipeline and notify
```

### **COMMAND: `gh-merge-workstreams`**
```yaml
purpose: Merge multiple parallel workstream branches without conflicts
replaces_concepts:
  - Manual merge conflict resolution
  - Multi-branch merge anxiety
  - Integration branch management
called_by: Phase 3 integration
implementation:
  script: |
    1. Create/checkout integration branch
    2. Validate all workstream branches pushed and current
    3. For each workstream branch:
       - Analyze changes (files modified, lines changed)
       - Detect potential conflicts before merging
       - Execute merge with appropriate strategy
       - Run validation after each merge
    4. If conflicts detected:
       - Categorize: file-level, line-level, semantic
       - Apply resolution strategy:
         * File-level: Keep both, rename if needed
         * Line-level: Use 3-way merge with ancestor
         * Semantic: Flag for validation
    5. After all merges:
       - Run linters on merged result
       - Run quick validation suite
       - Create merge commit with summary
    6. Push integration branch
  commands:
    - git checkout -B integration-${PIPELINE_ID}
    - for BRANCH in $WORKSTREAM_BRANCHES; do
    -   git merge --no-ff --strategy-option=patience $BRANCH
    -   [run lint/validation]
    - done
    - gh pr create --base main --head integration-${PIPELINE_ID} --title "Integration: ${PIPELINE_ID}" || echo "PR exists"
  bash: ./.det-tools/scripts/gh_merge_workstreams.sh
  pwsh: ./.det-tools/scripts/GH-Merge-Workstreams.ps1
outputs: 
  - .det-tools/out/merge_result.json
  - .det-tools/out/conflicts_resolved.json
success_criteria:
  - All workstreams merged
  - Conflicts auto-resolved or documented
  - Validation passing on merged state
  - Integration branch pushed
  - JSON contains: {branches_merged, conflicts_auto_resolved, conflicts_flagged}
conflict_resolution_hierarchy:
  1. Automatic: Non-overlapping changes (90%+ of cases)
  2. Rule-based: Config files, generated code, known patterns
  3. AI-assisted: Complex semantic conflicts (fallback to thinking_ai)
  4. Manual: Only if critical and ambiguous (rare with worktrees)
```

### **COMMAND: `gh-create-pr`**
```yaml
purpose: Create or update pull request with complete context
replaces_concepts:
  - Manual PR creation in web UI
  - PR description writing
  - Reviewer assignment
  - Label/milestone management
called_by: Phase 4 PR creation
implementation:
  script: |
    1. Validate branch is pushed and current
    2. Check if PR already exists for this branch
    3. Generate PR title from commit history and context
    4. Generate comprehensive PR description:
       - Summary of changes
       - Files modified breakdown
       - Test coverage report
       - Performance impact
       - Breaking changes warning
       - Validation results
    5. Attach artifacts:
       - Test reports (JUnit XML)
       - Coverage reports
       - Lint results
       - Performance benchmarks
    6. If PR exists: update description and add comment
       If new: create PR with metadata
    7. Assign reviewers based on CODEOWNERS and file patterns
    8. Add labels based on change type and impact
    9. Link related issues
    10. Set milestone if configured
    11. Enable auto-merge if all checks configured
  commands:
    - gh pr list --head $BRANCH --json number,state
    - gh pr create \
        --title "${PR_TITLE}" \
        --body-file .det-tools/out/pr_description.md \
        --base main \
        --head $BRANCH \
        --label "automated,${CHANGE_TYPE}" \
        --reviewer @${REVIEWERS} \
        --assignee @me \
        --milestone "${MILESTONE}"
    - gh pr edit $PR_NUMBER --add-label "validated"
    - gh pr merge $PR_NUMBER --auto --squash || echo "awaiting checks"
  bash: ./.det-tools/scripts/gh_create_pr.sh
  pwsh: ./.det-tools/scripts/GH-Create-PR.ps1
outputs: .det-tools/out/pr_info.json
success_criteria:
  - PR created or updated
  - Reviewers assigned
  - Labels applied
  - Checks triggered
  - JSON contains: {pr_number, pr_url, reviewers, status}
auto_merge_conditions:
  - All CI checks passing
  - Required approvals obtained
  - No merge conflicts
  - Branch up to date with base
```

### **COMMAND: `gh-cleanup-branches`**
```yaml
purpose: Clean up temporary branches and worktrees after merge
frequency: After successful merge to main
replaces_concepts:
  - Manual branch deletion
  - Stale branch accumulation
  - Worktree cleanup
implementation:
  script: |
    1. Verify merge to main completed
    2. List all feature branches for this pipeline
    3. For each branch:
       - Check if merged to main
       - If merged: delete local and remote branch
       - If not merged: flag for review
    4. Remove worktrees
    5. Prune remote tracking branches
    6. Clean up git reflog (optional, configurable)
    7. Archive branch metadata for audit
  commands:
    - gh pr view $PR_NUMBER --json state,mergedAt
    - for BRANCH in $FEATURE_BRANCHES; do
    -   git branch -d $BRANCH
    -   gh api repos/:owner/:repo/git/refs/heads/$BRANCH -X DELETE
    - done
    - git worktree prune
    - git remote prune origin
    - git reflog expire --expire=now --all && git gc --prune=now (optional)
  bash: ./.det-tools/scripts/gh_cleanup_branches.sh
  pwsh: ./.det-tools/scripts/GH-Cleanup-Branches.ps1
outputs: .det-tools/out/cleanup_report.json
success_criteria:
  - Merged branches deleted
  - Worktrees removed
  - Remote refs pruned
  - Audit trail preserved
```

### **COMMAND: `gh-rollback`**
```yaml
purpose: Revert to any previous checkpoint or commit
frequency: On demand or triggered by validation failures
replaces_concepts:
  - Manual git revert/reset
  - Fear of breaking main branch
  - Complex rollback procedures
implementation:
  script: |
    1. Identify rollback target:
       - By checkpoint ID
       - By commit SHA
       - By time ("30 minutes ago")
       - By tag
    2. Validate rollback target exists
    3. Create rollback branch from target
    4. If rolling back main:
       - Create revert commits (not reset, preserves history)
       - Run validation on reverted state
       - Create PR with rollback context
       - Auto-merge if validation passes
    5. If rolling back feature branch:
       - Hard reset to target
       - Force push with lease
    6. Update rollback registry
    7. Notify stakeholders
  commands:
    - git checkout -B rollback-${TIMESTAMP} ${ROLLBACK_TARGET}
    - git revert --no-edit ${COMMIT_RANGE} (for main branch)
    - git reset --hard ${ROLLBACK_TARGET} (for feature branch)
    - git push --force-with-lease origin rollback-${TIMESTAMP}
    - gh pr create --base main --head rollback-${TIMESTAMP} --title "Rollback: ${REASON}"
  bash: ./.det-tools/scripts/gh_rollback.sh
  pwsh: ./.det-tools/scripts/GH-Rollback.ps1
outputs: .det-tools/out/rollback_result.json
success_criteria:
  - Rollback target valid
  - State reverted successfully
  - History preserved (for main)
  - Validation passing
  - Stakeholders notified
safety:
  - Never destructive resets on main/master
  - Always preserve history
  - Always validate before finalizing
  - Always create audit trail
```

### **COMMAND: `gh-status-check`**
```yaml
purpose: Comprehensive repository and workflow status check
frequency: Before critical operations, on demand
replaces_concepts:
  - Manual status checking
  - "Is CI passing?" questions
  - "Are there conflicts?" uncertainty
implementation:
  script: |
    1. Check local workspace status:
       - Working tree clean/dirty
       - Commits ahead/behind remote
       - Untracked files
    2. Check remote branch status:
       - Exists on remote
       - CI/CD status
       - Review status
       - Merge conflicts
    3. Check PR status (if exists):
       - Approval count
       - Required checks status
       - Merge conflicts
       - Mergeable state
    4. Check workflow runs:
       - Latest run status
       - Failed jobs
       - Running jobs
    5. Generate comprehensive status report
  commands:
    - git status --porcelain --branch
    - gh pr checks $PR_NUMBER
    - gh pr view $PR_NUMBER --json reviewDecision,mergeable,statusCheckRollup
    - gh run list --branch $BRANCH --limit 5
    - gh api repos/:owner/:repo/commits/$BRANCH/status
  bash: ./.det-tools/scripts/gh_status_check.sh
  pwsh: ./.det-tools/scripts/GH-Status-Check.ps1
outputs: .det-tools/out/status_report.json
success_criteria:
  - Complete status snapshot generated
  - All checks accounted for
  - Clear go/no-go signals
  - JSON contains: {workspace_status, remote_status, pr_status, ci_status, mergeable}
```

---

## INTEGRATION POINTS IN MAIN PIPELINE

### **Checkpoint Integration Strategy**
```yaml
automatic_checkpoints:
  # Phase 0
  - after: init-moddoc
    cmd: gh-checkpoint --context "moddoc-initialized"
  
  # Phase 1  
  - after: analyze-project
    cmd: gh-checkpoint --context "analysis-complete"
  - after: setup-workstreams
    cmd: gh-checkpoint --context "workstreams-ready"
  
  # Phase 2 (per workstream)
  - after: exec-core-edits
    cmd: gh-checkpoint --context "workstream-a-complete" --branch workstream-a
  - after: exec-config-infra
    cmd: gh-checkpoint --context "workstream-b-complete" --branch workstream-b
  - after: exec-tests-docs
    cmd: gh-checkpoint --context "workstream-c-complete" --branch workstream-c
  - after: vscode-validate-all
    cmd: gh-checkpoint --context "validation-complete"
  
  # Phase 3
  - before: detect-resolve-conflicts
    cmd: gh-sync-remote --all-branches
  - after: run-integration-tests
    cmd: gh-checkpoint --context "integration-tested"
  - after: validate-quality-gates
    cmd: gh-checkpoint --context "quality-validated"
  
  # Phase 4
  - at: pr-creation
    cmd: gh-create-pr --auto-merge-when-ready
  
  # Phase 5
  - after: execute-final-merge
    cmd: gh-checkpoint --context "merged-to-main" --branch main
  - after: post-merge-validation
    cmd: gh-checkpoint --context "production-validated"
  
  # Cleanup
  - after: collect-metrics
    cmd: gh-cleanup-branches

on_failure:
  - trigger: gh-rollback --to-last-valid-checkpoint
  - notify: stakeholders
```

### **Modified Phase Commands with Git Integration**

```yaml
# Example: exec-core-edits with integrated git ops
exec-core-edits-v2:
  steps:
    - gh-init-workspace --workstream core-edits
    - [existing code modification logic]
    - lint-all
    - run-tests
    - gh-checkpoint --context "core-edits-validated"
  on_error:
    - gh-rollback --to checkpoint-before-exec-core-edits
```

---

## CONFIGURATION

### **Repository Configuration** (.det-tools/config/github.yaml)
```yaml
github:
  default_branch: main
  checkpoint_strategy: after_phase  # Options: after_phase, after_command, manual
  auto_merge: true
  require_reviews: 1
  merge_strategy: squash  # Options: squash, merge, rebase
  
  branch_naming:
    feature: "feature/${pipeline_id}/${workstream}/${timestamp}"
    integration: "integration/${pipeline_id}"
    rollback: "rollback/${timestamp}"
  
  commit_conventions:
    type: conventional  # feat, fix, chore, docs, etc.
    scope_from: workstream
    auto_sign: true
  
  conflict_resolution:
    strategy: auto_with_fallback
    rules:
      - pattern: "*.json"
        strategy: theirs
      - pattern: "*.lock"
        strategy: theirs
      - pattern: "src/**/*.py"
        strategy: patience_3way
  
  cleanup:
    auto_delete_merged: true
    keep_branches_days: 7
    prune_on_cleanup: true
```

---

## BENEFITS

### **For Users**
- Never think about git commands
- Never see merge conflicts
- Never worry about losing work
- Never manually create PRs or branches
- Automatic save points throughout workflow

### **For System**
- Idempotent operations (can retry safely)
- Complete audit trail of all changes
- Rollback to any point in history
- Parallel workstreams without conflicts
- CI/CD integration automatic

### **For Workflows**
- Drop-in git operations at any point
- Configurable checkpoint frequency
- Tool-agnostic (works with any pipeline)
- Handles complex multi-branch scenarios
- Automatic conflict resolution

---

## COMMAND REFERENCE

```bash
# Initialization
gh-init-workspace [--workstream NAME]

# Save points (automatic or manual)
gh-checkpoint [--context MESSAGE] [--branch BRANCH]

# Synchronization
gh-sync-remote [--all-branches] [--force]

# Merging
gh-merge-workstreams --branches BRANCH1,BRANCH2,BRANCH3

# PR management
gh-create-pr [--auto-merge] [--reviewers @user1,@user2]

# Status
gh-status-check [--verbose]

# Recovery
gh-rollback --to [CHECKPOINT_ID|COMMIT_SHA|TAG] [--reason MESSAGE]

# Cleanup
gh-cleanup-branches [--force] [--keep-days N]
```

---

## ERROR HANDLING

### **Network Issues**
```yaml
retry_strategy:
  max_attempts: 3
  backoff: exponential
  backoff_base: 2  # seconds
  timeout: 30  # seconds per operation
```

### **Conflict Resolution Failure**
```yaml
on_conflict:
  - attempt: auto_resolution
  - if_fails: create_conflict_report.json
  - if_critical: pause_pipeline
  - notify: human_oversight
  - provide: resolution_suggestions
```

### **Push Rejection**
```yaml
on_push_rejection:
  - fetch_remote
  - if_diverged: rebase_with_strategy
  - if_still_fails: force_with_lease
  - if_still_fails: create_new_branch
  - log: conflict_details
```

---

## OBSERVABILITY

### **Metrics Tracked**
```yaml
git_operations_metrics:
  - checkpoint_frequency
  - commits_per_phase
  - merge_conflict_rate
  - auto_resolution_success_rate
  - rollback_frequency
  - branch_lifetime
  - pr_creation_time
  - merge_to_main_time
```

### **Audit Trail**
Every git operation logs:
- Command executed
- Context (phase, workstream)
- Result (success/failure)
- Commit SHA
- Timestamp
- User/agent performing operation

Stored in: `.det-tools/audit/git_operations.jsonl`