# Two-ID Atomic Workflow Conversion & Maintenance Manual
 Two_ID Atomic Workflow Conversion  Maintenance Manual
.md
**Version:** 1.0.0  
**Status:** Enterprise Reference Standard  
**Last Updated:** 2025-10-05  
**Document Classification:** Technical Reference

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Core Concepts](#2-core-concepts)
3. [Identifier Specification](#3-identifier-specification)
4. [Canonical Schema](#4-canonical-schema)
5. [Namespacing & Versioning](#5-namespacing--versioning)
6. [File Organization](#6-file-organization)
7. [Registry Architecture](#7-registry-architecture)
8. [Conversion from Legacy Workflows](#8-conversion-from-legacy-workflows)
9. [Lifecycle Operations](#9-lifecycle-operations)
10. [Automation & Validation](#10-automation--validation)
11. [Governance Model](#11-governance-model)
12. [Error Handling & Recovery](#12-error-handling--recovery)
13. [Security & Compliance](#13-security--compliance)
14. [Performance Considerations](#14-performance-considerations)
15. [Tooling Reference](#15-tooling-reference)
16. [Quick Reference](#16-quick-reference)

---

## 1. Executive Summary

### 1.1 Purpose

The Two-ID System provides a deterministic, collision-proof framework for identifying, linking, and managing atomic tasks across autonomous workflows. It eliminates numeric ID conflicts, enables safe refactoring, and guarantees traceability throughout task lifecycles.

### 1.2 Business Value

- **Scalability:** Manage 100,000+ atomic tasks without coordination overhead
- **Autonomy:** Multiple teams work independently without ID collisions
- **Traceability:** Complete audit trail with immutable history
- **Flexibility:** Reorder, split, merge tasks without breaking dependencies
- **Automation-Ready:** Stable identifiers for AI agents and automated systems

### 1.3 Scope

This manual applies to all repositories and workflows adopting the Atomic Task Framework, including:

- Multi-agent code modification pipelines
- Parallel execution workflows
- CI/CD orchestration systems
- Enterprise workflow management platforms

---

## 2. Core Concepts

### 2.1 Atomic Task Definition

An **atomic task (atom)** represents the smallest independently verifiable unit of work within a workflow. Each atom:

- Has a single responsibility
- Can be tested in isolation
- Produces deterministic outputs given consistent inputs
- Can be executed, skipped, or retried without affecting other atoms
- Lives in its own YAML file

### 2.2 The Two-ID Principle

Every atomic task is identified by two complementary identifiers:

| Identifier | Purpose | Target Audience |
|------------|---------|-----------------|
| `atom_uid` | Permanent, globally unique machine identifier | Automation systems, databases, cross-workflow links |
| `atom_key` | Structured, human-readable contextual identifier | Documentation, reviews, discussions, sorting |

**Design Principle:** `atom_uid` ensures stability; `atom_key` provides context.

### 2.3 Dependency Model

Dependencies are **always** specified using `atom_uid` values. This ensures:

- Links remain stable across workflow reorganizations
- Cross-workflow dependencies are explicit and verifiable
- Automated validation can detect broken references
- Dependency graphs can be constructed programmatically

---

## 3. Identifier Specification

### 3.1 atom_uid (Machine Identifier)

#### Format Options

**Primary (Recommended): ULID**
```
^[0-9A-HJKMNP-TV-Z]{26}$
```
- 26 characters, base32-encoded
- Lexicographically sortable by timestamp
- 128 bits of entropy (48-bit timestamp + 80-bit random)
- Example: `01J9W4V4R8D8W0Q2Y5J7B0W4ZQ`

**Alternative: UUIDv7**
```
^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-7[0-9a-fA-F]{3}-[89ab][0-9a-fA-F]{3}-[0-9a-fA-F]{12}$
```
- Time-ordered UUID format (RFC 9562)
- Example: `018c3f19-07f2-7000-8000-000000000000`

#### Properties

- **Immutable:** Never changes after creation
- **Globally Unique:** Collision probability < 10^-15
- **Opaque:** Contains no semantic information
- **Sortable:** Natural chronological ordering

#### Generation Rules

1. Generate at atom creation time
2. Use cryptographically secure random source
3. Never reuse retired UIDs
4. Never manually construct UIDs
5. Always validate format before persistence

### 3.2 atom_key (Human Identifier)

#### Format Specification

```
<NS>/<WF>/<WFv>/<PH>/<LANE>/<SEQ>[-<VAR>][-r<REV>]
```

#### Component Definitions

| Segment | Description | Format | Examples |
|---------|-------------|--------|----------|
| `NS` | Namespace | `[a-z0-9-]+` | `cli`, `hp`, `eafix` |
| `WF` | Workflow slug | `[a-z0-9-]+` | `dev-setup`, `multi-merge` |
| `WFv` | Workflow version | `v[0-9]+` | `v1`, `v2`, `v10` |
| `PH` | Phase | `[a-z0-9-]+` | `init`, `prep`, `exec`, `val`, `ci` |
| `LANE` | Complexity lane | `[a-z0-9-]+` | `simple`, `mod`, `complex`, `all` |
| `SEQ` | Sequence number | `[0-9]{3}` | `001`, `042`, `999` |
| `VAR` | Optional variant | `-[a-z0-9-]+` | `-api`, `-db`, `-win`, `-linux` |
| `REV` | Optional revision | `-r[0-9]+` | `-r2`, `-r5` |

#### Validation Regex

```regex
^[a-z0-9-]+/[a-z0-9-]+/v[0-9]+/[a-z0-9-]+/[a-z0-9-]+/[0-9]{3}(-[a-z0-9-]+)?(-r[0-9]+)?$
```

#### Examples

```yaml
# Standard format
cli/dev-setup/v1/init/all/003

# With variant (platform-specific)
cli/dev-setup/v1/init/all/003-win

# With revision (semantic change)
hp/orchestrate/v3/val/complex/021-r2

# With both variant and revision
cli/multi-merge/v2/exec/mod/014-api-r3
```

#### Key Design Decisions

1. **Lowercase only:** Ensures case-insensitive file system compatibility
2. **Zero-padded sequence:** Enables natural sorting (001, 002, ..., 999)
3. **Hyphen separators:** Clear visual distinction between segments
4. **Optional segments:** Flexibility without complexity for simple cases

---

## 4. Canonical Schema

### 4.1 Minimal Required Schema

```yaml
atom_uid: 01J9W4V4R8D8W0Q2Y5J7B0W4ZQ
atom_key: cli/dev-setup/v1/init/all/003
title: "Initialize .env and secrets policy"
role: "orchestrator"
```

### 4.2 Complete Schema with Optional Fields

```yaml
# === REQUIRED IDENTIFIERS ===
atom_uid: 01J9W4V4R8D8W0Q2Y5J7B0W4ZQ
atom_key: cli/dev-setup/v1/init/all/003

# === DESCRIPTIVE METADATA ===
title: "Initialize .env and secrets policy"
description: "Creates .env template, validates secrets policy compliance"
role: "orchestrator"

# === INPUT/OUTPUT CONTRACTS ===
inputs:
  - config.yaml
  - .ai/guard/allowed_paths.txt
outputs:
  - .env.template
  - .ai/guard/policy.txt

# === DEPENDENCY GRAPH ===
deps:
  - 01J9W4R0T1A5M3P8Q6K2N7V5ZW  # Prerequisite atom UIDs
  - 01J9W4R0T1A5M3P8Q6K2N7V5ZX

# === LIFECYCLE METADATA ===
status: active  # active|deprecated|removed|split|merged
created: "2025-10-05T16:22:00Z"
updated: "2025-10-05T16:22:00Z"

# === VERSIONING ===
rev_notes: "Added guardrail validation step"
legacy_id: atom_003  # Optional: original numeric ID
display_order: 30    # Optional: override sequence for rendering

# === LIFECYCLE TRACKING ===
superseded_by: null          # UID of replacement atom
split_into: []               # UIDs if atom was split
merged_into: null            # UID if atom was consolidated

# === EXECUTION METADATA ===
estimated_duration: "30s"
retry_policy: "exponential_backoff"
timeout: "5m"

# === CLASSIFICATION ===
tags:
  - environment
  - security
  - initialization
```

### 4.3 Field Definitions

#### Required Fields

- **atom_uid:** Globally unique identifier (ULID/UUIDv7)
- **atom_key:** Structured human-readable key
- **title:** Brief descriptive name (max 100 chars)
- **role:** Responsible role or agent (e.g., orchestrator, planning_ai)

#### Recommended Fields

- **description:** Detailed explanation of atom's purpose
- **deps:** Array of prerequisite atom_uid values
- **status:** Current lifecycle state
- **inputs/outputs:** Contract specification

#### Optional Fields

- **display_order:** Override natural sequence ordering
- **legacy_id:** Traceability to old numbering system
- **rev_notes:** Explanation of revisions
- **tags:** Classification metadata

---

## 5. Namespacing & Versioning

### 5.1 Namespace Selection

**Purpose:** Organize atoms by business domain or organizational unit.

**Guidelines:**
- Use lowercase, hyphenated identifiers
- Keep short (2-10 characters)
- Stable over time (rarely changed)
- Unique within organization

**Examples:**
- `cli` - Command-line interface workflows
- `hp` - High-priority/hot-path workflows
- `eafix` - Emergency fix workflows
- `api` - API-related workflows

**Multi-Org Format:**
```
<org>.<project>
acme.billing
acme.inventory
```

### 5.2 Workflow Versioning

**When to Increment Workflow Version:**
- Major reordering of phases
- Significant addition/removal of lanes
- Breaking changes to workflow logic
- Change in workflow purpose or scope

**Version Format:** `v<N>` where N starts at 1

**Migration Strategy:**
- Old version remains frozen (read-only)
- New atoms created in new version
- Cross-version dependencies allowed via `atom_uid`

### 5.3 Atom Revision Handling

**When to Add Revision Suffix (-rN):**
- Semantic change to atom's behavior
- Input/output contract modification
- Role reassignment with different implementation

**Rules:**
- **Compatible change:** Same `atom_uid`, increment `-rN`
- **Breaking change:** New `atom_uid`, mark old as `superseded_by`

**Example Evolution:**
```yaml
# Original
atom_key: cli/dev-setup/v1/init/all/003
atom_uid: 01J9W4...ZQ

# Compatible revision
atom_key: cli/dev-setup/v1/init/all/003-r2
atom_uid: 01J9W4...ZQ  # SAME UID
rev_notes: "Added validation step"

# Breaking change
atom_key: cli/dev-setup/v1/init/all/003-r3
atom_uid: 01J9Y8...AB  # NEW UID
rev_notes: "Complete rewrite with new contract"
# Old atom marked: superseded_by: 01J9Y8...AB
```

### 5.4 Sequence Gap Strategy

To avoid mass renumbering when inserting atoms:

**Option 1: Number by Tens**
```
010, 020, 030, 040, ...
Insert at 025 between 020 and 030
```

**Option 2: Use Variants**
```
003, 004, 005
Insert 003-prep between 003 and 004
```

**Option 3: Rely on display_order**
```yaml
# Keep sequences unchanged
atom_key: .../003
display_order: 35  # Render after atom with display_order: 30
```

---

## 6. File Organization

### 6.1 Directory Structure

```
/atoms/
  ├── <workflow>/
  │   ├── <version>/
  │   │   ├── <phase>/
  │   │   │   ├── <lane>/
  │   │   │   │   ├── <seq>_<slug>.yaml
  │   │   │   │   └── ...
  │   │   │   └── ...
  │   │   └── ...
  │   └── ...
  └── ...
```

### 6.2 File Naming Convention

```
<seq>_<slug>.yaml
```

**Examples:**
```
001_detect_os_and_shell.yaml
042_run_integration_tests.yaml
123_merge_to_main.yaml
```

**Rules:**
- Sequence matches `atom_key` SEQ component
- Slug is kebab-case, descriptive
- Extension: `.yaml` (not `.yml`)

### 6.3 Complete Example

```
/atoms/
  ├── cli/
  │   ├── v1/
  │   │   ├── init/
  │   │   │   ├── all/
  │   │   │   │   ├── 001_detect_environment.yaml
  │   │   │   │   ├── 002_load_config.yaml
  │   │   │   │   └── 003_initialize_secrets.yaml
  │   │   │   ├── simple/
  │   │   │   └── complex/
  │   │   ├── exec/
  │   │   └── val/
  │   └── v2/
  └── hp/
```

---

## 7. Registry Architecture

### 7.1 Purpose

The registry is an **append-only ledger** that records all lifecycle events for every atom. It provides:

- Immutable audit trail
- Global uniqueness validation
- Historical tracking
- Dependency resolution

### 7.2 Primary Registry Format

**File:** `/registry/atoms.registry.jsonl`  
**Format:** JSON Lines (one event per line)

```jsonl
{"atom_uid":"01J9W4V4R8D8W0Q2Y5J7B0W4ZQ","atom_key":"cli/dev-setup/v1/init/all/003","event":"created","timestamp":"2025-10-05T16:22:00Z","meta":{"legacy_id":"atom_003"}}
{"atom_uid":"01J9W4V4R8D8W0Q2Y5J7B0W4ZQ","atom_key":"cli/dev-setup/v1/init/all/003-r2","event":"revised","timestamp":"2025-12-14T09:15:00Z","meta":{"rev_notes":"Added secret policy enforcement"}}
{"atom_uid":"01J9W4V4R8D8W0Q2Y5J7B0W4ZQ","event":"split","timestamp":"2026-03-02T11:30:00Z","meta":{"split_into":["01J9Y8...AB","01J9Y8...CD"]}}
```

### 7.3 Event Types

| Event | Description | Required Fields |
|-------|-------------|-----------------|
| `created` | New atom introduced | `atom_uid`, `atom_key` |
| `revised` | Compatible update | `atom_uid`, `atom_key` |
| `moved` | Phase/lane change | `atom_uid`, `prev_key`, `new_key` |
| `superseded` | Breaking replacement | `atom_uid`, `superseded_by` |
| `deprecated` | Scheduled for removal | `atom_uid` |
| `removed` | Retired from use | `atom_uid` |
| `split` | Split into multiple | `atom_uid`, `split_into` |
| `merged` | Consolidated | `atom_uid`, `merged_into` |

### 7.4 Derived Index

**File:** `/registry/atoms.index.json`  
**Generation:** Automated via CI pipeline  
**Purpose:** Fast lookup of current state

```json
{
  "01J9W4V4R8D8W0Q2Y5J7B0W4ZQ": {
    "atom_key": "cli/dev-setup/v1/init/all/003-r2",
    "status": "split",
    "split_into": ["01J9Y8...AB", "01J9Y8...CD"],
    "last_event": "2026-03-02T11:30:00Z",
    "history": [
      {"event": "created", "timestamp": "2025-10-05T16:22:00Z"},
      {"event": "revised", "timestamp": "2025-12-14T09:15:00Z"},
      {"event": "split", "timestamp": "2026-03-02T11:30:00Z"}
    ]
  }
}
```

### 7.5 Registry Operations

#### Append Event

```bash
echo '{"atom_uid":"01J9W4...","event":"created",...}' >> atoms.registry.jsonl
```

#### Rebuild Index

```bash
python tools/atoms/registry_tools.py build-index
```

#### Validate Registry

```bash
python tools/atoms/registry_tools.py validate
```

### 7.6 Registry Integrity Rules

1. **Append-Only:** Never edit or delete historical entries
2. **Chronological:** Timestamps must be monotonically increasing per UID
3. **Unique UIDs:** Each UID appears exactly once in `created` events
4. **Resolvable Refs:** All referenced UIDs must exist
5. **Signed Commits:** Registry changes require cryptographic signing (recommended)

---

## 8. Conversion from Legacy Workflows

### 8.1 Pre-Conversion Assessment

#### Inventory Checklist

- [ ] Count total atoms across all workflows
- [ ] Identify all dependency patterns (explicit and implicit)
- [ ] List all workflows, phases, and lanes
- [ ] Document existing numbering schemes
- [ ] Backup all source files
- [ ] Create conversion branch

#### Risk Assessment

**High-Risk Indicators:**
- Circular dependencies
- Duplicate atom numbers across workflows
- Ambiguous phase boundaries
- Shared atoms with unclear ownership

**Mitigation:**
- Create dependency graph before conversion
- Establish clear namespace boundaries
- Resolve circular deps before migration
- Assign single source of truth per atom

### 8.2 Conversion Process

#### Step 1: Preparation

```bash
# Create conversion workspace
git checkout -b conversion/two-id-migration
mkdir -p conversion/workspace
mkdir -p registry

# Backup existing atoms
cp -r atoms conversion/backup/

# Initialize registry
touch registry/atoms.registry.jsonl
```

#### Step 2: Generate Atom UIDs

For each existing atom:

```python
import ulid

# Generate new ULID
atom_uid = str(ulid.new())

# Store mapping: legacy_id -> atom_uid
mapping[legacy_id] = atom_uid
```

#### Step 3: Construct Atom Keys

```python
def build_atom_key(atom_metadata):
    """
    Construct atom_key from workflow context.
    """
    ns = atom_metadata['namespace']        # e.g., 'cli'
    wf = atom_metadata['workflow']         # e.g., 'dev-setup'
    version = atom_metadata['version']     # e.g., 'v1'
    phase = atom_metadata['phase']         # e.g., 'init'
    lane = atom_metadata['lane']           # e.g., 'all'
    seq = f"{atom_metadata['sequence']:03d}"  # e.g., '003'
    
    atom_key = f"{ns}/{wf}/{version}/{phase}/{lane}/{seq}"
    
    # Add variant if present
    if 'variant' in atom_metadata:
        atom_key += f"-{atom_metadata['variant']}"
    
    return atom_key
```

#### Step 4: Update Atom Files

Transform each atom file:

```python
# Read legacy atom
with open(f'atoms/atom_{legacy_id}.yaml') as f:
    atom = yaml.safe_load(f)

# Add Two-ID identifiers
atom['atom_uid'] = mapping[legacy_id]
atom['atom_key'] = build_atom_key(atom)
atom['legacy_id'] = f"atom_{legacy_id}"

# Rewrite dependencies
atom['deps'] = [mapping[dep_id] for dep_id in atom.get('deps', [])]

# Write to new location
new_path = construct_path(atom['atom_key'])
with open(new_path, 'w') as f:
    yaml.safe_dump(atom, f)
```

#### Step 5: Populate Registry

```python
for atom_uid, atom_key in conversions:
    event = {
        "atom_uid": atom_uid,
        "atom_key": atom_key,
        "event": "created",
        "timestamp": datetime.utcnow().isoformat() + 'Z',
        "meta": {"legacy_id": legacy_id}
    }
    append_to_registry(event)
```

#### Step 6: Validation

```bash
# Run full validation suite
python tools/atoms/atom_validator.py --all

# Check for issues:
# - Duplicate UIDs
# - Malformed atom_keys
# - Unresolvable dependencies
# - Registry inconsistencies

# Generate validation report
python tools/atoms/atom_validator.py --report > validation_report.txt
```

#### Step 7: Finalization

```bash
# Commit conversion
git add atoms/ registry/
git commit -m "feat: migrate to Two-ID system

- Generated UIDs for all atoms
- Restructured file organization
- Initialized registry
- Updated all dependencies

Affected atoms: 1,247
Migration tool: conversion/migrate.py"

# Freeze legacy numbering
echo "DEPRECATED - Use atom_uid only" > LEGACY_ATOMS_FROZEN.txt
```

### 8.3 Conversion Validation Gates

#### Pre-Commit Validation

```yaml
# .pre-commit-config.yaml
- repo: local
  hooks:
    - id: validate-atoms
      name: Validate Atom Schema
      entry: python tools/atoms/atom_validator.py
      language: system
      pass_filenames: false
```

#### CI Pipeline Validation

```yaml
# .github/workflows/atoms-validation.yml
name: Atom Validation
on: [push, pull_request]
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Validate Atoms
        run: |
          python tools/atoms/atom_validator.py --all
          python tools/atoms/registry_tools.py validate
          python tools/atoms/registry_tools.py build-index
```

#### Validation Checks

1. **Schema Compliance:** Every atom matches canonical schema
2. **UID Uniqueness:** No duplicate `atom_uid` values
3. **Key Format:** All `atom_key` values match regex
4. **Dependency Resolution:** All `deps` point to existing UIDs
5. **Registry Consistency:** Registry matches filesystem state
6. **Legacy Mapping:** All legacy IDs accounted for

### 8.4 Post-Conversion Tasks

- [ ] Update documentation to reference new system
- [ ] Train team on Two-ID operations
- [ ] Archive legacy atom files
- [ ] Update automation scripts to use `atom_uid`
- [ ] Monitor for issues over 1-2 sprint cycles
- [ ] Delete legacy backup after successful validation period

---

## 9. Lifecycle Operations

### 9.1 Adding a New Atom

#### Process

1. Generate `atom_uid`
2. Construct `atom_key`
3. Create atom YAML file
4. Append registry event
5. Validate and commit

#### Example

```bash
# Generate UID
atom_uid=$(python -c "import ulid; print(ulid.new())")

# Create atom file
cat > atoms/cli/v1/exec/all/045_new_validation.yaml <<EOF
atom_uid: ${atom_uid}
atom_key: cli/v1/exec/all/045
title: "Run new validation checks"
role: "qa_test_agent"
deps:
  - 01J9W4R0T1A5M3P8Q6K2N7V5ZW
status: active
EOF

# Register creation event
echo "{\"atom_uid\":\"${atom_uid}\",\"atom_key\":\"cli/v1/exec/all/045\",\"event\":\"created\",\"timestamp\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"}" >> registry/atoms.registry.jsonl

# Validate
python tools/atoms/atom_validator.py

# Commit
git add atoms/cli/v1/exec/all/045_new_validation.yaml registry/
git commit -m "feat(exec): add validation checks

Atom: ${atom_uid} (cli/v1/exec/all/045)"
```

### 9.2 Deprecating an Atom

#### Process

1. Update atom status to `deprecated`
2. Add `superseded_by` if replacement exists
3. Append registry event
4. Update dependent atoms (optional)

#### Example

```yaml
# In atom file
atom_uid: 01J9W4V4R8D8W0Q2Y5J7B0W4ZQ
status: deprecated
superseded_by: 01J9Y8XYZABC123DEF456GH789
deprecated_reason: "Replaced by improved implementation"
deprecated_date: "2025-11-01"
```

```jsonl
# Registry event
{"atom_uid":"01J9W4V4R8D8W0Q2Y5J7B0W4ZQ","event":"deprecated","timestamp":"2025-11-01T00:00:00Z","meta":{"superseded_by":"01J9Y8XYZABC123DEF456GH789","reason":"Improved implementation"}}
```

### 9.3 Removing an Atom

#### Pre-Removal Checklist

- [ ] Atom status is `deprecated` for at least one release cycle
- [ ] No active dependencies reference this atom
- [ ] Replacement atom (if any) is stable
- [ ] Documentation updated

#### Process

```yaml
# Update atom file (keep for archive)
status: removed
removed_date: "2025-12-01"
```

```jsonl
# Registry event
{"atom_uid":"01J9W4V4R8D8W0Q2Y5J7B0W4ZQ","event":"removed","timestamp":"2025-12-01T00:00:00Z"}
```

### 9.4 Reordering Atoms

#### Preferred Method: display_order

```yaml
# Keep original atom_key unchanged
atom_key: cli/v1/exec/all/042
display_order: 55  # Execute after atom with display_order 50
```

#### Alternative: Update atom_key

```yaml
# Original
atom_key: cli/v1/exec/all/042

# After moving to different phase
atom_key: cli/v1/val/all/042-r2  # Added revision suffix
```

```jsonl
# Registry event
{"atom_uid":"01J9W4...","event":"moved","timestamp":"2025-11-15T10:00:00Z","meta":{"prev_key":"cli/v1/exec/all/042","new_key":"cli/v1/val/all/042-r2"}}
```

### 9.5 Revising an Atom

#### Compatible Revision

```yaml
# Same atom_uid, increment revision
atom_uid: 01J9W4V4R8D8W0Q2Y5J7B0W4ZQ
atom_key: cli/v1/init/all/003-r2  # Was 003, now 003-r2
rev_notes: "Added input validation"
```

```jsonl
{"atom_uid":"01J9W4V4R8D8W0Q2Y5J7B0W4ZQ","atom_key":"cli/v1/init/all/003-r2","event":"revised","timestamp":"2025-11-20T14:30:00Z","meta":{"rev_notes":"Added input validation"}}
```

#### Breaking Revision

```yaml
# New atom_uid, mark old as superseded
# NEW ATOM
atom_uid: 01J9Y8NEWUID123456789ABCDEF
atom_key: cli/v1/init/all/003-r3
title: "Initialize .env (v2 implementation)"
rev_notes: "Complete rewrite with new contract"

# OLD ATOM (updated)
atom_uid: 01J9W4V4R8D8W0Q2Y5J7B0W4ZQ
status: superseded
superseded_by: 01J9Y8NEWUID123456789ABCDEF
```

### 9.6 Splitting an Atom

#### Process

1. Create new atoms with new UIDs
2. Mark original atom as `split`
3. Update dependencies
4. Register split event

#### Example

```yaml
# ORIGINAL (updated)
atom_uid: 01J9W4V4R8D8W0Q2Y5J7B0W4ZQ
status: split
split_into:
  - 01J9Y8SPLIT1AAA111222333444
  - 01J9Y8SPLIT2BBB555666777888

# NEW ATOM 1
atom_uid: 01J9Y8SPLIT1AAA111222333444
atom_key: cli/v1/init/all/003a
title: "Initialize .env template"

# NEW ATOM 2
atom_uid: 01J9Y8SPLIT2BBB555666777888
atom_key: cli/v1/init/all/003b
title: "Validate secrets policy"
```

```jsonl
{"atom_uid":"01J9W4V4R8D8W0Q2Y5J7B0W4ZQ","event":"split","timestamp":"2025-12-01T09:00:00Z","meta":{"split_into":["01J9Y8SPLIT1AAA111222333444","01J9Y8SPLIT2BBB555666777888"]}}
{"atom_uid":"01J9Y8SPLIT1AAA111222333444","atom_key":"cli/v1/init/all/003a","event":"created","timestamp":"2025-12-01T09:00:01Z"}
{"atom_uid":"01J9Y8SPLIT2BBB555666777888","atom_key":"cli/v1/init/all/003b","event":"created","timestamp":"2025-12-01T09:00:02Z"}
```

### 9.7 Merging Atoms

#### Process

1. Create new consolidated atom
2. Mark original atoms as `merged`
3. Update dependencies
4. Register merge events

#### Example

```yaml
# NEW CONSOLIDATED ATOM
atom_uid: 01J9Y8MERGED999888777666555
atom_key: cli/v1/init/all/005
title: "Initialize environment (consolidated)"
merged_from:
  - 01J9W4ATOM1111111111111111
  - 01J9W4ATOM2222222222222222

# ORIGINAL ATOM 1 (updated)
atom_uid: 01J9W4ATOM1111111111111111
status: merged
merged_into: 01J9Y8MERGED999888777666555

# ORIGINAL ATOM 2 (updated)
atom_uid: 01J9W4ATOM2222222222222222
status: merged
merged_into: 01J9Y8MERGED999888777666555
```

```jsonl
{"atom_uid":"01J9Y8MERGED999888777666555","atom_key":"cli/v1/init/all/005","event":"created","timestamp":"2025-12-05T11:00:00Z","meta":{"merged_from":["01J9W4ATOM1111111111111111","01J9W4ATOM2222222222222222"]}}
{"atom_uid":"01J9W4ATOM1111111111111111","event":"merged","timestamp":"2025-12-05T11:00:01Z","meta":{"merged_into":"01J9Y8MERGED999888777666555"}}
{"atom_uid":"01J9W4ATOM2222222222222222","event":"merged","timestamp":"2025-12-05T11:00:02Z","meta":{"merged_into":"01J9Y8MERGED999888777666555"}}
```

---

## 10. Automation & Validation

### 10.1 Validation Architecture

```
┌──────────────┐
│ Pre-Commit   │ → Fast schema validation
│ Hooks        │   UID format check
└──────┬───────┘
       │
       ↓
┌──────────────┐
│ CI Pipeline  │ → Comprehensive validation
│              │   Registry consistency
│              │   Dependency resolution
└──────┬───────┘
       │
       ↓
┌──────────────┐
│ Nightly      │ → Deep analysis
│ Audit        │   Metrics collection
└──────────────┘
```

### 10.2 Pre-Commit Validation

#### Configuration

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: validate-atom-schema
        name: Validate Atom Schema
        entry: python tools/atoms/atom_validator.py --changed
        language: system
        files: 'atoms/.*\.yaml$'
        
      - id: validate-atom-uids
        name: Check UID Uniqueness
        entry: python tools/atoms/uid_checker.py
        language: system
        files: 'atoms/.*\.yaml$'
```

#### Checks Performed

1. YAML syntax validity
2. Required fields present
3. `atom_uid` format compliance
4. `atom_key` regex match
5. Basic dependency reference check

### 10.3 CI Pipeline Validation

#### GitHub Actions Example

```yaml
name: Atom Validation Suite
on: [push, pull_request]

jobs:
  validate-atoms:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install Dependencies
        run: pip install -r tools/requirements.txt
      
      - name: Schema Validation
        run: python tools/atoms/atom_validator.py --all
      
      - name: UID Uniqueness Check
        run: python tools/atoms/uid_checker.py --strict
      
      - name: Dependency Resolution
        run: python tools/atoms/dep_resolver.py --verify-all
      
      - name: Registry Consistency
        run: python tools/atoms/registry_tools.py validate
      
      - name: Build Registry Index
        run: python tools/atoms/registry_tools.py build-index
      
      - name: Generate Validation Report
        run: python tools/atoms/report_generator.py > validation_report.md
      
      - name: Upload Artifacts
        uses: actions/upload-artifact@v3
        with:
          name: validation-report
          path: validation_report.md
```

### 10.4 Validation Tooling

#### atom_validator.py

```python
#!/usr/bin/env python3
"""
Atom validation tool - ensures schema compliance.
"""
import sys
from pathlib import Path
import yaml
import re

ATOM_KEY_REGEX = r'^[a-z0-9-]+/[a-z0-9-]+/v[0-9]+/[a-z0-9-]+/[a-z0-9-]+/[0-9]{3}(-[a-z0-9-]+)?(-r[0-9]+)?$'
ULID_REGEX = r'^[0-9A-HJKMNP-TV-Z]{26}$'

def validate_atom(file_path):
    """Validate single atom file."""
    with open(file_path) as f:
        atom = yaml.safe_load(f)
    
    errors = []
    
    # Check required fields
    if 'atom_uid' not in atom:
        errors.append("Missing required field: atom_uid")
    elif not re.match(ULID_REGEX, atom['atom_uid']):
        errors.append(f"Invalid atom_uid format: {atom['atom_uid']}")
    
    if 'atom_key' not in atom:
        errors.append("Missing required field: atom_key")
    elif not re.match(ATOM_KEY_REGEX, atom['atom_key']):
        errors.append(f"Invalid atom_key format: {atom['atom_key']}")
    
    if 'title' not in atom:
        errors.append("Missing required field: title")
    
    if 'role' not in atom:
        errors.append("Missing required field: role")
    
    return errors

if __name__ == '__main__':
    atoms_dir = Path('atoms')
    all_errors = {}
    
    for atom_file in atoms_dir.rglob('*.yaml'):
        errors = validate_atom(atom_file)
        if errors:
            all_errors[str(atom_file)] = errors
    
    if all_errors:
        print("VALIDATION ERRORS:")
        for file, errors in all_errors.items():
            print(f"\n{file}:")
            for error in errors:
                print(f"  - {error}")
        sys.exit(1)
    
    print("✓ All atoms valid")
```

#### uid_checker.py

```python
#!/usr/bin/env python3
"""
Check for duplicate atom_uid values.
"""
import sys
from pathlib import Path
import yaml
from collections import defaultdict

def check_uid_uniqueness():
    """Verify all UIDs are unique."""
    uid_to_files = defaultdict(list)
    
    for atom_file in Path('atoms').rglob('*.yaml'):
        with open(atom_file) as f:
            atom = yaml.safe_load(f)
        
        if 'atom_uid' in atom:
            uid_to_files[atom['atom_uid']].append(str(atom_file))
    
    duplicates = {uid: files for uid, files in uid_to_files.items() if len(files) > 1}
    
    if duplicates:
        print("DUPLICATE UIDs FOUND:")
        for uid, files in duplicates.items():
            print(f"\n{uid}:")
            for file in files:
                print(f"  - {file}")
        sys.exit(1)
    
    print(f"✓ All {len(uid_to_files)} UIDs unique")

if __name__ == '__main__':
    check_uid_uniqueness()
```

### 10.5 Registry Tools

#### build-index Command

Generates derived index from registry:

```python
def build_index():
    """Build atoms.index.json from registry."""
    index = {}
    
    with open('registry/atoms.registry.jsonl') as f:
        for line in f:
            event = json.loads(line)
            uid = event['atom_uid']
            
            if uid not in index:
                index[uid] = {
                    'history': [],
                    'current_status': 'active'
                }
            
            index[uid]['history'].append(event)
            
            # Update current state based on event type
            if event['event'] == 'removed':
                index[uid]['current_status'] = 'removed'
            elif event['event'] == 'deprecated':
                index[uid]['current_status'] = 'deprecated'
            # ... handle other events
    
    with open('registry/atoms.index.json', 'w') as f:
        json.dump(index, f, indent=2)
```

---

## 11. Governance Model

### 11.1 Roles & Responsibilities

| Role | Responsibilities | Authority |
|------|------------------|-----------|
| **Atom Owner** | Define atom metadata, maintain correctness, request lifecycle changes | Create, update own atoms |
| **Workflow Maintainer** | Validate cross-atom dependencies, approve major changes, ensure coherence | Approve additions/removals within workflow |
| **Registry Administrator** | Manage ledger, perform backups, handle corruption recovery | Full registry access |
| **Automation Guardian** | Maintain validation tools, CI pipelines, monitoring dashboards | Deploy validation updates |
| **Auditor** | Periodic compliance reviews, integrity checks, policy enforcement | Read-only access, escalation authority |

### 11.2 Change Approval Matrix

| Change Type | Requires Approval From |
|-------------|----------------------|
| Add new atom | Workflow Maintainer |
| Update atom metadata | Atom Owner |
| Deprecate atom | Workflow Maintainer + downstream consumers |
| Remove atom | Workflow Maintainer + Registry Administrator |
| Split/merge atoms | Workflow Maintainer + all affected Atom Owners |
| Modify registry directly | Registry Administrator only (emergency) |

### 11.3 Commit Message Standards

```
<type>(<scope>): <subject>

Atom: <atom_uid> (<atom_key>)

<body>

<footer>
```

**Types:** `feat`, `fix`, `refactor`, `docs`, `chore`  
**Scopes:** Phase names (`init`, `exec`, `val`, etc.)

**Example:**

```
feat(exec): add integration test validation

Atom: 01J9Y8ABC123XYZ456DEF789GHI (cli/v1/exec/all/047)

Adds comprehensive integration test suite for API endpoints.
Includes retry logic and detailed error reporting.

Refs: #1234
```

### 11.4 Review Process

1. **Automated Validation:** Pre-commit hooks + CI pipeline
2. **Peer Review:** At least one workflow maintainer approval
3. **Dependency Impact:** Automated analysis of affected atoms
4. **Documentation:** Updates to related docs required
5. **Merge:** Squash or rebase per project policy

---

## 12. Error Handling & Recovery

### 12.1 Common Errors

#### Duplicate UID

**Symptom:** Validation fails with "Duplicate atom_uid detected"

**Cause:** Manual UID creation or file copy without regenerating UID

**Resolution:**
```bash
# Generate new UID for duplicate
new_uid=$(python -c "import ulid; print(ulid.new())")

# Update atom file
sed -i "s/atom_uid: <OLD_UID>/atom_uid: ${new_uid}/" path/to/atom.yaml

# Append correction event
echo "{\"atom_uid\":\"${new_uid}\",\"event\":\"corrected\",\"timestamp\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\",\"meta\":{\"reason\":\"Duplicate UID resolved\"}}" >> registry/atoms.registry.jsonl
```

#### Broken Dependency

**Symptom:** Validation fails with "Unresolvable dependency"

**Cause:** Referenced UID doesn't exist, or atom was removed without updating dependents

**Resolution:**
```bash
# Find all atoms with broken dep
grep -r "broken_uid" atoms/

# Either:
# 1. Remove the dependency if no longer needed
# 2. Update to correct UID
# 3. Restore removed atom
```

#### Malformed atom_key

**Symptom:** Validation fails with "Invalid atom_key format"

**Resolution:**
```bash
# Review regex: ^[a-z0-9-]+/[a-z0-9-]+/v[0-9]+/...
# Common issues:
# - Uppercase letters
# - Missing version prefix 'v'
# - Wrong separator (underscore instead of hyphen)
# - Non-zero-padded sequence

# Fix format and recommit
```

### 12.2 Registry Corruption Recovery

#### Backup Strategy

```bash
# Daily automated backup
0 2 * * * tar -czf /backups/registry-$(date +\%Y\%m\%d).tar.gz registry/
```

#### Recovery Procedure

```bash
# 1. Verify corruption
python tools/atoms/registry_tools.py validate

# 2. Restore from backup
cp /backups/registry-20251005.tar.gz ./
tar -xzf registry-20251005.tar.gz

# 3. Replay missing events
git log --since="2025-10-05" --grep="Atom:" --format="%H %s" | \
  while read commit msg; do
    # Extract and replay events
  done

# 4. Rebuild index
python tools/atoms/registry_tools.py build-index

# 5. Validate
python tools/atoms/registry_tools.py validate
```

### 12.3 Emergency Procedures

#### Freeze All Changes

```bash
# Enable read-only mode
touch registry/.READONLY

# Update pre-commit hook to check for flag
if [ -f registry/.READONLY ]; then
  echo "Registry is in read-only mode"
  exit 1
fi
```

#### Rollback Workflow

```bash
# Identify last known good state
git log --all --grep="validation: passed" -1

# Create rollback branch
git checkout -b emergency/rollback <good_commit>

# Force update main (with extreme caution)
git push origin emergency/rollback:main --force
```

---

## 13. Security & Compliance

### 13.1 Security Properties

**UID Non-Guessability**
- ULID provides 80 bits of random entropy
- Collision probability: < 10^-15 for 100k atoms
- Not sequentially predictable

**Registry Integrity**
- Append-only design prevents tampering
- Cryptographic signing recommended for regulated environments
- Git commit signatures provide chain of custody

**Access Control**
- File system permissions protect atom definitions
- Registry modifications require commit access
- Audit log via Git history

### 13.2 Compliance Features

**Audit Trail**
- Complete history of all atom changes
- Immutable ledger in registry
- Git commit messages link changes to issues/tickets

**Traceability**
- Every atom has permanent, unique identifier
- Cross-workflow dependencies explicitly documented
- Legacy ID mapping preserves historical context

**Regulatory Alignment**
- Supports SOC 2, ISO 27001 change management requirements
- Provides evidence for CMMI Level 3+ process maturity
- Enables FDA 21 CFR Part 11 compliance (with signing)

### 13.3 Cryptographic Signing

#### GPG Commit Signing

```bash
# Configure Git
git config --global user.signingkey <GPG_KEY_ID>
git config --global commit.gpgsign true

# All atom changes automatically signed
git commit -am "feat(init): add new validation"
```

#### Registry Event Signing

```python
import hashlib
import hmac

def sign_event(event, secret_key):
    """Add HMAC signature to registry event."""
    payload = json.dumps(event, sort_keys=True)
    signature = hmac.new(
        secret_key.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
    
    event['signature'] = signature
    return event
```

---

## 14. Performance Considerations

### 14.1 Scalability Metrics

| Atom Count | Registry Size | Index Build Time | Validation Time |
|------------|---------------|------------------|-----------------|
| 1,000 | ~500 KB | <1s | <2s |
| 10,000 | ~5 MB | ~3s | ~10s |
| 100,000 | ~50 MB | ~30s | ~90s |
| 1,000,000 | ~500 MB | ~5min | ~15min |

### 14.2 Optimization Strategies

**Incremental Validation**
```bash
# Only validate changed atoms
git diff --name-only --diff-filter=ACM | grep '^atoms/' | \
  xargs python tools/atoms/atom_validator.py
```

**Parallel Processing**
```python
from multiprocessing import Pool

def validate_batch(atom_files):
    with Pool(processes=8) as pool:
        results = pool.map(validate_atom, atom_files)
    return results
```

**Index Caching**
```python
# Cache index in memory for repeated lookups
class AtomIndex:
    _cache = None
    _cache_time = None
    
    @classmethod
    def get(cls):
        if cls._cache is None or cls._is_stale():
            cls._cache = cls._load_index()
            cls._cache_time = time.time()
        return cls._cache
```

### 14.3 Large-Scale Deployment

**Sharded Registry**
```
registry/
  ├── atoms.registry.00.jsonl  # UIDs starting with 00-0F
  ├── atoms.registry.01.jsonl  # UIDs starting with 10-1F
  └── ...
```

**Distributed Validation**
```yaml
# CI matrix for parallel validation
jobs:
  validate:
    strategy:
      matrix:
        shard: [0, 1, 2, 3, 4, 5, 6, 7]
    steps:
      - run: validate_shard.py --shard ${{ matrix.shard }}
```

---

## 15. Tooling Reference

### 15.1 Core Utilities

| Tool | Purpose | Location |
|------|---------|----------|
| `atom_validator.py` | Schema validation | `tools/atoms/` |
| `uid_checker.py` | UID uniqueness | `tools/atoms/` |
| `dep_resolver.py` | Dependency analysis | `tools/atoms/` |
| `registry_tools.py` | Registry operations | `tools/atoms/` |
| `id_utils.py` | UID generation | `tools/atoms/` |
| `atom_schema.json` | JSON Schema definition | `tools/atoms/` |

### 15.2 Command Reference

#### Generate New UID

```bash
python tools/atoms/id_utils.py --new
# Output: 01J9Y8ABC123XYZ456DEF789GHI
```

#### Validate All Atoms

```bash
python tools/atoms/atom_validator.py --all
```

#### Validate Changed Atoms Only

```bash
python tools/atoms/atom_validator.py --changed
```

#### Check UID Uniqueness

```bash
python tools/atoms/uid_checker.py --strict
```

#### Resolve Dependencies

```bash
# Check if all deps are resolvable
python tools/atoms/dep_resolver.py --verify-all

# Show dependency tree for specific atom
python tools/atoms/dep_resolver.py --tree <atom_uid>

# Find all dependents of an atom
python tools/atoms/dep_resolver.py --dependents <atom_uid>
```

#### Registry Operations

```bash
# Validate registry integrity
python tools/atoms/registry_tools.py validate

# Build index from registry
python tools/atoms/registry_tools.py build-index

# Query registry history
python tools/atoms/registry_tools.py history <atom_uid>

# Export registry as graph
python tools/atoms/registry_tools.py export-graph --format dot
```

### 15.3 Integration Examples

#### Pre-Commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit

# Validate changed atoms
git diff --cached --name-only --diff-filter=ACM | grep '^atoms/' | \
  xargs -r python tools/atoms/atom_validator.py || exit 1

# Check UID uniqueness
python tools/atoms/uid_checker.py || exit 1

echo "✓ Atom validation passed"
```

#### CI Integration

```yaml
# .github/workflows/atoms.yml
name: Atom Validation
on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
      - run: pip install -r tools/requirements.txt
      - run: python tools/atoms/atom_validator.py --all
      - run: python tools/atoms/uid_checker.py --strict
      - run: python tools/atoms/dep_resolver.py --verify-all
      - run: python tools/atoms/registry_tools.py validate
```

---

## 16. Quick Reference

### 16.1 Cheat Sheet

#### Creating New Atom

```bash
# 1. Generate UID
uid=$(python tools/atoms/id_utils.py --new)

# 2. Create file
cat > atoms/<workflow>/<version>/<phase>/<lane>/<seq>_<name>.yaml <<EOF
atom_uid: ${uid}
atom_key: <ns>/<workflow>/<version>/<phase>/<lane>/<seq>
title: "Descriptive title"
role: "role_name"
deps: []
status: active
EOF

# 3. Register
echo "{\"atom_uid\":\"${uid}\",\"atom_key\":\"...\",\"event\":\"created\",\"timestamp\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"}" >> registry/atoms.registry.jsonl

# 4. Validate & commit
python tools/atoms/atom_validator.py
git add atoms/ registry/
git commit -m "feat(<phase>): <description>

Atom: ${uid}"
```

#### Finding an Atom

```bash
# By UID
grep -r "atom_uid: 01J9W4..." atoms/

# By key pattern
find atoms/ -path "*cli/v1/init/all/*"

# By title
grep -r "title: \"Initialize" atoms/
```

#### Checking Dependencies

```bash
# What does this atom depend on?
python tools/atoms/dep_resolver.py --deps <atom_uid>

# What depends on this atom?
python tools/atoms/dep_resolver.py --dependents <atom_uid>

# Full dependency tree
python tools/atoms/dep_resolver.py --tree <atom_uid>
```

### 16.2 Status Values

| Status | Meaning | Next Actions |
|--------|---------|--------------|
| `active` | In current use | Normal operations |
| `deprecated` | Scheduled for removal | Plan migration |
| `removed` | No longer in use | Archive only |
| `split` | Divided into multiple | Use new atoms |
| `merged` | Consolidated | Use merged atom |

### 16.3 Event Types

| Event | When to Use |
|-------|-------------|
| `created` | New atom added |
| `revised` | Compatible update |
| `moved` | Phase/lane change |
| `superseded` | Breaking replacement |
| `deprecated` | Mark for future removal |
| `removed` | Final removal |
| `split` | Atom divided |
| `merged` | Atoms consolidated |

### 16.4 Validation Regex

```regex
# atom_key format
^[a-z0-9-]+/[a-z0-9-]+/v[0-9]+/[a-z0-9-]+/[a-z0-9-]+/[0-9]{3}(-[a-z0-9-]+)?(-r[0-9]+)?$

# ULID format
^[0-9A-HJKMNP-TV-Z]{26}$

# UUIDv7 format
^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-7[0-9a-fA-F]{3}-[89ab][0-9a-fA-F]{3}-[0-9a-fA-F]{12}$
```

### 16.5 Common Patterns

#### Sequential Atom IDs

```yaml
cli/v1/init/all/001
cli/v1/init/all/002
cli/v1/init/all/003
```

#### Platform Variants

```yaml
cli/v1/init/all/003-win
cli/v1/init/all/003-linux
cli/v1/init/all/003-mac
```

#### Revisions

```yaml
cli/v1/init/all/003      # Original
cli/v1/init/all/003-r2   # Compatible revision
cli/v1/init/all/003-r3   # Another revision
```

#### Split Atoms

```yaml
cli/v1/init/all/003      # Original (now split)
cli/v1/init/all/003a     # First part
cli/v1/init/all/003b     # Second part
```

---

## Appendix A: Schema Definition

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Atomic Task Schema",
  "type": "object",
  "required": ["atom_uid", "atom_key", "title", "role"],
  "properties": {
    "atom_uid": {
      "type": "string",
      "pattern": "^[0-9A-HJKMNP-TV-Z]{26}$",
      "description": "Globally unique identifier (ULID)"
    },
    "atom_key": {
      "type": "string",
      "pattern": "^[a-z0-9-]+/[a-z0-9-]+/v[0-9]+/[a-z0-9-]+/[a-z0-9-]+/[0-9]{3}(-[a-z0-9-]+)?(-r[0-9]+)?$",
      "description": "Human-readable structured key"
    },
    "title": {
      "type": "string",
      "maxLength": 100,
      "description": "Brief descriptive title"
    },
    "description": {
      "type": "string",
      "description": "Detailed explanation of atom's purpose"
    },
    "role": {
      "type": "string",
      "description": "Responsible role or agent"
    },
    "inputs": {
      "type": "array",
      "items": {"type": "string"},
      "description": "Required input artifacts"
    },
    "outputs": {
      "type": "array",
      "items": {"type": "string"},
      "description": "Produced output artifacts"
    },
    "deps": {
      "type": "array",
      "items": {
        "type": "string",
        "pattern": "^[0-9A-HJKMNP-TV-Z]{26}$"
      },
      "description": "Array of prerequisite atom UIDs"
    },
    "status": {
      "type": "string",
      "enum": ["active", "deprecated", "removed", "split", "merged"],
      "default": "active"
    },
    "legacy_id": {
      "type": "string",
      "description": "Original numeric identifier"
    },
    "display_order": {
      "type": "integer",
      "description": "Override natural sequence ordering"
    },
    "rev_notes": {
      "type": "string",
      "description": "Explanation of revisions"
    },
    "superseded_by": {
      "type": "string",
      "pattern": "^[0-9A-HJKMNP-TV-Z]{26}$",
      "description": "UID of replacement atom"
    },
    "split_into": {
      "type": "array",
      "items": {
        "type": "string",
        "pattern": "^[0-9A-HJKMNP-TV-Z]{26}$"
      },
      "description": "UIDs of atoms this was split into"
    },
    "merged_into": {
      "type": "string",
      "pattern": "^[0-9A-HJKMNP-TV-Z]{26}$",
      "description": "UID of consolidated atom"
    }
  }
}
```

---

## Appendix B: Glossary

| Term | Definition |
|------|------------|
| **Atom** | Smallest independently verifiable unit of work |
| **atom_uid** | Globally unique, immutable identifier (ULID/UUIDv7) |
| **atom_key** | Human-readable, structured identifier |
| **Namespace** | Top-level organizational domain |
| **Workflow** | Collection of related atoms organized into phases |
| **Phase** | Logical grouping within a workflow (e.g., init, exec, val) |
| **Lane** | Complexity classification (simple, moderate, complex, all) |
| **Sequence** | Numeric position within phase and lane |
| **Registry** | Append-only ledger of all atom lifecycle events |
| **Index** | Derived data structure for fast lookups |
| **Dependency** | Prerequisite relationship between atoms |
| **Lifecycle Event** | Recorded change in atom status (created, revised, etc.) |

---

## Appendix C: FAQ

**Q: Can I reuse an atom_uid after removing an atom?**  
A: No. UIDs are permanent. Reusing violates uniqueness guarantees.

**Q: What if I need to change an atom's phase?**  
A: Update the atom_key (add -r2 suffix), keep atom_uid, register "moved" event.

**Q: How do I handle circular dependencies?**  
A: Circular dependencies indicate design flaw. Refactor to break cycle before conversion.

**Q: Can atoms depend on atoms from different workflows?**  
A: Yes. Use atom_uid for cross-workflow dependencies.

**Q: What's the maximum number of atoms supported?**  
A: Tested to 100k atoms. Theoretical limit >1M with sharding.

**Q: Do I need cryptographic signing?**  
A: Recommended for regulated environments (finance, healthcare, aerospace). Optional otherwise.

**Q: Can I use sequential UIDs instead of ULIDs?**  
A: Not recommended. Sequential IDs enable prediction and lose collision resistance.

**Q: How do I migrate 10,000+ existing atoms?**  
A: Use batch conversion script (Section 8), validate incrementally, allow 2-4 week testing period.

---

## Appendix D: Document Revision History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-10-05 | Initial release |

---

**End of Document**