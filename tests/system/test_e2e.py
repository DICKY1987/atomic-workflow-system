"""System tests for end-to-end workflow validation."""
import pytest
from pathlib import Path
import sys
import tempfile
import shutil
import yaml
import subprocess

# Add tools directory to path
tools_path = Path(__file__).parent.parent.parent / 'tools' / 'atoms'
sys.path.insert(0, str(tools_path))

from atom_validator import validate_atom


class TestEndToEndWorkflow:
    """Test complete workflow from conversion to validation."""
    
    def setup_method(self):
        """Set up temporary directory for each test."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.atoms_dir = self.temp_dir / 'atoms'
        self.atoms_dir.mkdir()
    
    def teardown_method(self):
        """Clean up temporary directory."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_md2atom_to_validation(self):
        """Test Markdown conversion and validation."""
        # Create test markdown file
        md_file = self.temp_dir / 'test.md'
        md_file.write_text("""# Test Task

## Description

This is a test task.

## Inputs

- input.txt

## Outputs

- output.txt

## Role

task
""")
        
        # Convert using md2atom
        output_file = self.atoms_dir / 'test.yaml'
        result = subprocess.run([
            sys.executable, str(tools_path / 'md2atom.py'),
            str(md_file),
            '--output', str(output_file),
            '--namespace', 'test',
            '--workflow', 'demo',
            '--version', 'v1',
            '--phase', 'exec',
            '--lane', 'all',
            '--sequence', '1'
        ], capture_output=True, text=True)
        
        assert result.returncode == 0, f"Conversion failed: {result.stderr}"
        assert output_file.exists()
        
        # Validate the atom
        errors = validate_atom(output_file)
        assert len(errors) == 0, f"Validation errors: {errors}"
        
        # Check content
        with open(output_file) as f:
            atom = yaml.safe_load(f)
        
        assert atom['title'] == 'Test Task'
        assert atom['role'] == 'task'
        assert 'atom_uid' in atom
        assert 'atom_key' in atom
    
    def test_ps2atom_to_validation(self):
        """Test PowerShell conversion and validation."""
        # Create test PowerShell file
        ps_file = self.temp_dir / 'test.ps1'
        ps_file.write_text("""<#
.SYNOPSIS
Test PowerShell task

.DESCRIPTION
Validates system requirements
#>

# Role: validator

$data = Get-Content "input.json"
Set-Content "output.txt" -Value "Done"
""")
        
        # Convert using ps2atom
        output_file = self.atoms_dir / 'test_ps.yaml'
        result = subprocess.run([
            sys.executable, str(tools_path / 'ps2atom.py'),
            str(ps_file),
            '--output', str(output_file),
            '--namespace', 'test',
            '--workflow', 'demo',
            '--version', 'v1',
            '--phase', 'init',
            '--lane', 'all',
            '--sequence', '2'
        ], capture_output=True, text=True)
        
        assert result.returncode == 0, f"Conversion failed: {result.stderr}"
        assert output_file.exists()
        
        # Validate the atom
        errors = validate_atom(output_file)
        assert len(errors) == 0, f"Validation errors: {errors}"
        
        # Check content
        with open(output_file) as f:
            atom = yaml.safe_load(f)
        
        assert 'PowerShell' in atom['title'] or 'Test' in atom['title']
        assert atom['role'] == 'validator'
    
    def test_py2atom_to_validation(self):
        """Test Python conversion and validation."""
        # Create test Python file
        py_file = self.temp_dir / 'test.py'
        py_file.write_text('''"""
Test Python task.

Processes data files.
"""
# pragma: role=processor

import json

with open('input.json', 'r') as f:
    data = json.load(f)

with open('output.json', 'w') as f:
    json.dump(data, f)
''')
        
        # Convert using py2atom
        output_file = self.atoms_dir / 'test_py.yaml'
        result = subprocess.run([
            sys.executable, str(tools_path / 'py2atom.py'),
            str(py_file),
            '--output', str(output_file),
            '--namespace', 'test',
            '--workflow', 'demo',
            '--version', 'v1',
            '--phase', 'exec',
            '--lane', 'all',
            '--sequence', '3'
        ], capture_output=True, text=True)
        
        assert result.returncode == 0, f"Conversion failed: {result.stderr}"
        assert output_file.exists()
        
        # Validate the atom
        errors = validate_atom(output_file)
        assert len(errors) == 0, f"Validation errors: {errors}"
        
        # Check content
        with open(output_file) as f:
            atom = yaml.safe_load(f)
        
        assert 'Test' in atom['title']
        assert atom['role'] == 'processor'
    
    def test_batch_validation(self):
        """Test batch validation of multiple atoms."""
        # Create multiple test atoms
        for i in range(3):
            atom_file = self.atoms_dir / f'atom_{i}.yaml'
            atom_file.write_text(f"""atom_uid: 01K6W1BSSCAZGCG5M81WJHRS{'XK' if i == 0 else str(i).zfill(2)}
atom_key: test/demo/v1/exec/all/{str(i+1).zfill(3)}
title: Test Atom {i}
role: task
""")
        
        # Validate all atoms
        from atom_validator import validate_paths
        errors = validate_paths([str(self.atoms_dir)])
        
        assert len(errors) == 0, f"Validation errors: {errors}"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
