#!/usr/bin/env python3
"""
Atom validation tool - ensures schema compliance.
"""
import sys
from pathlib import Path

import structlog
import yaml
from id_utils import validate_atom_key, validate_ulid

log = structlog.get_logger()


def validate_atom(file_path: Path) -> list[str]:
    """
    Validate single atom file.

    Args:
        file_path: Path to atom YAML file

    Returns:
        List of error messages (empty if valid)
    """
    errors = []

    try:
        with open(file_path) as f:
            atom = yaml.safe_load(f)
    except Exception as e:
        return [f"Failed to parse YAML: {e}"]

    if not isinstance(atom, dict):
        return ["File does not contain a valid YAML dictionary"]

    # Check required fields
    if 'atom_uid' not in atom:
        errors.append("Missing required field: atom_uid")
    elif not validate_ulid(atom['atom_uid']):
        errors.append(f"Invalid atom_uid format: {atom['atom_uid']}")

    if 'atom_key' not in atom:
        errors.append("Missing required field: atom_key")
    elif not validate_atom_key(atom['atom_key']):
        errors.append(f"Invalid atom_key format: {atom['atom_key']}")

    if 'title' not in atom:
        errors.append("Missing required field: title")
    elif not atom['title'] or not isinstance(atom['title'], str):
        errors.append("Field 'title' must be a non-empty string")

    if 'role' not in atom:
        errors.append("Missing required field: role")
    elif not atom['role'] or not isinstance(atom['role'], str):
        errors.append("Field 'role' must be a non-empty string")

    # Validate deps if present
    if 'deps' in atom:
        if not isinstance(atom['deps'], list):
            errors.append("Field 'deps' must be a list")
        else:
            for i, dep in enumerate(atom['deps']):
                if isinstance(dep, str):
                    if not validate_ulid(dep):
                        errors.append(f"Invalid dependency ULID at index {i}: {dep}")
                elif isinstance(dep, dict):
                    if 'uid' in dep and not validate_ulid(dep['uid']):
                        errors.append(f"Invalid dependency ULID at index {i}: {dep['uid']}")
                else:
                    errors.append(f"Invalid dependency format at index {i}")

    # Validate inputs/outputs if present
    for field in ['inputs', 'outputs']:
        if field in atom:
            if not isinstance(atom[field], list):
                errors.append(f"Field '{field}' must be a list")
            else:
                for i, item in enumerate(atom[field]):
                    if not isinstance(item, str):
                        errors.append(f"Invalid {field} item at index {i}: must be a string")

    return errors


def validate_paths(paths: list[str], strict: bool = False) -> dict[str, list[str]]:
    """
    Validate multiple atom files.

    Args:
        paths: List of file or directory paths to validate
        strict: If True, exit with error code on any validation failure

    Returns:
        Dictionary mapping file paths to error lists
    """
    all_errors = {}
    atom_files = []

    for path_str in paths:
        path = Path(path_str)
        if path.is_file() and path.suffix in ['.yaml', '.yml']:
            atom_files.append(path)
        elif path.is_dir():
            atom_files.extend(path.rglob('*.yaml'))
            atom_files.extend(path.rglob('*.yml'))

    for atom_file in atom_files:
        errors = validate_atom(atom_file)
        if errors:
            all_errors[str(atom_file)] = errors
            log.error("validation.failed", file=str(atom_file), errors=errors)
        else:
            log.info("validation.passed", file=str(atom_file))

    if all_errors:
        log.error("validation.summary",
                  total_files=len(atom_files),
                  failed_files=len(all_errors),
                  total_errors=sum(len(errs) for errs in all_errors.values()))
        if strict:
            sys.exit(1)
    else:
        log.info("validation.summary",
                 total_files=len(atom_files),
                 failed_files=0)

    return all_errors


def main():
    """CLI entry point."""
    import argparse

    structlog.configure(
        processors=[
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer()
        ]
    )

    parser = argparse.ArgumentParser(description='Validate atom YAML files')
    parser.add_argument('paths', nargs='+', help='Files or directories to validate')
    parser.add_argument('--strict', action='store_true',
                       help='Exit with error code on validation failure')
    parser.add_argument('--changed', action='store_true',
                       help='Only validate changed files (uses git diff)')

    args = parser.parse_args()

    if args.changed:
        # Get changed files from git
        import subprocess
        result = subprocess.run(
            ['git', 'diff', '--name-only', '--diff-filter=ACMR', 'HEAD'],
            capture_output=True, text=True
        )
        changed_files = [f for f in result.stdout.strip().split('\n')
                        if f and (f.endswith('.yaml') or f.endswith('.yml'))]
        if not changed_files:
            log.info("validation.no_changes")
            return
        args.paths = changed_files

    all_errors = validate_paths(args.paths, strict=args.strict)

    if all_errors:
        print("\n=== Validation Errors ===")
        for file_path, errors in all_errors.items():
            print(f"\n{file_path}:")
            for error in errors:
                print(f"  - {error}")


if __name__ == '__main__':
    main()
