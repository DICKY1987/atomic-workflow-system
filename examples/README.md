# Atomic Workflow Tooling - Examples

This directory contains practical examples of using the Atomic Workflow tooling.

## Example 1: Converting a Simple Markdown File

Create a markdown file describing a task:

```bash
cat > init_env.md << 'EOF'
# Initialize Environment

## Description

Sets up the development environment by creating configuration files and
validating dependencies are installed.

## Inputs

- config.yaml
- requirements.txt

## Outputs

- .env.template
- validation.log

## Role

orchestrator
EOF
```

Convert it to an Atom:

```bash
python3 tools/atoms/md2atom.py init_env.md \
  --namespace cli \
  --workflow dev-setup \
  --version v1 \
  --phase init \
  --lane all \
  --sequence 1 \
  --output atoms/cli/v1/init/all/001_init_env.yaml
```

Validate the generated atom:

```bash
python3 tools/atoms/atom_validator.py atoms/cli/v1/init/all/001_init_env.yaml
```

## Example 2: Batch Conversion

Create multiple task files and process them:

```bash
# Create a directory for tasks
mkdir -p tasks atoms/batch/v1/exec/all

# Create several markdown tasks
for i in {1..5}; do
  cat > tasks/task_$i.md << EOF
# Task $i

## Description

This is task number $i in the workflow.

## Role

task
EOF
done

# Convert all tasks
for i in {1..5}; do
  python3 tools/atoms/md2atom.py tasks/task_$i.md \
    --namespace batch \
    --workflow demo \
    --version v1 \
    --phase exec \
    --lane all \
    --sequence $i \
    --output atoms/batch/v1/exec/all/$(printf "%03d" $i)_task.yaml
done

# Validate all generated atoms
python3 tools/atoms/atom_validator.py atoms/batch/ --strict
```

## Example 3: Mining Application Logs

Create a sample log file and mine it:

```bash
cat > app.log << 'EOF'
2025-10-06T10:00:05Z ERROR Database connection failed: timeout after 5s
2025-10-06T10:00:15Z ERROR Database connection failed: timeout after 5s
2025-10-06T10:01:05Z ERROR Database connection failed: timeout after 5s
2025-10-06T10:01:10Z WARNING Cache miss for key user_12345
2025-10-06T10:02:10Z WARNING Cache miss for key user_67890
EOF

python3 tools/atoms/log_miner.py app.log \
  --output log_analysis.json \
  --min-count 2

# View the analysis
cat log_analysis.json | python3 -m json.tool
```

## Example 4: Building Documentation Index

```bash
mkdir -p docs/{guides,api,reference}

cat > docs/README.md << 'EOF'
# Documentation Home

Welcome to the documentation.
EOF

cat > docs/guides/getting-started.md << 'EOF'
# Getting Started Guide

Quick start guide for new users.
EOF

# Build the index
python3 tools/atoms/doc_indexer.py docs/

# View the generated index
cat docs/_index.md
```

## Tips

1. **Always validate** atoms after creation
2. **Use structured logging** output for debugging
3. **Batch processing** works well with shell loops
4. **Log mining** helps identify repeated patterns

See [tools/README.md](../tools/README.md) for detailed documentation.
