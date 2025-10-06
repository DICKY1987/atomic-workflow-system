#!/usr/bin/env python3
"""
Python script to Atom converter.

Converts Python scripts to Atom format by extracting:
- Module docstring (first line becomes title, rest becomes description)
- Pragmas: # pragma: role=orchestrator, # pragma: deps=ULID1,ULID2
- Static file input/output patterns (open(), Path operations)

Usage:
    python py2atom.py script.py --namespace cli --workflow dev-setup --version v1 \
                      --phase init --lane all --sequence 1
"""
import sys
import re
import ast
from pathlib import Path
from typing import Dict, List, Optional, Set
import yaml
import structlog
import argparse

from id_utils import generate_ulid, build_atom_key, validate_ulid

log = structlog.get_logger()


def extract_docstring(content: str) -> Optional[Dict[str, str]]:
    """
    Extract module docstring from Python script.
    
    Args:
        content: Python script content
        
    Returns:
        Dictionary with 'title' and 'description' or None
    """
    try:
        tree = ast.parse(content)
        docstring = ast.get_docstring(tree)
        
        if docstring:
            lines = docstring.strip().split('\n')
            title = lines[0].strip()
            description = '\n'.join(lines[1:]).strip() if len(lines) > 1 else None
            
            result = {'title': title}
            if description:
                result['description'] = description
            return result
    except:
        pass
    
    return None


def extract_pragmas(content: str) -> Dict[str, any]:
    """
    Extract pragma comments from Python script.
    
    Supports:
    - # pragma: role=orchestrator
    - # pragma: deps=ULID1,ULID2
    - # pragma: inputs=file1,file2
    - # pragma: outputs=file3,file4
    
    Args:
        content: Python script content
        
    Returns:
        Dictionary of pragma values
    """
    pragmas = {}
    
    # Find all pragma lines
    pragma_pattern = r'#\s*pragma:\s*(\w+)=(.+?)$'
    matches = re.findall(pragma_pattern, content, re.MULTILINE | re.IGNORECASE)
    
    for key, value in matches:
        key = key.lower().strip()
        value = value.strip()
        
        if key in ['deps', 'inputs', 'outputs']:
            # Parse as list
            pragmas[key] = [item.strip() for item in value.split(',')]
        else:
            # Store as string
            pragmas[key] = value
    
    return pragmas


def scan_file_patterns(content: str) -> Dict[str, Set[str]]:
    """
    Scan Python script for file input/output patterns.
    
    Detects:
    - open() calls with 'r', 'rb' modes (inputs)
    - open() calls with 'w', 'a', 'wb', 'ab' modes (outputs)
    - Path().read_text(), Path().read_bytes() (inputs)
    - Path().write_text(), Path().write_bytes() (outputs)
    
    Args:
        content: Python script content
        
    Returns:
        Dictionary with 'inputs' and 'outputs' sets
    """
    patterns = {'inputs': set(), 'outputs': set()}
    
    try:
        tree = ast.parse(content)
        
        for node in ast.walk(tree):
            # Check for open() calls
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id == 'open':
                    # Get first argument (filename)
                    if node.args:
                        filename_node = node.args[0]
                        if isinstance(filename_node, ast.Constant):
                            filename = filename_node.value
                            
                            # Check mode (second argument or keyword 'mode')
                            mode = 'r'  # Default mode
                            if len(node.args) > 1 and isinstance(node.args[1], ast.Constant):
                                mode = node.args[1].value
                            else:
                                for kw in node.keywords:
                                    if kw.arg == 'mode' and isinstance(kw.value, ast.Constant):
                                        mode = kw.value.value
                            
                            if isinstance(mode, str):
                                if 'r' in mode or mode == '':
                                    patterns['inputs'].add(filename)
                                elif 'w' in mode or 'a' in mode:
                                    patterns['outputs'].add(filename)
                
                # Check for Path operations
                elif isinstance(node.func, ast.Attribute):
                    method_name = node.func.attr
                    
                    # Path().read_text() or Path().read_bytes()
                    if method_name in ['read_text', 'read_bytes', 'open']:
                        # Try to get the path
                        if isinstance(node.func.value, ast.Call):
                            if isinstance(node.func.value.func, ast.Name) and node.func.value.func.id == 'Path':
                                if node.func.value.args and isinstance(node.func.value.args[0], ast.Constant):
                                    filename = node.func.value.args[0].value
                                    patterns['inputs'].add(filename)
                    
                    # Path().write_text() or Path().write_bytes()
                    elif method_name in ['write_text', 'write_bytes']:
                        if isinstance(node.func.value, ast.Call):
                            if isinstance(node.func.value.func, ast.Name) and node.func.value.func.id == 'Path':
                                if node.func.value.args and isinstance(node.func.value.args[0], ast.Constant):
                                    filename = node.func.value.args[0].value
                                    patterns['outputs'].add(filename)
    
    except Exception as e:
        log.warning("py2atom.scan_failed", error=str(e))
    
    return patterns


def convert_py_to_atom(
    py_path: Path,
    namespace: str,
    workflow: str,
    version: str,
    phase: str,
    lane: str,
    sequence: int,
    variant: Optional[str] = None,
    revision: Optional[int] = None,
    scan_patterns: bool = True
) -> Dict:
    """
    Convert a Python script to an Atom definition.
    
    Args:
        py_path: Path to Python script
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
    log.info("py2atom.converting", file=str(py_path))
    
    with open(py_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract docstring
    docstring_data = extract_docstring(content)
    
    # Extract pragmas (take precedence)
    pragmas = extract_pragmas(content)
    
    # Determine title
    if docstring_data and 'title' in docstring_data:
        title = docstring_data['title']
    else:
        # Fallback to filename
        title = py_path.stem
    
    # Build atom
    atom = {
        'atom_uid': generate_ulid(),
        'atom_key': build_atom_key(namespace, workflow, version, phase, lane, sequence, variant, revision),
        'title': title,
    }
    
    # Add description
    if docstring_data and 'description' in docstring_data:
        atom['description'] = docstring_data['description']
    
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
                log.warning("py2atom.invalid_dep", dep=dep, file=str(py_path))
        if valid_deps:
            atom['deps'] = valid_deps
    
    log.info("py2atom.converted",
             file=str(py_path),
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
    
    parser = argparse.ArgumentParser(description='Convert Python script to Atom format')
    parser.add_argument('input', help='Input Python script file')
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
        atom = convert_py_to_atom(
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
            log.info("py2atom.written", output=args.output)
        else:
            print(yaml_output)
            
    except Exception as e:
        log.error("py2atom.failed", error=str(e))
        sys.exit(1)


if __name__ == '__main__':
    main()
