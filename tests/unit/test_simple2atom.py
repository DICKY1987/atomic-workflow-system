"""Unit tests for simple2atom converter."""
import json
import sys
import tempfile
from pathlib import Path

import pytest

# Add tools directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'tools' / 'atoms'))

from simple2atom import convert_simple_to_atom


def test_convert_simple_to_atom_basic():
    """Test basic Simple JSON to atom conversion."""
    # Create temporary JSON file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump({
            "title": "Test Task",
            "description": "Test description",
            "role": "task",
            "inputs": ["file1.txt", "file2.txt"],
            "outputs": ["output.txt"]
        }, f)
        temp_path = Path(f.name)

    try:
        atom = convert_simple_to_atom(
            temp_path,
            'cli',
            'test',
            'v1',
            'exec',
            'all',
            1
        )

        assert 'atom_uid' in atom
        assert 'atom_key' in atom
        assert atom['atom_key'] == 'cli/test/v1/exec/all/001'
        assert atom['title'] == 'Test Task'
        assert atom['description'] == 'Test description'
        assert atom['role'] == 'task'
        assert len(atom['inputs']) == 2
        assert len(atom['outputs']) == 1
    finally:
        temp_path.unlink()


def test_convert_simple_to_atom_with_deps():
    """Test Simple JSON conversion with dependencies."""
    # Create temporary JSON file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump({
            "title": "Dependent Task",
            "role": "orchestrator",
            "deps": ["01K6W1BSSCAZGCG5M81WJHRSXK", "01K6W1CF5DSTQSR3ZYZ2XD1X45"]
        }, f)
        temp_path = Path(f.name)

    try:
        atom = convert_simple_to_atom(
            temp_path,
            'cli',
            'test',
            'v1',
            'init',
            'all',
            2
        )

        assert 'deps' in atom
        assert len(atom['deps']) == 2
        assert '01K6W1BSSCAZGCG5M81WJHRSXK' in atom['deps']
    finally:
        temp_path.unlink()


def test_convert_simple_to_atom_minimal():
    """Test Simple JSON conversion with minimal data."""
    # Create temporary JSON file with only title
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump({
            "title": "Minimal Task"
        }, f)
        temp_path = Path(f.name)

    try:
        atom = convert_simple_to_atom(
            temp_path,
            'cli',
            'test',
            'v1',
            'exec',
            'all',
            3
        )

        assert atom['title'] == 'Minimal Task'
        assert atom['role'] == 'task'  # Default role
        assert 'atom_uid' in atom
        assert 'atom_key' in atom
    finally:
        temp_path.unlink()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
