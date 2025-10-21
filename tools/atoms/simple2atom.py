#!/usr/bin/env python3
"""
Simple JSON to Atom converter.

Converts Simple JSON format to Atom format with deterministic mapping.
Expected Simple JSON format:
{
  "title": "Task title",
  "description": "Task description",
  "role": "task",
  "inputs": ["file1", "file2"],
  "outputs": ["file3"],
  "deps": ["ULID1", "ULID2"]
}

Usage:
    python simple2atom.py input.json --namespace cli --workflow dev-setup --version v1 \
                          --phase init --lane all --sequence 1
"""
import argparse
import json
import sys
from pathlib import Path
from typing import Optional

import structlog
import yaml
from id_utils import build_atom_key, generate_ulid, validate_ulid

log = structlog.get_logger()


def convert_simple_to_atom(
    json_path: Path,
    namespace: str,
    workflow: str,
    version: str,
    phase: str,
    lane: str,
    sequence: int,
    variant: Optional[str] = None,
    revision: Optional[int] = None
) -> dict:
    """
    Convert a Simple JSON file to an Atom definition.

    Args:
        json_path: Path to JSON file
        namespace: Namespace for atom_key
        workflow: Workflow for atom_key
        version: Version for atom_key
        phase: Phase for atom_key
        lane: Lane for atom_key
        sequence: Sequence number for atom_key
        variant: Optional variant
        revision: Optional revision number

    Returns:
        Atom dictionary
    """
    log.info("simple2atom.converting", file=str(json_path))

    with open(json_path, encoding='utf-8') as f:
        simple_data = json.load(f)

    if not isinstance(simple_data, dict):
        raise ValueError(f"JSON file must contain an object: {json_path}")

    # Build atom with required fields
    atom = {
        'atom_uid': generate_ulid(),
        'atom_key': build_atom_key(namespace, workflow, version, phase, lane, sequence, variant, revision),
        'title': simple_data.get('title', 'Untitled'),
        'role': simple_data.get('role', 'task'),
    }

    # Add optional fields if present
    if 'description' in simple_data and simple_data['description']:
        atom['description'] = simple_data['description']

    if 'inputs' in simple_data and simple_data['inputs']:
        if isinstance(simple_data['inputs'], list):
            atom['inputs'] = simple_data['inputs']
        else:
            log.warning("simple2atom.invalid_inputs", file=str(json_path))

    if 'outputs' in simple_data and simple_data['outputs']:
        if isinstance(simple_data['outputs'], list):
            atom['outputs'] = simple_data['outputs']
        else:
            log.warning("simple2atom.invalid_outputs", file=str(json_path))

    if 'deps' in simple_data and simple_data['deps']:
        if isinstance(simple_data['deps'], list):
            valid_deps = []
            for dep in simple_data['deps']:
                if isinstance(dep, str) and validate_ulid(dep):
                    valid_deps.append(dep)
                else:
                    log.warning("simple2atom.invalid_dep", dep=dep, file=str(json_path))
            if valid_deps:
                atom['deps'] = valid_deps
        else:
            log.warning("simple2atom.invalid_deps", file=str(json_path))

    # Copy any additional fields (deterministic mapping)
    known_fields = {'title', 'description', 'role', 'inputs', 'outputs', 'deps'}
    for key, value in simple_data.items():
        if key not in known_fields and value is not None:
            atom[key] = value

    log.info("simple2atom.converted",
             file=str(json_path),
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

    parser = argparse.ArgumentParser(description='Convert Simple JSON to Atom format')
    parser.add_argument('input', help='Input JSON file')
    parser.add_argument('--output', '-o', help='Output YAML file (default: stdout)')
    parser.add_argument('--namespace', required=True, help='Namespace (e.g., cli)')
    parser.add_argument('--workflow', required=True, help='Workflow slug (e.g., dev-setup)')
    parser.add_argument('--version', required=True, help='Version (e.g., v1)')
    parser.add_argument('--phase', required=True, help='Phase (e.g., init, exec, val)')
    parser.add_argument('--lane', required=True, help='Lane (e.g., all, simple, complex)')
    parser.add_argument('--sequence', type=int, required=True, help='Sequence number')
    parser.add_argument('--variant', help='Optional variant (e.g., win, linux)')
    parser.add_argument('--revision', type=int, help='Optional revision number')

    args = parser.parse_args()

    try:
        atom = convert_simple_to_atom(
            Path(args.input),
            args.namespace,
            args.workflow,
            args.version,
            args.phase,
            args.lane,
            args.sequence,
            args.variant,
            args.revision
        )

        yaml_output = yaml.dump(atom, sort_keys=False, allow_unicode=True)

        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(yaml_output)
            log.info("simple2atom.written", output=args.output)
        else:
            print(yaml_output)

    except Exception as e:
        log.error("simple2atom.failed", error=str(e))
        sys.exit(1)


if __name__ == '__main__':
    main()
