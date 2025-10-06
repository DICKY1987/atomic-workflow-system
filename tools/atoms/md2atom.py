#!/usr/bin/env python3
"""
Markdown to Atom converter.

Converts Markdown files to Atom format following strict heading conventions:
- # Title (required, becomes atom title)
- ## Description (optional, becomes atom description)
- ## Inputs (optional, list of input files)
- ## Outputs (optional, list of output files)
- ## Dependencies (optional, list of atom UIDs)
- ## Role (optional, defaults to 'task')

Usage:
    python md2atom.py input.md --namespace cli --workflow dev-setup --version v1 \
                      --phase init --lane all --sequence 1
"""
import sys
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import yaml
import structlog
import argparse

from id_utils import generate_ulid, build_atom_key, validate_ulid

log = structlog.get_logger()


def parse_markdown_sections(content: str) -> Dict[str, str]:
    """
    Parse markdown content into sections based on headings.
    
    Args:
        content: Markdown file content
        
    Returns:
        Dictionary mapping section names to their content
    """
    sections = {}
    current_section = None
    current_content = []
    
    lines = content.split('\n')
    
    for line in lines:
        # Check for h1 heading (title)
        if line.startswith('# ') and not line.startswith('## '):
            # Save any previous section
            if current_section and current_content:
                sections[current_section] = '\n'.join(current_content).strip()
            # Store title and reset
            sections['title'] = line[2:].strip()
            current_section = None
            current_content = []
        # Check for h2 heading (other sections)
        elif line.startswith('## '):
            # Save previous section
            if current_section and current_content:
                sections[current_section] = '\n'.join(current_content).strip()
            # Start new section
            current_section = line[3:].strip().lower()
            current_content = []
        else:
            # Add content to current section
            if current_section:
                current_content.append(line)
    
    # Don't forget the last section
    if current_section and current_content:
        sections[current_section] = '\n'.join(current_content).strip()
    
    return sections


def extract_list_items(text: str) -> List[str]:
    """
    Extract list items from markdown text.
    
    Args:
        text: Markdown text containing lists
        
    Returns:
        List of items
    """
    items = []
    for line in text.split('\n'):
        line = line.strip()
        # Match bullet points (-, *, +) or numbered lists
        if line.startswith('- ') or line.startswith('* ') or line.startswith('+ '):
            items.append(line[2:].strip())
        elif re.match(r'^\d+\.\s', line):
            items.append(re.sub(r'^\d+\.\s', '', line).strip())
    return items


def convert_markdown_to_atom(
    md_path: Path,
    namespace: str,
    workflow: str,
    version: str,
    phase: str,
    lane: str,
    sequence: int,
    variant: Optional[str] = None,
    revision: Optional[int] = None,
    pragmas: Optional[Dict[str, str]] = None
) -> Dict:
    """
    Convert a Markdown file to an Atom definition.
    
    Args:
        md_path: Path to markdown file
        namespace: Namespace for atom_key
        workflow: Workflow for atom_key
        version: Version for atom_key
        phase: Phase for atom_key
        lane: Lane for atom_key
        sequence: Sequence number for atom_key
        variant: Optional variant
        revision: Optional revision number
        pragmas: Optional pragma overrides (e.g., {'role': 'orchestrator'})
        
    Returns:
        Atom dictionary
    """
    log.info("md2atom.converting", file=str(md_path))
    
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Parse sections
    sections = parse_markdown_sections(content)
    
    # Extract title (required)
    if 'title' not in sections:
        raise ValueError(f"Markdown file must have a # Title heading: {md_path}")
    
    title = sections['title']
    
    # Build atom
    atom = {
        'atom_uid': generate_ulid(),
        'atom_key': build_atom_key(namespace, workflow, version, phase, lane, sequence, variant, revision),
        'title': title,
    }
    
    # Add description if present
    if 'description' in sections:
        atom['description'] = sections['description']
    
    # Add role (from pragma or section or default)
    if pragmas and 'role' in pragmas:
        atom['role'] = pragmas['role']
    elif 'role' in sections:
        atom['role'] = sections['role'].strip()
    else:
        atom['role'] = 'task'
    
    # Extract inputs
    if 'inputs' in sections:
        inputs = extract_list_items(sections['inputs'])
        if inputs:
            atom['inputs'] = inputs
    
    # Extract outputs
    if 'outputs' in sections:
        outputs = extract_list_items(sections['outputs'])
        if outputs:
            atom['outputs'] = outputs
    
    # Extract dependencies
    if 'dependencies' in sections or 'deps' in sections:
        deps_section = sections.get('dependencies') or sections.get('deps')
        deps = extract_list_items(deps_section)
        # Validate that deps are ULIDs
        valid_deps = []
        for dep in deps:
            dep = dep.strip()
            if validate_ulid(dep):
                valid_deps.append(dep)
            else:
                log.warning("md2atom.invalid_dep", dep=dep, file=str(md_path))
        if valid_deps:
            atom['deps'] = valid_deps
    
    # Apply any additional pragmas
    if pragmas:
        for key, value in pragmas.items():
            if key not in ['role'] and key not in atom:  # Don't override existing fields
                atom[key] = value
    
    log.info("md2atom.converted", 
             file=str(md_path), 
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
    
    parser = argparse.ArgumentParser(description='Convert Markdown to Atom format')
    parser.add_argument('input', help='Input Markdown file')
    parser.add_argument('--output', '-o', help='Output YAML file (default: stdout)')
    parser.add_argument('--namespace', required=True, help='Namespace (e.g., cli)')
    parser.add_argument('--workflow', required=True, help='Workflow slug (e.g., dev-setup)')
    parser.add_argument('--version', required=True, help='Version (e.g., v1)')
    parser.add_argument('--phase', required=True, help='Phase (e.g., init, exec, val)')
    parser.add_argument('--lane', required=True, help='Lane (e.g., all, simple, complex)')
    parser.add_argument('--sequence', type=int, required=True, help='Sequence number')
    parser.add_argument('--variant', help='Optional variant (e.g., win, linux)')
    parser.add_argument('--revision', type=int, help='Optional revision number')
    parser.add_argument('--role', help='Override role (default: task)')
    
    args = parser.parse_args()
    
    pragmas = {}
    if args.role:
        pragmas['role'] = args.role
    
    try:
        atom = convert_markdown_to_atom(
            Path(args.input),
            args.namespace,
            args.workflow,
            args.version,
            args.phase,
            args.lane,
            args.sequence,
            args.variant,
            args.revision,
            pragmas
        )
        
        yaml_output = yaml.dump(atom, sort_keys=False, allow_unicode=True)
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(yaml_output)
            log.info("md2atom.written", output=args.output)
        else:
            print(yaml_output)
            
    except Exception as e:
        log.error("md2atom.failed", error=str(e))
        sys.exit(1)


if __name__ == '__main__':
    main()
