"""Tests for process2atoms parser and generation helpers."""
from pathlib import Path
import sys

# Add tools dir to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'tools' / 'atoms'))

from process2atoms import parse_process_doc, map_tag_to_lane, slugify


def test_map_tag_to_lane():
    assert map_tag_to_lane('AI MAKES DECISIONS') == 'ai'
    assert map_tag_to_lane('deterministic') == 'det'
    assert map_tag_to_lane(None) == 'all'


def test_parse_minimal_doc(tmp_path: Path):
    md = tmp_path / 'sample.md'
    md.write_text(
        """# Sample Workflow\n\n## PHASE 0: ENTRY (2 atoms)\n\n### Entry Point [AI MAKES DECISIONS] (1 atom)\n```yaml\natom_001: detect_entry | Role: orchestrator\n```\n\n### Determination [DETERMINISTIC] (1 atom)\n```yaml\natom_002: validate | Role: qa_test_agent\n```\n""",
        encoding='utf-8',
    )

    title, atoms = parse_process_doc(md)
    assert 'Sample Workflow' in title
    assert len(atoms) == 2
    # First atom
    a0 = atoms[0]
    assert a0.phase_slug.startswith('p00-')
    assert a0.lane == 'ai'
    assert a0.sequence == 1
    assert a0.role == 'orchestrator'
    # Second atom
    a1 = atoms[1]
    assert a1.lane == 'det'
    assert a1.sequence == 2
    assert a1.role == 'qa_test_agent'

