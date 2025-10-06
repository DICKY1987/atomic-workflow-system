"""Unit tests for py2atom converter."""
import pytest
from pathlib import Path
import sys
import tempfile

# Add tools directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'tools' / 'atoms'))

from py2atom import (
    extract_docstring,
    extract_pragmas,
    scan_file_patterns,
    convert_py_to_atom
)


def test_extract_docstring():
    """Test Python docstring extraction."""
    py_content = '''"""
Short title.

This is a longer description
spanning multiple lines.
"""

def main():
    pass
'''
    
    result = extract_docstring(py_content)
    
    assert result is not None
    assert result['title'] == 'Short title.'
    assert 'longer description' in result['description']


def test_extract_pragmas():
    """Test pragma extraction."""
    py_content = """
# pragma: role=processor
# pragma: deps=01K6W1BSSCAZGCG5M81WJHRSXK,01K6W1CF5DSTQSR3ZYZ2XD1X45
# pragma: inputs=data.json,config.yaml
# pragma: outputs=result.json

def main():
    pass
"""
    
    pragmas = extract_pragmas(py_content)
    
    assert pragmas['role'] == 'processor'
    assert 'deps' in pragmas
    assert len(pragmas['deps']) == 2
    assert 'inputs' in pragmas
    assert len(pragmas['inputs']) == 2
    assert 'outputs' in pragmas
    assert len(pragmas['outputs']) == 1


def test_scan_file_patterns():
    """Test file pattern scanning."""
    py_content = """
import json
from pathlib import Path

with open('input.json', 'r') as f:
    data = json.load(f)

with open('output.json', 'w') as f:
    json.dump(data, f)

Path('data.txt').read_text()
Path('result.txt').write_text('Done')
"""
    
    patterns = scan_file_patterns(py_content)
    
    assert 'input.json' in patterns['inputs']
    assert 'data.txt' in patterns['inputs']
    assert 'output.json' in patterns['outputs']
    assert 'result.txt' in patterns['outputs']


def test_convert_py_to_atom():
    """Test full Python to atom conversion."""
    # Create temporary Python file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write('''"""
Process data files.

Loads input data and transforms it.
"""
# pragma: role=processor
# pragma: inputs=data.json
# pragma: outputs=result.json

import json

def main():
    with open('data.json', 'r') as f:
        data = json.load(f)
    
    with open('result.json', 'w') as f:
        json.dump(data, f)

if __name__ == '__main__':
    main()
''')
        temp_path = Path(f.name)
    
    try:
        atom = convert_py_to_atom(
            temp_path,
            'cli',
            'pipeline',
            'v1',
            'exec',
            'all',
            3
        )
        
        assert 'atom_uid' in atom
        assert 'atom_key' in atom
        assert atom['atom_key'] == 'cli/pipeline/v1/exec/all/003'
        assert atom['title'] == 'Process data files.'
        assert 'transforms' in atom['description']
        assert atom['role'] == 'processor'
        assert 'inputs' in atom
        assert 'outputs' in atom
    finally:
        temp_path.unlink()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
