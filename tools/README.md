# Atomic Workflow Tooling

Comprehensive tooling suite for converting, validating, and managing atomic tasks in the Two-ID Atomic Workflow System.

## Overview

This tooling suite provides:

- **Converters**: Transform various file formats to Atom YAML format
  - `md2atom.py`: Markdown to Atom
  - `ps2atom.py`: PowerShell scripts to Atom
  - `py2atom.py`: Python scripts to Atom
  - `simple2atom.py`: Simple JSON to Atom

- **Supporting Tools**:
  - `atom_validator.py`: Validates atom schema compliance
  - `doc_indexer.py`: Builds hierarchical documentation indexes
  - `log_miner.py`: Normalizes logs and identifies repeated patterns

- **Utilities**:
  - `id_utils.py`: ULID generation and validation

## Installation

```bash
# Install dependencies
pip install -r tools/requirements.txt
```

## Quick Start

### Converting Files to Atoms

#### Markdown to Atom
```bash
python3 tools/atoms/md2atom.py input.md \
  --namespace cli \
  --workflow dev-setup \
  --version v1 \
  --phase init \
  --lane all \
  --sequence 1 \
  --output atoms/cli/v1/init/all/001_task.yaml
```

#### PowerShell to Atom
```bash
python3 tools/atoms/ps2atom.py script.ps1 \
  --namespace hp \
  --workflow pipeline \
  --version v2 \
  --phase exec \
  --lane all \
  --sequence 5 \
  --output atoms/hp/v2/exec/all/005_task.yaml
```

#### Python to Atom
```bash
python3 tools/atoms/py2atom.py script.py \
  --namespace cli \
  --workflow pipeline \
  --version v1 \
  --phase exec \
  --lane all \
  --sequence 3
```

#### Simple JSON to Atom
```bash
python3 tools/atoms/simple2atom.py task.json \
  --namespace db \
  --workflow migrations \
  --version v1 \
  --phase exec \
  --lane all \
  --sequence 1
```

### Validating Atoms

```bash
# Validate a single file
python3 tools/atoms/atom_validator.py atoms/cli/v1/init/all/001_task.yaml

# Validate a directory
python3 tools/atoms/atom_validator.py atoms/ --strict

# Validate only changed files
python3 tools/atoms/atom_validator.py --changed --strict
```

### Building Documentation Indexes

```bash
# Build index for documentation directory
python3 tools/atoms/doc_indexer.py /path/to/docs

# Specify output directory
python3 tools/atoms/doc_indexer.py /path/to/docs --output-dir /output/path
```

### Mining Logs

```bash
# Mine a single log file
python3 tools/atoms/log_miner.py app.log --output analysis.json --min-count 3

# Mine multiple log files
python3 tools/atoms/log_miner.py logs/*.log --output analysis.json

# Filter patterns
python3 tools/atoms/log_miner.py logs/ --output analysis.json --pattern "ERROR"
```

## Converter Details

### md2atom.py

Converts Markdown files to Atom format following strict heading conventions.

**Expected Markdown Structure:**
```markdown
# Task Title

## Description

Task description goes here.

## Inputs

- input1.txt
- input2.txt

## Outputs

- output.txt

## Dependencies

- 01K6W1BSSCAZGCG5M81WJHRSXK

## Role

orchestrator
```

**Features:**
- Generates ULID for `atom_uid`
- Builds `atom_key` from context parameters
- Extracts inputs, outputs, and dependencies as lists
- Supports pragma overrides via `--role` flag

### ps2atom.py

Converts PowerShell scripts to Atom format.

**Extraction Methods:**
1. Comment-based help blocks (`.SYNOPSIS`, `.DESCRIPTION`)
2. Pragmas: `# Role:`, `# DependsOn:`, `# Inputs:`, `# Outputs:`
3. Automatic file pattern scanning

**Example Script:**
```powershell
<#
.SYNOPSIS
Validates PowerShell environment

.DESCRIPTION
Checks for required modules and sets up paths
#>

# Role: validator
# Inputs: modules.json
# Outputs: validation.log

Get-Content "modules.json"
Set-Content "validation.log" -Value "Complete"
```

**Features:**
- Pragma overrides take precedence over scanning
- Detects common PowerShell cmdlets for file I/O
- Validates ULID format for dependencies

### py2atom.py

Converts Python scripts to Atom format.

**Extraction Methods:**
1. Module docstring (first line = title, rest = description)
2. Pragmas: `# pragma: role=value`, `# pragma: deps=UID1,UID2`
3. AST-based file pattern scanning

**Example Script:**
```python
"""
Process data files.

Loads and transforms input data.
"""
# pragma: role=processor
# pragma: inputs=data.json,config.yaml
# pragma: outputs=result.json

import json

with open('data.json', 'r') as f:
    data = json.load(f)
```

**Features:**
- AST parsing for robust extraction
- Detects `open()`, `Path().read_text()`, `Path().write_text()`
- Pragma overrides supported

### simple2atom.py

Converts Simple JSON to Atom format with deterministic mapping.

**Expected JSON Structure:**
```json
{
  "title": "Task title",
  "description": "Task description",
  "role": "task",
  "inputs": ["file1.txt", "file2.txt"],
  "outputs": ["output.txt"],
  "deps": ["01K6W1BSSCAZGCG5M81WJHRSXK"]
}
```

**Features:**
- Direct field mapping
- Additional fields preserved
- ULID validation for dependencies

## Supporting Tools

### atom_validator.py

Validates atom YAML files against the schema.

**Validation Checks:**
- Required fields: `atom_uid`, `atom_key`, `title`, `role`
- ULID format for `atom_uid`
- atom_key regex compliance
- Dependency ULID validation
- Type checking for lists and strings

**Usage:**
```bash
# Single file
python3 tools/atoms/atom_validator.py atom.yaml

# Directory
python3 tools/atoms/atom_validator.py atoms/ --strict

# Changed files only
python3 tools/atoms/atom_validator.py --changed
```

### doc_indexer.py

Builds hierarchical documentation indexes.

**Outputs:**
- `_index.json`: Machine-readable index
- `_index.md`: Human-readable table of contents

**Features:**
- Recursive directory scanning
- Markdown title extraction
- Configurable depth limit
- Generates relative links

**Usage:**
```bash
python3 tools/atoms/doc_indexer.py docs/ --max-depth 10
```

### log_miner.py

Normalizes logs and identifies repeated patterns.

**Normalization:**
- Timestamps → `<TIMESTAMP>`
- UUIDs → `<UUID>`
- Paths → `<UNIX_PATH>` or `<WINDOWS_PATH>`
- Numbers → `<NUMBER>`
- IP addresses → `<IP_ADDRESS>`

**Outputs:**
- Summary statistics
- Repeated patterns with counts
- Candidate atoms for high-frequency patterns

**Usage:**
```bash
python3 tools/atoms/log_miner.py logs/ --output analysis.json --min-count 3
```

## Testing

```bash
# Run all tests
python3 -m pytest tests/ -v

# Run unit tests only
python3 -m pytest tests/unit/ -v

# Run system tests only
python3 -m pytest tests/system/ -v

# Run with coverage
python3 -m pytest tests/ --cov=tools/atoms --cov-report=html
```

## Schema Reference

### Atom YAML Schema

```yaml
# Required fields
atom_uid: 01K6W1BSSCAZGCG5M81WJHRSXK  # ULID format
atom_key: cli/dev-setup/v1/init/all/001  # Structured key
title: "Task title"
role: "task"  # task, orchestrator, validator, processor

# Optional fields
description: "Detailed description"
inputs:
  - input1.txt
  - input2.txt
outputs:
  - output.txt
deps:
  - 01K6W1BSSCAZGCG5M81WJHRS00  # Dependency UIDs
```

### atom_key Format

```
<namespace>/<workflow>/<version>/<phase>/<lane>/<sequence>[-<variant>][-r<revision>]
```

Examples:
- `cli/dev-setup/v1/init/all/001`
- `hp/pipeline/v2/exec/complex/042-win`
- `cli/setup/v1/init/all/003-r2`

### ULID Format

- 26 characters
- Base32 encoded
- Lexicographically sortable
- Time-ordered
- Pattern: `^[0-9A-HJKMNP-TV-Z]{26}$`

## Structured Logging

All tools use `structlog` for JSON-formatted logging:

```json
{
  "event": "md2atom.converted",
  "file": "input.md",
  "atom_uid": "01K6W1BSSCAZGCG5M81WJHRSXK",
  "atom_key": "cli/dev-setup/v1/init/all/001",
  "level": "info",
  "timestamp": "2025-10-06T12:34:56.789Z"
}
```

## Contributing

When adding new converters or tools:

1. Follow existing patterns for CLI arguments
2. Use `structlog` for logging with JSON output
3. Include comprehensive docstrings
4. Add unit tests in `tests/unit/`
5. Add system tests in `tests/system/`
6. Update this README

## License

See repository root for license information.

## Support

For issues, questions, or contributions, please refer to the main repository documentation.
