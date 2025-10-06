# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This repository implements an **Enterprise Agentic Workflow Architecture** based on atomic task decomposition with a **Two-ID governance system**. The architecture enables deterministic, multi-agent code modification pipelines with comprehensive validation, merge automation, and workflow orchestration.

## Core Architectural Concepts

### Two-ID Rule
Every atomic task has two identifiers:

1. **atom_uid** - ULID (26 chars, immutable, globally unique)
   - Format: `01J9W4V4R8D8W0Q2Y5J7B0W4ZQ`
   - Used for cross-workflow linking, dependencies, and machine references
   - Never changes even if workflow is reordered or renamed

2. **atom_key** - Human-readable structured key
   - Format: `<NS>/<WF>/<WFv>/<PH>/<LANE>/<SEQ>[-<VAR>][-r<REV>]`
   - Example: `cli/dev-setup/v1/init/all/003`
   - Used for display, documentation, and human communication
   - Stable within workflow version but may change across versions

**Critical Rule**: Always reference dependencies using `atom_uid`, never `atom_key`.

### Repository Structure

```
atomic_two_id_tooling/          # Core toolkit
  atoms/
    examples/                    # Example atom YAML files
    schema/                      # JSON Schema for validation
  tools/atoms/                   # Python validation utilities
  .github/workflows/             # CI enforcement
  Makefile                       # Common commands

deterministic_merge_system/     # Git merge automation
  scripts/                       # PowerShell merge drivers

ATOMIZED_PROCESSES/             # Workflow documentation
DOC & REF/                      # Reference documentation
YAML_YML/                       # Workflow specifications
GIT/                            # Git workflow documentation
```

## Development Commands

### Environment Setup (PowerShell)
```powershell
python -m venv .venv
./.venv/Scripts/python.exe -m pip install -U pip pyyaml jsonschema pre-commit
pre-commit install
```

### Core Validation & Build (from atomic_two_id_tooling/)
```bash
# Validate all atoms (schema, UIDs, deps, contracts)
make validate

# Build searchable index
make index

# Generate dependency graph
make graph

# Fix glossary issues automatically
make glossary/fix

# Query glossary
make glossary/query

# Index schemas
make schemas/index
```

### Individual Validation Steps
If `make` is unavailable, run Python scripts directly:
```bash
python tools/atoms/atom_validator.py      # Schema validation
python tools/atoms/uid_checker.py         # UID uniqueness
python tools/atoms/dep_resolver.py        # Dependency resolution
python tools/atoms/contract_checker.py    # Contract validation
python tools/atoms/glossary_checker.py    # Glossary consistency
```

### Finding Atoms by Need
```bash
# Find producers/consumers by data type
python tools/atoms/find_by_need.py json application/json schemas/users.schema.json
```

### Testing
```bash
pytest -q                              # All tests
pytest -q tests/specific_module        # Specific module
pytest -q -m slow                      # Slow/integration tests only
```

## Atom YAML Schema

All atom definitions must conform to `atoms/schema/atomic_task.schema.json`:

```yaml
atom_uid: 01J9W4V4R8D8W0Q2Y5J7B0W4ZQ    # ULID (required)
atom_key: cli/dev-setup/v1/init/all/003  # Structured key (required)
title: "Initialize .env and secrets policy"
version: "1.0.0"                         # Semver (required)
status: draft | active | deprecated | removed

deps:                                    # ALWAYS use atom_uid
  - 01J9W4R0T1A5M3...                   # Reference by UID only

inputs:                                  # Array of input contracts
  - name: config_template
    kind: json | file | text | table | binary | record | stream
    mime: application/json               # Optional
    schema_ref: schemas/config.json      # Optional
    required: true
    cardinality: one | many

outputs:                                 # Array of output contracts
  - name: validated_config
    kind: json
    mime: application/json
    schema_ref: schemas/validated_config.json

runtime:                                 # Optional execution context
  language: bash | powershell | python | node | none
  entrypoint: scripts/init.sh

security:                                # Security metadata
  pii: false
  secrets_required: ["API_KEY"]

deterministic: true                      # Default true
```

## Git Merge System

The `deterministic_merge_system/` provides automated conflict resolution:

### Setup
```powershell
# From repo root
pwsh ./scripts/setup-merge-drivers.ps1

# Enable rerere (remember resolutions)
git config rerere.enabled true
git config rerere.autoupdate true
```

### Running Merge Train
```powershell
pwsh ./scripts/AutoMerge-Workstream.ps1       # Auto-merge current branch
pwsh ./scripts/AutoMerge-Workstream.ps1 -DryRun  # Preview without merging
```

### Configuration Files
- `.merge-policy.yaml` - Declarative merge rules (branch priority, strategies, gates)
- `.gitattributes` - File-type merge strategies (union/ours/theirs/custom)
- Merge drivers use `jq`/`yq` for JSON/YAML structural merges with fallbacks

## CI/CD Workflow

The `atoms-ci.yaml` workflow enforces validation on every push:
1. Schema validation for all atoms
2. UID uniqueness checks
3. Dependency resolution
4. Contract validation
5. Glossary consistency
6. Index and graph generation

**Pre-commit requirement**: Run `make validate` locally before pushing. CI must pass.

## Coding Conventions

### Python
- 4-space indentation
- Type hints for public functions
- Short docstrings for public APIs
- `snake_case` functions/variables
- `PascalCase` classes
- `UPPER_SNAKE_CASE` constants

### Commits
Use Conventional Commits:
- `feat: add index builder`
- `fix(atoms): enforce UID uniqueness`
- `docs: update Two-ID rule explanation`

### Pull Requests
- One logical change per PR
- Include: problem description, approach, tradeoffs, testing notes
- Link related issues
- CI must be green (run `make validate` and `make index` locally first)

## Key Architectural Patterns

### Multi-Agent Workflow Pattern
The system supports tool-agnostic multi-agent code modification:
1. **Decomposition** - Break tasks into atomic operations
2. **Parallel Execution** - Independent atoms run concurrently
3. **Validation Gates** - Each atom validated before acceptance
4. **Deterministic Merge** - Automated conflict resolution with audit trails

### Quality Assurance Framework
- **Pre-emptive Validation** - Constraints checked before execution
- **Contract Enforcement** - Input/output schemas validated
- **Atomic Recovery** - Failed operations retried without full restart
- **Continuous Validation** - Real-time error detection and correction

### ID Stability Rules
- **Mint new atom_uid** when atom semantics change incompatibly
- **Bump revision (-r2)** for backward-compatible changes to same UID
- **Bump workflow version (v2)** when reordering/retitling atoms in workflow
- **Preserve atom_uid** across reorders (only atom_key sequence changes)

## Common Workflows

### Adding a New Atom
1. Mint new ULID for `atom_uid`
2. Compute `atom_key` from namespace/workflow/phase/sequence
3. Create YAML file in `atoms/examples/` or appropriate workflow directory
4. Reference dependencies using `atom_uid` only
5. Run `make validate` to verify schema and uniqueness
6. Run `make index` to update searchable catalog
7. Commit with message: `feat(atoms): add <atom_key>`

### Modifying an Existing Atom
1. Read atom YAML file to get current `atom_uid`
2. If changing semantics incompatibly: mint new `atom_uid`, mark old as `deprecated`
3. If backward-compatible: keep `atom_uid`, bump revision in `atom_key` (-r2)
4. Update `version` field (semver)
5. Run `make validate` and `make index`
6. Update dependent atoms if breaking change

### Debugging Dependency Chains
1. Run `make graph` to generate `atoms.graph.dot` and `.json`
2. Visualize with Graphviz: `dot -Tpng atoms.graph.dot -o atoms.png`
3. Query index: `python tools/atoms/find_by_need.py <kind> <mime> <schema>`
4. Check `atoms.index.json` for atom catalog

### Resolving Merge Conflicts
1. Check `.merge-policy.yaml` for configured strategies
2. Run `pwsh ./scripts/PreFlight-Check.ps1` to predict conflicts
3. Review `.gitattributes` for file-type merge drivers
4. Check `.git/merge-audit.jsonl` for resolution history
5. Use `git rerere` to replay previous resolutions

## Important Notes

- **Never edit atom_uid** - ULIDs are permanent identifiers
- **Always validate before commit** - Run `make validate` and `make index`
- **Use UID for deps** - Never reference atoms by `atom_key` in dependency arrays
- **Test atomic operations independently** - Each atom should be testable in isolation
- **Security-sensitive files** - Handled conservatively by merge system (see `.merge-policy.yaml`)
- **No secrets in repo** - Use environment variables, document in `config/.env.example`
