"""Unit tests for converters and utilities."""
import pytest
from pathlib import Path
import sys

# Add tools directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'tools' / 'atoms'))

from id_utils import (
    generate_ulid,
    validate_ulid,
    validate_atom_key,
    build_atom_key
)


def test_generate_ulid():
    """Test ULID generation."""
    ulid1 = generate_ulid()
    ulid2 = generate_ulid()
    
    assert len(ulid1) == 26
    assert len(ulid2) == 26
    assert ulid1 != ulid2  # Should be unique
    assert validate_ulid(ulid1)
    assert validate_ulid(ulid2)


def test_validate_ulid():
    """Test ULID validation."""
    # Valid ULIDs
    assert validate_ulid('01ARZ3NDEKTSV4RRFFQ69G5FAV')
    assert validate_ulid('01K6W1BSSCAZGCG5M81WJHRSXK')
    
    # Invalid ULIDs
    assert not validate_ulid('invalid')
    assert not validate_ulid('01ARZ3NDEKTSV4RRFFQ69G5FA')  # Too short
    assert not validate_ulid('01ARZ3NDEKTSV4RRFFQ69G5FAVX')  # Too long
    assert not validate_ulid('01arz3ndektsv4rrffq69g5fav')  # Lowercase not allowed


def test_validate_atom_key():
    """Test atom_key validation."""
    # Valid atom_keys
    assert validate_atom_key('cli/dev-setup/v1/init/all/001')
    assert validate_atom_key('hp/orchestrate/v3/exec/simple/042')
    assert validate_atom_key('cli/dev-setup/v1/init/all/001-win')
    assert validate_atom_key('cli/dev-setup/v1/init/all/001-r2')
    assert validate_atom_key('cli/dev-setup/v1/init/all/001-win-r2')
    
    # Invalid atom_keys
    assert not validate_atom_key('invalid')
    assert not validate_atom_key('CLI/dev-setup/v1/init/all/001')  # Uppercase
    assert not validate_atom_key('cli/dev-setup/1/init/all/001')  # Missing 'v' prefix
    assert not validate_atom_key('cli/dev-setup/v1/init/all/1')  # Sequence not padded


def test_build_atom_key():
    """Test atom_key construction."""
    key = build_atom_key('cli', 'dev-setup', 'v1', 'init', 'all', 1)
    assert key == 'cli/dev-setup/v1/init/all/001'
    
    key = build_atom_key('hp', 'pipeline', 'v2', 'exec', 'complex', 42)
    assert key == 'hp/pipeline/v2/exec/complex/042'
    
    key = build_atom_key('cli', 'setup', 'v1', 'init', 'all', 3, variant='win')
    assert key == 'cli/setup/v1/init/all/003-win'
    
    key = build_atom_key('cli', 'setup', 'v1', 'init', 'all', 3, revision=2)
    assert key == 'cli/setup/v1/init/all/003-r2'
    
    key = build_atom_key('cli', 'setup', 'v1', 'init', 'all', 3, variant='linux', revision=1)
    assert key == 'cli/setup/v1/init/all/003-linux-r1'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
