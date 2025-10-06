"""Unit tests for ps2atom converter."""
import pytest
from pathlib import Path
import sys
import tempfile

# Add tools directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'tools' / 'atoms'))

from ps2atom import (
    extract_comment_block_help,
    extract_pragmas,
    scan_file_patterns,
    convert_ps_to_atom
)


def test_extract_comment_block_help():
    """Test PowerShell help block extraction."""
    ps_content = """<#
.SYNOPSIS
Test script synopsis

.DESCRIPTION
This is a detailed description
of the script functionality.
#>

Write-Host "Test"
"""
    
    help_data = extract_comment_block_help(ps_content)
    
    assert 'synopsis' in help_data
    assert 'Test script synopsis' in help_data['synopsis']
    assert 'description' in help_data
    assert 'detailed description' in help_data['description']


def test_extract_pragmas():
    """Test pragma extraction."""
    ps_content = """
# Role: orchestrator
# DependsOn: 01K6W1BSSCAZGCG5M81WJHRSXK, 01K6W1CF5DSTQSR3ZYZ2XD1X45
# Inputs: config.json, data.csv
# Outputs: result.txt

Write-Host "Test"
"""
    
    pragmas = extract_pragmas(ps_content)
    
    assert pragmas['role'] == 'orchestrator'
    assert 'deps' in pragmas
    assert len(pragmas['deps']) == 2
    assert 'inputs' in pragmas
    assert len(pragmas['inputs']) == 2
    assert 'outputs' in pragmas
    assert len(pragmas['outputs']) == 1


def test_scan_file_patterns():
    """Test file pattern scanning."""
    ps_content = """
$config = Get-Content -Path "config.json" | ConvertFrom-Json
$data = Import-Csv "data.csv"

Set-Content -Path "output.txt" -Value "Result"
Export-Csv -Path "results.csv" -InputObject $data
"""
    
    patterns = scan_file_patterns(ps_content)
    
    assert 'config.json' in patterns['inputs']
    assert 'data.csv' in patterns['inputs']
    assert 'output.txt' in patterns['outputs']
    assert 'results.csv' in patterns['outputs']


def test_convert_ps_to_atom():
    """Test full PowerShell to atom conversion."""
    # Create temporary PS file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.ps1', delete=False) as f:
        f.write("""<#
.SYNOPSIS
Validate environment

.DESCRIPTION
Check system requirements
#>

# Role: validator
# Inputs: requirements.json
# Outputs: validation.log

$reqs = Get-Content "requirements.json"
Set-Content "validation.log" -Value "OK"
""")
        temp_path = Path(f.name)
    
    try:
        atom = convert_ps_to_atom(
            temp_path,
            'cli',
            'setup',
            'v1',
            'init',
            'all',
            2
        )
        
        assert 'atom_uid' in atom
        assert 'atom_key' in atom
        assert atom['atom_key'] == 'cli/setup/v1/init/all/002'
        assert atom['title'] == 'Validate environment'
        assert 'Check system requirements' in atom['description']
        assert atom['role'] == 'validator'
        assert 'inputs' in atom
        assert 'outputs' in atom
    finally:
        temp_path.unlink()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
