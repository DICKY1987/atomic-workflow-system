#!/usr/bin/env python3
"""
PowerShell script to Atom converter.

Converts PowerShell scripts to Atom format by extracting:
- .SYNOPSIS section (becomes title)
- .DESCRIPTION section (becomes description)
- Pragmas: # Role:, # DependsOn:, # Inputs:, # Outputs:
- Input/Output pattern scanning for file operations

Usage:
    python ps2atom.py script.ps1 --namespace cli --workflow dev-setup --version v1 \
                      --phase init --lane all --sequence 1
"""
import argparse
import re
import sys
from pathlib import Path
from typing import Optional

import structlog
import yaml
from id_utils import build_atom_key, generate_ulid, validate_ulid

log = structlog.get_logger()


def extract_comment_block_help(content: str) -> dict[str, str]:
    """
    Extract PowerShell comment-based help sections.

    Args:
        content: PowerShell script content

    Returns:
        Dictionary with 'synopsis', 'description', etc.
    """
    help_data = {}

    # Match comment-based help block
    # Pattern: <# ... .SYNOPSIS ... .DESCRIPTION ... #>
    block_match = re.search(r'<#\s*(.*?)\s*#>', content, re.DOTALL | re.IGNORECASE)

    if block_match:
        help_block = block_match.group(1)

        # Extract .SYNOPSIS
        synopsis_match = re.search(r'\.SYNOPSIS\s+(.*?)(?=\.|$)', help_block, re.DOTALL | re.IGNORECASE)
        if synopsis_match:
            help_data['synopsis'] = synopsis_match.group(1).strip()

        # Extract .DESCRIPTION
        desc_match = re.search(r'\.DESCRIPTION\s+(.*?)(?=\.|$)', help_block, re.DOTALL | re.IGNORECASE)
        if desc_match:
            help_data['description'] = desc_match.group(1).strip()

    return help_data


def extract_pragmas(content: str) -> dict[str, str]:
    """
    Extract pragma comments from PowerShell script.

    Supports:
    - # Role: orchestrator
    - # DependsOn: ULID1, ULID2
    - # Inputs: file1, file2
    - # Outputs: file3, file4

    Args:
        content: PowerShell script content

    Returns:
        Dictionary of pragma values
    """
    pragmas = {}

    # Extract Role
    role_match = re.search(r'#\s*Role:\s*(.+?)$', content, re.MULTILINE | re.IGNORECASE)
    if role_match:
        pragmas['role'] = role_match.group(1).strip()

    # Extract DependsOn
    deps_match = re.search(r'#\s*DependsOn:\s*(.+?)$', content, re.MULTILINE | re.IGNORECASE)
    if deps_match:
        deps_str = deps_match.group(1).strip()
        deps = [d.strip() for d in deps_str.split(',')]
        pragmas['deps'] = deps

    # Extract Inputs
    inputs_match = re.search(r'#\s*Inputs:\s*(.+?)$', content, re.MULTILINE | re.IGNORECASE)
    if inputs_match:
        inputs_str = inputs_match.group(1).strip()
        inputs = [i.strip() for i in inputs_str.split(',')]
        pragmas['inputs'] = inputs

    # Extract Outputs
    outputs_match = re.search(r'#\s*Outputs:\s*(.+?)$', content, re.MULTILINE | re.IGNORECASE)
    if outputs_match:
        outputs_str = outputs_match.group(1).strip()
        outputs = [o.strip() for o in outputs_str.split(',')]
        pragmas['outputs'] = outputs

    return pragmas


def scan_file_patterns(content: str) -> dict[str, set[str]]:
    """
    Scan PowerShell script for input/output file patterns.

    Detects:
    - Get-Content, Import-*, Read-*
    - Set-Content, Export-*, Out-File, Write-*
    - Test-Path (treated as input)

    Args:
        content: PowerShell script content

    Returns:
        Dictionary with 'inputs' and 'outputs' sets
    """
    patterns = {'inputs': set(), 'outputs': set()}

    # Input patterns - look for -Path parameter or direct string argument
    input_cmdlets = [
        r'Get-Content\s+(?:-Path\s+)?["\']([^"\']+)["\']',
        r'Import-\w+\s+(?:-Path\s+)?["\']([^"\']+)["\']',
        r'Read-\w+\s+(?:-Path\s+)?["\']([^"\']+)["\']',
        r'Test-Path\s+(?:-Path\s+)?["\']([^"\']+)["\']',
    ]

    for pattern in input_cmdlets:
        matches = re.findall(pattern, content, re.IGNORECASE)
        for match in matches:
            # Clean up and normalize paths
            if not match.startswith('$'):
                patterns['inputs'].add(match.strip())

    # Output patterns
    output_cmdlets = [
        r'Set-Content\s+(?:-Path\s+)?["\']([^"\']+)["\']',
        r'Export-\w+\s+-Path\s+["\']([^"\']+)["\']',
        r'Out-File\s+(?:-FilePath\s+)?["\']([^"\']+)["\']',
        r'>>\s*["\']?([^"\'\s]+)["\']?',  # Redirection operator
    ]

    for pattern in output_cmdlets:
        matches = re.findall(pattern, content, re.IGNORECASE)
        for match in matches:
            if not match.startswith('$'):
                patterns['outputs'].add(match.strip())

    return patterns


def convert_ps_to_atom(
    ps_path: Path,
    namespace: str,
    workflow: str,
    version: str,
    phase: str,
    lane: str,
    sequence: int,
    variant: Optional[str] = None,
    revision: Optional[int] = None,
    scan_patterns: bool = True
) -> dict:
    """
    Convert a PowerShell script to an Atom definition.

    Args:
        ps_path: Path to PowerShell script
        namespace: Namespace for atom_key
        workflow: Workflow for atom_key
        version: Version for atom_key
        phase: Phase for atom_key
        lane: Lane for atom_key
        sequence: Sequence number for atom_key
        variant: Optional variant
        revision: Optional revision number
        scan_patterns: Whether to scan for file patterns

    Returns:
        Atom dictionary
    """
    log.info("ps2atom.converting", file=str(ps_path))

    with open(ps_path, encoding='utf-8') as f:
        content = f.read()

    # Extract comment-based help
    help_data = extract_comment_block_help(content)

    # Extract pragmas
    pragmas = extract_pragmas(content)

    # Determine title
    if help_data.get('synopsis'):
        title = help_data['synopsis']
    else:
        # Fallback to filename
        title = ps_path.stem

    # Build atom
    atom = {
        'atom_uid': generate_ulid(),
        'atom_key': build_atom_key(namespace, workflow, version, phase, lane, sequence, variant, revision),
        'title': title,
    }

    # Add description
    if help_data.get('description'):
        atom['description'] = help_data['description']

    # Add role from pragma or default
    atom['role'] = pragmas.get('role', 'task')

    # Handle inputs - pragma takes precedence
    if 'inputs' in pragmas:
        atom['inputs'] = pragmas['inputs']
    elif scan_patterns:
        file_patterns = scan_file_patterns(content)
        if file_patterns['inputs']:
            atom['inputs'] = sorted(file_patterns['inputs'])

    # Handle outputs - pragma takes precedence
    if 'outputs' in pragmas:
        atom['outputs'] = pragmas['outputs']
    elif scan_patterns:
        if 'file_patterns' not in locals():
            file_patterns = scan_file_patterns(content)
        if file_patterns['outputs']:
            atom['outputs'] = sorted(file_patterns['outputs'])

    # Handle dependencies
    if 'deps' in pragmas:
        valid_deps = []
        for dep in pragmas['deps']:
            if validate_ulid(dep):
                valid_deps.append(dep)
            else:
                log.warning("ps2atom.invalid_dep", dep=dep, file=str(ps_path))
        if valid_deps:
            atom['deps'] = valid_deps

    log.info("ps2atom.converted",
             file=str(ps_path),
             atom_uid=atom['atom_uid'],
             atom_key=atom['atom_key'])

    return atom


def main():
    """CLI entry point."""
    structlog.configure(
        processors=[
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer()
        ]
    )

    parser = argparse.ArgumentParser(description='Convert PowerShell script to Atom format')
    parser.add_argument('input', help='Input PowerShell script file')
    parser.add_argument('--output', '-o', help='Output YAML file (default: stdout)')
    parser.add_argument('--namespace', required=True, help='Namespace (e.g., cli)')
    parser.add_argument('--workflow', required=True, help='Workflow slug (e.g., dev-setup)')
    parser.add_argument('--version', required=True, help='Version (e.g., v1)')
    parser.add_argument('--phase', required=True, help='Phase (e.g., init, exec, val)')
    parser.add_argument('--lane', required=True, help='Lane (e.g., all, simple, complex)')
    parser.add_argument('--sequence', type=int, required=True, help='Sequence number')
    parser.add_argument('--variant', help='Optional variant (e.g., win, linux)')
    parser.add_argument('--revision', type=int, help='Optional revision number')
    parser.add_argument('--no-scan', action='store_true', help='Disable file pattern scanning')

    args = parser.parse_args()

    try:
        atom = convert_ps_to_atom(
            Path(args.input),
            args.namespace,
            args.workflow,
            args.version,
            args.phase,
            args.lane,
            args.sequence,
            args.variant,
            args.revision,
            scan_patterns=not args.no_scan
        )

        yaml_output = yaml.dump(atom, sort_keys=False, allow_unicode=True)

        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(yaml_output)
            log.info("ps2atom.written", output=args.output)
        else:
            print(yaml_output)

    except Exception as e:
        log.error("ps2atom.failed", error=str(e))
        sys.exit(1)


if __name__ == '__main__':
    main()
