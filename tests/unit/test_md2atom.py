"""Unit tests for md2atom converter."""
import sys
import tempfile
from pathlib import Path

import pytest

# Add tools directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'tools' / 'atoms'))

from md2atom import (
    convert_markdown_to_atom,
    extract_list_items,
    parse_markdown_sections,
)


def test_parse_markdown_sections():
    """Test markdown section parsing."""
    md_content = """# Test Title

This is some content.

## Description

This is a description section.

## Inputs

- input1.txt
- input2.txt

## Outputs

- output.txt
"""

    sections = parse_markdown_sections(md_content)

    assert 'title' in sections
    assert sections['title'] == 'Test Title'
    assert 'description' in sections
    assert 'inputs' in sections
    assert 'outputs' in sections


def test_extract_list_items():
    """Test list item extraction."""
    text = """
- item1
- item2
* item3
+ item4
1. numbered1
2. numbered2
"""

    items = extract_list_items(text)
    assert len(items) == 6
    assert 'item1' in items
    assert 'numbered1' in items


def test_convert_markdown_to_atom():
    """Test full markdown to atom conversion."""
    # Create temporary markdown file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write("""# Initialize Environment

## Description

Setup the development environment.

## Inputs

- config.yaml
- settings.json

## Outputs

- .env

## Role

orchestrator
""")
        temp_path = Path(f.name)

    try:
        atom = convert_markdown_to_atom(
            temp_path,
            'cli',
            'dev-setup',
            'v1',
            'init',
            'all',
            1
        )

        assert 'atom_uid' in atom
        assert 'atom_key' in atom
        assert atom['atom_key'] == 'cli/dev-setup/v1/init/all/001'
        assert atom['title'] == 'Initialize Environment'
        assert atom['description'] == 'Setup the development environment.'
        assert atom['role'] == 'orchestrator'
        assert 'inputs' in atom
        assert len(atom['inputs']) == 2
        assert 'outputs' in atom
        assert len(atom['outputs']) == 1
    finally:
        temp_path.unlink()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
