#!/usr/bin/env python3
"""
Utility functions for generating and validating identifiers (ULID, atom_key).
"""
import re
from ulid import ULID


# Regex patterns from the specification
ATOM_KEY_REGEX = r'^[a-z0-9-]+/[a-z0-9-]+/v[0-9]+/[a-z0-9-]+/[a-z0-9-]+/[0-9]{3}(-[a-z0-9-]+)?(-r[0-9]+)?$'
ULID_REGEX = r'^[0-9A-HJKMNP-TV-Z]{26}$'


def generate_ulid() -> str:
    """
    Generate a new ULID (Universally Unique Lexicographically Sortable Identifier).
    
    Returns:
        str: A 26-character ULID string
    """
    return str(ULID())


def validate_ulid(uid: str) -> bool:
    """
    Validate that a string matches the ULID format.
    
    Args:
        uid: String to validate
        
    Returns:
        bool: True if valid ULID format, False otherwise
    """
    return bool(re.match(ULID_REGEX, uid))


def validate_atom_key(key: str) -> bool:
    """
    Validate that a string matches the atom_key format.
    
    Args:
        key: String to validate
        
    Returns:
        bool: True if valid atom_key format, False otherwise
    """
    return bool(re.match(ATOM_KEY_REGEX, key))


def build_atom_key(
    namespace: str,
    workflow: str,
    version: str,
    phase: str,
    lane: str,
    sequence: int,
    variant: str = None,
    revision: int = None
) -> str:
    """
    Construct atom_key from workflow context.
    
    Args:
        namespace: Namespace (e.g., 'cli', 'hp')
        workflow: Workflow slug (e.g., 'dev-setup')
        version: Workflow version (e.g., 'v1')
        phase: Phase (e.g., 'init', 'exec', 'val')
        lane: Lane (e.g., 'all', 'simple', 'complex')
        sequence: Sequence number (e.g., 3)
        variant: Optional variant (e.g., 'win', 'linux')
        revision: Optional revision number
        
    Returns:
        str: Constructed atom_key
    """
    seq_padded = f"{sequence:03d}"
    atom_key = f"{namespace}/{workflow}/{version}/{phase}/{lane}/{seq_padded}"
    
    if variant:
        atom_key += f"-{variant}"
    
    if revision is not None:
        atom_key += f"-r{revision}"
    
    return atom_key
