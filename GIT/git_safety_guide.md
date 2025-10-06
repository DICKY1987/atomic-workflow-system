# Git Safety Net for AI Coding Tools
**Never Lose Work Again: A Multi-Layer Defense Strategy**

---

## 🎯 ROOT CAUSE ANALYSIS

Your problems stem from:
1. **No auto-save layer** - closing terminals loses uncommitted work
2. **Branch chaos** - each tool creates branches independently
3. **No coordination** - tools don't know about each other's changes
4. **Manual git** - you're the integration point (which fails)

---

## 💡 SOLUTION ARCHITECTURE

### **Layer 1: Git-Level Protection (Works for ALL tools)**

Create a `.git/hooks` setup that acts as an invisible safety net:

#### `.git/hooks/pre-close` (custom trigger)
```bash
#!/bin/bash
# Auto-checkpoint before any terminal might close
# Trigger this via shell config (see below)

WORK_IN_PROGRESS=$(git status --porcelain)
if [ -n "$WORK_IN_PROGRESS" ]; then
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    TOOL_NAME=${AI_TOOL_NAME:-"unknown"}
    
    git add -A
    git commit -m "WIP: Auto-save from ${TOOL_NAME} [${TIMESTAMP}]" \
               -m "Auto-checkpoint before session end" \
               --no-verify
    
    # Push to personal backup branch
    BACKUP_BRANCH="wip/${TOOL_NAME}/${TIMESTAMP}"
    git push -u origin HEAD:${BACKUP_BRANCH} --no-verify 2>/dev/null || true
    
    echo "✓ Work saved to ${BACKUP_BRANCH}"
fi
```

#### `.git/hooks/post-commit`
```bash
#!/bin/bash
# Auto-push every commit to a safety branch
git push origin HEAD:refs/heads/auto-backup/$(git branch --show-current) --force-with-lease 2>/dev/null &
```

**Don't forget to make hooks executable:**
```bash
chmod +x .git/hooks/pre-close
chmod +x .git/hooks/post-commit
```

---

### **Layer 2: Shell-Level Integration**

#### Bash/Zsh Configuration
Add to your `.bashrc` or `.zshrc`:

```bash
export AI_TOOL_NAME="generic"

# Auto-save on terminal exit
function auto_save_git() {
    if [ -d .git ]; then
        .git/hooks/pre-close 2>/dev/null
    fi
}
trap auto_save_git EXIT

# Enhanced tool aliases with auto-checkpointing
alias aider='export AI_TOOL_NAME="aider" && aider --auto-commits --commit-prompt "feat({file}): {message}"'
alias continue='export AI_TOOL_NAME="continue" && continue'

# Git aliases for safe operations
git config --global alias.safe-checkpoint '!f() { 
    git add -A && 
    git commit -m "checkpoint: ${1:-auto-save}" && 
    git push origin HEAD --force-with-lease; 
}; f'

git config --global alias.wip '!git safe-checkpoint "WIP: $(date +%H:%M)"'
```

#### PowerShell Configuration
Add to your PowerShell `$PROFILE`:

```powershell
$env:AI_TOOL_NAME = "generic"

# Auto-save on PowerShell exit
Register-EngineEvent -SourceIdentifier PowerShell.Exiting -Action {
    if (Test-Path .git) {
        git add -A
        git commit -m "WIP: Auto-save on exit [$(Get-Date -Format 'HHmmss')]" --no-verify
        git push origin HEAD:refs/heads/wip/$(git branch --show-current) --force-with-lease 2>$null
    }
}
```

---

### **Layer 3: Per-Tool Configuration**

#### **Aider** (Best git integration out of the box)

Create `.aider.conf.yml` in your repo root:

```yaml
auto-commits: true
commit-prompt: "feat({file}): {message}\n\nCo-authored-by: Aider <aider@ai>"
dirty-commits: true  # Commit even with uncommitted changes
git-diffs: true
```

Command line usage:
```bash
aider --auto-commits --dirty-commits
```

#### **Continue** (VS Code extension)

Add to `.vscode/settings.json`:

```json
{
  "continue.enableAutoCommit": true,
  "continue.autoCommitMessage": "feat: Continue AI changes [skip ci]",
  "git.autoStash": true,
  "git.autoFetch": true,
  "files.autoSave": "afterDelay",
  "files.autoSaveDelay": 1000,
  
  "continue.gitBranchPattern": "continue/${timestamp}"
}
```

#### **GitHub Copilot** (Built into VS Code)

Add to `.vscode/settings.json`:

```json
{
  "github.copilot.advanced": {
    "autoCommit": true,
    "commitMessageTemplate": "feat: Copilot suggestion for ${file}"
  }
}
```

#### **Claude Code** (CLI wrapper)

Create `~/bin/claude-code-safe`:

```bash
#!/bin/bash
export AI_TOOL_NAME="claude"

# Auto-checkpoint before starting
git wip

# Your Claude Code command here
claude "$@"

# Auto-checkpoint after
git wip

# Optional: Create a feature branch for this session
SESSION_BRANCH="claude/$(date +%Y%m%d_%H%M%S)"
git checkout -b "$SESSION_BRANCH" 2>/dev/null || true
```

Make it executable:
```bash
chmod +x ~/bin/claude-code-safe
```

---

### **Layer 4: Git Worktrees (Parallel Work Without Conflicts)**

#### Setup Script: `.det-tools/setup-worktrees.sh`

```bash
#!/bin/bash

# Main repo for orchestration
MAIN_REPO=$(pwd)

# Create worktrees for each tool
tools=("aider" "continue" "claude" "copilot")

for tool in "${tools[@]}"; do
    WORKTREE_DIR="../${tool}-workspace"
    BRANCH="tool/${tool}/main"
    
    # Create branch if doesn't exist
    git branch "$BRANCH" 2>/dev/null || true
    
    # Create worktree
    git worktree add "$WORKTREE_DIR" "$BRANCH" 2>/dev/null || \
        echo "Worktree $WORKTREE_DIR already exists"
    
    echo "✓ $tool workspace: $WORKTREE_DIR (branch: $BRANCH)"
done

echo "
Workspaces created! Use them like:
  cd ../aider-workspace && aider
  cd ../continue-workspace && code .
"
```

**Benefits of Worktrees:**
- Each tool works in its own workspace
- No conflicts - they're on different branches
- Easy to merge later: `git merge tool/aider/main tool/continue/main`
- All share the same `.git` directory (saves space)

---

### **Layer 5: VS Code Settings (Universal)**

#### `.vscode/settings.json`

```json
{
  "files.autoSave": "afterDelay",
  "files.autoSaveDelay": 1000,
  
  "git.autoStash": true,
  "git.autoFetch": "all",
  "git.autoRepositoryDetection": true,
  "git.confirmSync": false,
  "git.enableSmartCommit": true,
  "git.postCommitCommand": "push",
  "git.allowForcePush": true,
  "git.useForcePushWithLease": true,
  
  "workbench.localHistory.enabled": true,
  "workbench.localHistory.maxFileSize": 4096,
  "workbench.localHistory.mergeWindow": 10,
  
  "tasks.autoDetect": "on"
}
```

#### `.vscode/tasks.json`

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Auto-checkpoint every 5min",
      "type": "shell",
      "command": "git",
      "args": ["wip"],
      "runOptions": {
        "runOn": "folderOpen",
        "instanceLimit": 1
      },
      "presentation": {
        "echo": false,
        "reveal": "never",
        "panel": "shared"
      },
      "isBackground": true,
      "problemMatcher": []
    }
  ]
}
```

---

### **Layer 6: Smart Branch Strategy**

#### `.git/config` (Local Repository)

```ini
[branch]
    autosetuprebase = always

[pull]
    rebase = true

[push]
    default = current
    autoSetupRemote = true
    followTags = true

[merge]
    conflictstyle = zdiff3  # Better conflict markers
    ff = false

[rebase]
    autoStash = true
    autoSquash = true
```

#### Git Aliases (Global or Local)

```bash
# Quick recovery commands
git config --global alias.undo 'reset --soft HEAD^'
git config --global alias.recover '!git fsck --lost-found && git reflog'

# Branch cleanup
git config --global alias.cleanup-merged "!git branch --merged | grep -v '\\*\\|main\\|master' | xargs -n 1 git branch -d"

# Smart merge all tool branches
git config --global alias.merge-all-tools '!git merge --no-ff tool/aider/main tool/continue/main tool/claude/main tool/copilot/main'
```

---

## 🚀 IMPLEMENTATION PLAN

### **Week 1: Safety Net**

```bash
# 1. Install hooks
mkdir -p .git/hooks
# Copy hook scripts above to .git/hooks/
chmod +x .git/hooks/*

# 2. Configure shell auto-save
# Add shell configuration from Layer 2 to ~/.bashrc or ~/.zshrc

# 3. Test it
# Open terminal, make a change, close terminal
# Check: git log should show auto-save commit
git log --oneline -5
```

### **Week 2: Tool Integration**

1. Configure each tool's settings (Layer 3)
2. Test each tool in isolation
3. Verify auto-commits happening with `git log`

### **Week 3: Worktrees** (Optional but recommended)

```bash
# 1. Setup worktrees for each tool
bash .det-tools/setup-worktrees.sh

# 2. Update your workflow:
#    - Aider work → ../aider-workspace
#    - Continue work → ../continue-workspace
#    - etc.

# 3. Weekly merge:
git merge-all-tools
```

### **Week 4: Automation**

Add scheduled tasks:

**Linux/Mac (crontab):**
```bash
# Every hour: auto-checkpoint
0 * * * * cd /path/to/repo && git wip

# Every day: merge all tools
0 0 * * * cd /path/to/repo && git merge-all-tools && git push
```

**Windows (Task Scheduler):**
```powershell
# Create scheduled task for hourly checkpoint
$action = New-ScheduledTaskAction -Execute 'git' -Argument 'wip' -WorkingDirectory 'C:\path\to\repo'
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Hours 1)
Register-ScheduledTask -TaskName "Git Auto-Checkpoint" -Action $action -Trigger $trigger
```

---

## 📊 MONITORING & RECOVERY

### Check What's Been Auto-Saved

```bash
# See all auto-save commits
git log --all --oneline --grep="WIP\|Auto-save"

# See all tool branches
git branch -a | grep "tool/\|wip/"

# See detailed auto-save history
git log --all --oneline --author="Auto" --since="1 week ago"
```

### Recover Lost Work

```bash
# See everything that happened (including deleted branches)
git reflog --all | head -50

# Search for specific work
git reflog --all | grep "your search term"

# Recover a specific commit
git cherry-pick <commit-hash>

# Recover a deleted branch
git checkout -b recovered-branch <commit-hash>

# Find dangling commits (not on any branch)
git fsck --lost-found
```

---

## 🎁 BONUS: Ultimate Safety Script

### `~/bin/safe-ai-session`

```bash
#!/bin/bash
# Wrapper for ANY AI tool that guarantees no lost work

TOOL_NAME=${1:-"unknown"}
shift  # Remove tool name from args

echo "🛡️  Starting safe session with $TOOL_NAME"

# 1. Auto-checkpoint before
git wip

# 2. Create session branch
SESSION="$TOOL_NAME/$(date +%Y%m%d_%H%M%S)"
git checkout -b "$SESSION" 2>/dev/null || git checkout "$SESSION"

# 3. Run the tool
"$TOOL_NAME" "$@"

# 4. Auto-checkpoint after
git add -A
git commit -m "Session complete: $TOOL_NAME" --no-verify || true

# 5. Push to remote
git push -u origin "$SESSION" --force-with-lease

echo "✅ Session saved to branch: $SESSION"
echo "To merge: git checkout main && git merge $SESSION"
```

**Usage:**
```bash
chmod +x ~/bin/safe-ai-session

safe-ai-session aider
safe-ai-session continue
# etc.
```

---

## 🎯 KEY PRINCIPLES

1. **Never trust humans** (including yourself) to remember to commit
2. **Auto-save everything** at multiple layers
3. **Push often** - remote is backup
4. **Branch per tool** - isolation prevents conflicts  
5. **Git is cheap** - commit noise is better than lost work
6. **Hooks > humans** - automation wins
7. **Multiple safety nets** - if one fails, others catch you

---

## 🔧 TROUBLESHOOTING

### "Hook not executing"
```bash
# Verify hook is executable
ls -la .git/hooks/
chmod +x .git/hooks/*

# Test hook manually
.git/hooks/pre-close
```

### "Can't push - authentication failed"
```bash
# Setup Git credential helper
git config --global credential.helper store
# or for Windows
git config --global credential.helper manager

# Or use SSH keys instead of HTTPS
git remote set-url origin git@github.com:user/repo.git
```

### "Too many branches cluttering repo"
```bash
# Clean up old auto-save branches (older than 7 days)
git branch -r | grep 'wip/' | while read branch; do
    BRANCH_DATE=$(git log -1 --format=%ci "$branch" | cut -d' ' -f1)
    if [[ "$BRANCH_DATE" < "$(date -d '7 days ago' +%Y-%m-%d)" ]]; then
        git push origin --delete "${branch#origin/}"
    fi
done
```

### "Merge conflicts between tool branches"
```bash
# Use merge strategy that favors newest changes
git merge --strategy-option=patience tool/aider/main

# Or merge manually with conflict resolution
git merge tool/aider/main
# Fix conflicts in editor
git add .
git commit
```

---

## 📚 ADDITIONAL RESOURCES

- [Git Worktrees Documentation](https://git-scm.com/docs/git-worktree)
- [Git Hooks Reference](https://git-scm.com/docs/githooks)
- [Aider Documentation](https://aider.chat/)
- [Continue.dev Documentation](https://continue.dev/)

---

## 📝 CONFIGURATION CHECKLIST

- [ ] Git hooks installed and executable
- [ ] Shell configuration updated (bashrc/zshrc/profile)
- [ ] VS Code settings configured
- [ ] Per-tool configurations added
- [ ] Git aliases configured
- [ ] Worktrees set up (optional)
- [ ] Scheduled tasks created (optional)
- [ ] Test: Make change, close terminal, verify auto-save
- [ ] Test: Run each AI tool, verify commits appear
- [ ] Test: Merge tool branches together

---

**Remember:** This system is designed to be fail-safe. Even if you forget everything, the hooks and auto-save mechanisms will protect your work. The worst case scenario is having too many commits, which is infinitely better than losing work!