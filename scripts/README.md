# Rollback Branch Cleanup Scripts

This directory contains PowerShell scripts for managing and cleaning up Git rollback branches in the Atomic repository.

## Scripts Overview

### 1. `list-rollback-branches.ps1`
Lists all local rollback branches that match entries in the registry file.

**Usage:**
```powershell
.\list-rollback-branches.ps1 -RepoPath "." -RegistryPath "slash_registry_optimized.v2.json"
```

**Parameters:**
- `RepoPath` - Path to the repository (default: current directory)
- `RegistryPath` - Path to the registry JSON file

---

### 2. `export-rollback-branches.ps1`
Exports registry-matched rollback branches to a text file for batch processing.

**Usage:**
```powershell
.\export-rollback-branches.ps1 -RepoPath "." -RegistryPath "slash_registry_optimized.v2.json" -OutputPath "rollback_branches.txt"
```

**Parameters:**
- `RepoPath` - Path to the repository (default: current directory)
- `RegistryPath` - Path to the registry JSON file
- `OutputPath` - Output file path (default: rollback_branches_from_registry.txt)

---

### 3. `cleanup-rollback-branches.ps1`
Deletes rollback branches from the remote repository. Can use either git or GitHub CLI (gh).

**Usage:**
```powershell
# Using git
.\cleanup-rollback-branches.ps1

# Using GitHub CLI
.\cleanup-rollback-branches.ps1 -UseGh -Repo "DICKY1987/Atomic"
```

**Parameters:**
- `UseGh` - Use GitHub CLI instead of git (switch)
- `Repo` - Repository name (e.g., DICKY1987/Atomic)

---

### 4. `rollback-cleanup-automation.ps1`
**Main comprehensive script** that performs a complete rollback cleanup:
- Deletes local and remote rollback branches
- Fixes rollback naming conventions (rollback/ → rollback-)
- Installs cleanup automation (GitHub Actions workflow)
- Creates commits and optionally opens a pull request
- Generates detailed JSON and text reports

**Usage:**
```powershell
.\rollback-cleanup-automation.ps1 -RepoPath "." -BaseBranch "main" -GitUserName "Your Name" -GitUserEmail "your.email@example.com"
```

**Parameters:**
- `RepoPath` - Repository path (default: current directory)
- `BaseBranch` - Base branch name (default: main)
- `GitRemote` - Git remote name (default: origin)
- `SkipNamingFix` - Skip fixing naming conventions (switch)
- `SkipAutomation` - Skip installing automation (switch)
- `PrTitle` - Pull request title
- `PrBody` - Pull request body
- `GitUserName` - Git user name for commits
- `GitUserEmail` - Git user email for commits
- `GitHubToken` - GitHub API token for creating PRs (optional)
- `GitHubRepo` - GitHub repository (e.g., DICKY1987/Atomic) - auto-detected if omitted

**Example with PR creation:**
```powershell
.\rollback-cleanup-automation.ps1 `
  -GitUserName "Your Name" `
  -GitUserEmail "your.email@example.com" `
  -GitHubToken "ghp_your_token_here" `
  -GitHubRepo "DICKY1987/Atomic"
```

---

## GitHub Actions Workflow

The `cleanup-rollback-branches.yml` workflow automatically runs the cleanup script:
- **Trigger:** On push to main branch or manual dispatch
- **Action:** Deletes all rollback branches using GitHub CLI
- **Permissions:** Requires write access to contents

---

## Workflow

1. **Review branches:** Run `list-rollback-branches.ps1` to see what will be cleaned up
2. **Export list (optional):** Run `export-rollback-branches.ps1` to create a list
3. **Run cleanup:** Execute `rollback-cleanup-automation.ps1` to perform full cleanup
4. **Review reports:** Check generated JSON and text reports in repository root

---

## Requirements

- **PowerShell 7+** (Windows PowerShell)
- **Git** installed and configured
- **GitHub CLI (gh)** - Optional, for `UseGh` mode
- **GitHub Personal Access Token** - Optional, for automatic PR creation

---

## Notes

- All scripts include error handling and detailed logging
- The main automation script creates a transcript log file
- Backup your repository before running cleanup operations
- The automation installs a GitHub Actions workflow that runs on every push to main
