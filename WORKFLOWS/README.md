# Deterministic Tool-Agnostic Workflow Automation System

A comprehensive collection of **deterministic, reusable workflows** that automate common software development tasks across multiple AI coding tools (Claude Code, Aider, Gemini CLI, Copilot Chat, Continue VSCode).

---

## 📋 Table of Contents

- [Overview](#overview)
- [Workflow Categories](#workflow-categories)
- [Key Features](#key-features)
- [Quick Start](#quick-start)
- [Workflows](#workflows)
- [Architecture](#architecture)
- [Usage Examples](#usage-examples)
- [Installation](#installation)
- [Configuration](#configuration)
- [Best Practices](#best-practices)

---

## Overview

This system provides **atomic, composable workflows** that bring enterprise-grade automation to AI-assisted coding. Every workflow is:

✅ **Deterministic** - Same inputs always produce same outputs
✅ **Tool-Agnostic** - Works across Claude Code, Aider, Gemini, etc.
✅ **Atomic** - Each operation has unique IDs and can be tracked/rolled back
✅ **Git-Safe** - Automatic checkpointing and conflict-free merges
✅ **Validated** - Built-in quality gates and validation
✅ **Observable** - Full audit trails and metrics

### Based On

- **Slash Command Registry**: `slash_registry_optimized.v2.json` - Cross-tool command mapping
- **Git Workflows**: Zero-touch Git automation patterns
- **Atomic Two-ID System**: ULID-based task governance from `CLAUDE.md`
- **Deterministic Merge**: Conflict-free parallel development

---

## Workflow Categories

### 🔧 Core Workflows (`core/`)

1. **Cross-Tool Workflow Translator** - Translate workflows between AI tools
2. **Git Zero-Touch Automation** - Wrap tool sessions with automatic Git safety
3. **Atomic Task Orchestrator** - Execute multi-step tasks with checkpointing
4. **Multi-Agent Pipeline** - Coordinate multiple agents on parallel code changes

### 🔄 GitHub Operations (`github/`)

5. **gh-checkpoint** - Atomic save points with commit and sync
6. **gh-init-workspace** - Initialize isolated workspaces
7. **gh-create-pr** - Create PRs with comprehensive metadata
8. **gh-status-check** - Comprehensive repo status
9. **gh-rollback** - Safe rollback to any checkpoint
10. **gh-merge-workstreams** - Merge parallel branches deterministically

### ✅ Validation (`validation/`)

11. **CI Validation Matrix** - Comprehensive linting, testing, security scans

### 📝 Slash Commands (`slash_commands/`)

12. **Slash Command Library** - Tool-agnostic reusable commands

### 🏗️ Generators (`generators/`)

13. **Registry Workflow Generator** - Auto-generate workflows from intent tags

---

## Key Features

### 🎯 Cross-Tool Translation

```yaml
# Write once in Claude Code
/init-project project_name="my-api" project_type="python"

# Auto-translate to Aider, Gemini, Copilot, Continue
```

### 🔒 Git Zero-Touch

Every AI tool session automatically:
- Creates checkpoint before/after
- Pushes to dedicated branch
- Auto-saves on exit
- Never loses work

### ⚡ Parallel Execution

Execute multiple tasks simultaneously using Git worktrees:
- Workstream A: Core logic (Agent 1)
- Workstream B: Config/infra (Agent 2)
- Workstream C: Tests/docs (Agent 3)
- **Deterministic merge** with auto-conflict resolution

### 📊 Full Observability

Every operation logged to `.workflows/audit/`:
```json
{"timestamp": "2025-10-06T...", "operation": "checkpoint", "result": "success", ...}
```

---

## Quick Start

### 1. Clone Workflows

```bash
cd "C:\Users\Richard Wilks\Downloads\Atomic workflows\WORKFLOWS"
```

### 2. Run a Workflow

#### Example: Safe Git Checkpoint

```bash
# Using the gh-checkpoint workflow
cd github/
python run_workflow.py gh_checkpoint.yaml \
  --context "feature-complete" \
  --skip_ci true
```

#### Example: Multi-Agent Parallel Development

```yaml
# Create workstreams.yaml
workstreams:
  - workstream_id: core_logic
    agent_tool: claude
    task_description: "Refactor authentication"
    file_patterns: ["src/auth/**"]
    priority: 1

  - workstream_id: config_infra
    agent_tool: aider
    task_description: "Update Docker configs"
    file_patterns: ["Dockerfile", ".github/**"]
    priority: 2

  - workstream_id: tests_docs
    agent_tool: gemini
    task_description: "Add tests and docs"
    file_patterns: ["tests/**", "docs/**"]
    priority: 3
```

```bash
# Execute parallel workflow
python run_workflow.py core/multi_agent_pipeline.yaml \
  --project-path /path/to/project \
  --workstreams workstreams.yaml
```

### 3. Validate Code

```bash
# Run full validation matrix
python run_workflow.py validation/ci_validation_matrix.yaml \
  --project-path /path/to/project \
  --validation-gates lint,test,security,coverage
```

---

## Workflows

### Core Workflows

#### 1. Cross-Tool Workflow Translator

**Purpose**: Translate workflows between AI coding tools

**Input**:
```yaml
source_workflow: my_workflow.yaml
source_tool: claude_code
target_tools: [aider, gemini_cli, copilot_chat]
```

**Output**:
- Translated workflows for each target tool
- Compatibility report
- Platform variants (Windows/Linux/macOS)

**Example**:
```bash
python translate.py \
  --source my_claude_workflow.yaml \
  --from claude_code \
  --to aider,gemini
```

---

#### 2. Git Zero-Touch Automation

**Purpose**: Wrap AI tool sessions with automatic Git safety

**Features**:
- Pre/post session checkpoints
- Session-specific branches
- Auto-save on exit
- Push to remote automatically

**Example**:
```bash
# Wrap Claude Code session
./git_zero_touch.sh claude \
  --session-name "feature-auth" \
  --branch-strategy session_branch
```

**Hooks Created**:
- `.git/hooks/pre-close` - Auto-save before exit
- `.git/hooks/post-commit` - Auto-push after commit

---

#### 3. Atomic Task Orchestrator

**Purpose**: Execute complex workflows with automatic checkpointing and rollback

**Features**:
- Dependency resolution
- Parallel execution
- Automatic rollback on failure
- Checkpoint after each atom

**Example**:
```bash
python orchestrate.py workflow.yaml \
  --execution-mode hybrid \
  --checkpoint-after-each \
  --rollback-on-failure
```

**Execution Plan**:
```
Batch 0: [atom_001] (sequential)
Batch 1: [atom_002, atom_003, atom_004] (parallel)
Batch 2: [atom_005] (sequential, depends on 002-004)
```

---

#### 4. Multi-Agent Code Modification Pipeline

**Purpose**: Coordinate multiple AI agents on parallel code changes

**Workflow**:
1. Create isolated worktrees per agent
2. Execute tasks in parallel
3. Analyze changes for conflicts
4. Merge deterministically
5. Run integration tests
6. Cleanup worktrees

**Example**:
```bash
python multi_agent.py \
  --project-path /path/to/project \
  --workstreams workstreams.yaml \
  --integration-tests tests/integration/
```

**Benefits**:
- 60-80% time reduction vs sequential
- Zero conflicts during development
- Each agent works in isolation
- Automatic conflict resolution on merge

---

### GitHub Operations

#### 5. gh-checkpoint

Create atomic save points with commit and remote sync.

```bash
./gh_checkpoint.sh --context "validation-passed"
```

**Output**:
```json
{
  "checkpoint_id": "abc123...",
  "context": "validation-passed",
  "files_changed": 5,
  "pushed_to_remote": true
}
```

---

#### 6. gh-init-workspace

Initialize isolated workspace with branch strategy.

```bash
./gh_init_workspace.sh \
  --repo-url https://github.com/user/repo.git \
  --workstream-id "feature-api" \
  --use-worktree
```

---

#### 7. gh-create-pr

Create PR with auto-generated description and metadata.

```bash
./gh_create_pr.sh \
  --branch-name feature/new-api \
  --reviewers alice,bob \
  --auto-merge
```

**Generated PR**:
- Title from branch name and commits
- Comprehensive description with changes summary
- Test results attached
- Auto-merge enabled when checks pass

---

#### 8. gh-status-check

Comprehensive repository status check.

```bash
./gh_status_check.sh --verbose
```

**Output**:
```
=== Status Summary ===
Branch: feature/new-api
Ready to merge: ✅ YES
Working tree: ✅ Clean
Remote sync: ✅ Synced
PR #42: OPEN (MERGEABLE)
Reviews: APPROVED
Checks: 5 passing, 0 failing
CI: success
```

---

#### 9. gh-rollback

Safe rollback to any checkpoint with history preservation.

```bash
./gh_rollback.sh \
  --target checkpoint:abc123 \
  --reason "Failed integration tests" \
  --preserve-history
```

---

#### 10. gh-merge-workstreams

Merge multiple parallel workstream branches.

```bash
./gh_merge_workstreams.sh \
  --workstream-branches ws1,ws2,ws3 \
  --integration-branch integration/2025-10-06 \
  --merge-strategy no-ff
```

---

### Validation Workflows

#### 11. CI Validation Matrix

Comprehensive validation: linting, tests, security, coverage.

```bash
./ci_validation_matrix.sh --project-path /path/to/project
```

**Validation Gates**:
- ✅ Lint (pylint, black, isort)
- ✅ Tests (pytest with coverage)
- ✅ Security (bandit, safety)
- ✅ Coverage (>80% threshold)

---

### Slash Commands

#### 12. Slash Command Library

Reusable commands for all tools:

**Available Commands**:
- `/init-project` - Initialize new project
- `/safe-edit` - Edit with checkpointing
- `/parallel-work` - Multi-agent execution
- `/validate-all` - Full validation suite
- `/merge-safe` - Safe merge with validation
- `/create-pr` - Create PR with metadata
- `/rollback` - Rollback to checkpoint
- `/status` - Comprehensive status

**Installation**:
```bash
# For Claude Code
cp slash_commands/*.md .claude/commands/

# For Aider
cp slash_commands/*.toml .aider/commands/
```

---

### Generators

#### 13. Registry Workflow Generator

Auto-generate workflows from slash command registry.

```bash
python registry_workflow_gen.py \
  --registry-path ../DOC\ &\ REF/slash_registry_optimized.v2.json \
  --intent-tags code.review,agents.manage
```

**Output**:
- `code_review_workflow.yaml`
- `agents_manage_workflow.yaml`
- `generation_report.json`

---

## Architecture

### Two-ID Governance

Every atomic task has two identifiers:

```yaml
atom_uid: 01JADVXR0000000000000000A1  # ULID (immutable, globally unique)
atom_key: workflows/translator/v1/load/all/001  # Human-readable
```

**Rules**:
- Always reference dependencies using `atom_uid`
- `atom_key` is for display/documentation
- Never reuse `atom_uid` even if atom is deleted

### Workflow Structure

```yaml
meta:
  workflow_id: "my-workflow-v1"
  version: "1.0.0"
  purpose: "What this workflow does"

inputs:
  - name: input_param
    kind: text
    required: true

outputs:
  - name: output_result
    kind: json

atoms:
  - atom_uid: 01JADV...
    atom_key: workflows/my/v1/step/all/001
    title: "Do something"
    runtime:
      language: python
      entrypoint: |
        # Python code here
    inputs: [input_param]
    outputs: [output_result]
```

### Execution Modes

1. **Sequential**: Atoms run one after another
2. **Parallel**: Independent atoms run simultaneously
3. **Hybrid**: Mix of sequential and parallel based on dependencies

---

## Usage Examples

### Example 1: Safe Development Workflow

```bash
# 1. Initialize workspace
./gh_init_workspace.sh --repo-url https://github.com/user/repo

# 2. Wrap coding session with Git safety
./git_zero_touch.sh claude --session-name "feature-auth"

# 3. Validate changes
./ci_validation_matrix.sh --project-path .

# 4. Create PR
./gh_create_pr.sh --auto-merge --reviewers alice
```

### Example 2: Parallel Multi-Agent Development

```bash
# 1. Define workstreams
cat > workstreams.yaml <<EOF
workstreams:
  - workstream_id: backend
    agent_tool: claude
    task_description: "API endpoints"
  - workstream_id: frontend
    agent_tool: aider
    task_description: "UI components"
  - workstream_id: tests
    agent_tool: gemini
    task_description: "Test coverage"
EOF

# 2. Execute in parallel
python multi_agent_pipeline.py --workstreams workstreams.yaml

# 3. Results merged automatically with conflict resolution
```

### Example 3: Translate Workflow Across Tools

```bash
# 1. Create workflow for Claude Code
cat > my_workflow.yaml <<EOF
# Claude Code specific workflow
EOF

# 2. Translate to other tools
python cross_tool_translator.py \
  --source my_workflow.yaml \
  --from claude_code \
  --to aider,gemini,copilot

# 3. Use translated workflows
# - workflows/aider/translated_my_workflow.yaml
# - workflows/gemini/translated_my_workflow.yaml
# - workflows/copilot/translated_my_workflow.yaml
```

---

## Installation

### Prerequisites

```bash
# Git 2.34+
git --version

# GitHub CLI
gh --version

# Python 3.9+
python --version

# Node/npm (optional, for Node projects)
node --version
```

### Setup

```bash
# 1. Clone workflows
cd "C:\Users\Richard Wilks\Downloads\Atomic workflows\WORKFLOWS"

# 2. Install Python dependencies
pip install pyyaml jsonschema ulid-py

# 3. Make scripts executable (Unix)
chmod +x github/*.sh validation/*.sh core/*.sh

# 4. Configure Git
git config --global rerere.enabled true
git config --global merge.conflictstyle zdiff3
```

---

## Configuration

### Git Configuration

```bash
# Recommended Git settings
git config --local rerere.enabled true
git config --local rerere.autoupdate true
git config --local merge.conflictstyle zdiff3
git config --local push.default current
git config --local push.autoSetupRemote true
git config --local rebase.autoStash true
```

### Workflow Configuration

Create `.workflows/config.yaml`:

```yaml
github:
  default_branch: main
  checkpoint_strategy: after_phase
  auto_merge: true
  merge_strategy: squash

validation:
  coverage_threshold: 80
  fail_fast: false
  gates: [lint, test, security, coverage]

multi_agent:
  max_parallel_agents: 5
  merge_strategy: no-ff
  auto_resolve_conflicts: true
```

---

## Best Practices

### 1. Always Use Checkpoints

```bash
# Before major changes
./gh_checkpoint.sh --context "before-refactor"

# After validation
./gh_checkpoint.sh --context "validation-passed"
```

### 2. Isolate Parallel Work

```bash
# Use worktrees for true isolation
--branch-strategy worktree
```

### 3. Validate Before Merge

```bash
# Always run validation
./ci_validation_matrix.sh

# Check status
./gh_status_check.sh
```

### 4. Use Tool Translation

```bash
# Write once, run anywhere
python cross_tool_translator.py --source workflow.yaml --to all
```

### 5. Monitor Audit Logs

```bash
# Check operation history
tail -f .workflows/audit/*.jsonl
```

---

## Observability

### Metrics Tracked

- `checkpoints_created` - Total checkpoints
- `validation_pass_rate` - % validations passing
- `merge_conflict_rate` - % merges with conflicts
- `auto_resolution_success_rate` - % conflicts auto-resolved
- `parallel_efficiency` - Time saved with parallel execution

### Audit Trails

All operations logged to `.workflows/audit/`:

```jsonl
{"timestamp":"2025-10-06T10:30:00Z","operation":"checkpoint","context":"feature-complete","result":"success","sha":"abc123"}
{"timestamp":"2025-10-06T10:31:00Z","operation":"validation","gates":["lint","test"],"result":"pass"}
{"timestamp":"2025-10-06T10:32:00Z","operation":"merge","branches":["ws1","ws2"],"conflicts":0,"result":"success"}
```

---

## Troubleshooting

### Checkpoint Failed

```bash
# Check if in git repo
git status

# Verify remote configured
git remote -v

# Retry with force
./gh_checkpoint.sh --context "retry" --force
```

### Merge Conflicts

```bash
# Check conflict predictions
./gh_merge_workstreams.sh --dry-run

# Use auto-resolution
# Configured in .gitattributes and .merge-policy.yaml
```

### Validation Failures

```bash
# Run individual gates
./ci_validation_matrix.sh --validation-gates lint
./ci_validation_matrix.sh --validation-gates test

# Check detailed output
cat .workflows/validation/report.json
```

---

## Contributing

To add new workflows:

1. Follow atomic schema: `atomic_two_id_tooling/atoms/schema/atomic_task.schema.json`
2. Generate unique `atom_uid` using ULID
3. Add validation and observability
4. Document in this README

---

## License

MIT License - See parent repository for details

---

## Support

- **Issues**: Report at repository issues page
- **Documentation**: See `../DOC & REF/` for detailed references
- **Examples**: Check `../YAML_YML/` for workflow examples

---

**🤖 Generated with Atomic Workflow System**

Last Updated: 2025-10-06
