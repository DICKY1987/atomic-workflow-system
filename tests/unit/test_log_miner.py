"""Unit tests for log_miner."""
import sys
import tempfile
from pathlib import Path

import pytest

# Add tools directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'tools' / 'atoms'))

from log_miner import categorize_line, fingerprint_line, mine_logs, normalize_log_line


def test_normalize_log_line():
    """Test log line normalization."""
    # Timestamp normalization
    line1 = "2025-10-06T12:34:56.789Z ERROR Something failed"
    norm1 = normalize_log_line(line1)
    assert '<TIMESTAMP>' in norm1
    assert 'ERROR' in norm1

    # UUID normalization
    line2 = "Request a1b2c3d4-e5f6-7890-abcd-ef1234567890 failed"
    norm2 = normalize_log_line(line2)
    assert '<UUID>' in norm2
    assert 'Request' in norm2

    # Path normalization
    line3 = "File /home/user/data/file.txt not found"
    norm3 = normalize_log_line(line3)
    assert '<UNIX_PATH>' in norm3
    assert 'File' in norm3


def test_fingerprint_line():
    """Test fingerprint generation."""
    line1 = "ERROR Something failed"
    line2 = "ERROR Something failed"
    line3 = "ERROR Something else failed"

    fp1 = fingerprint_line(line1)
    fp2 = fingerprint_line(line2)
    fp3 = fingerprint_line(line3)

    assert fp1 == fp2  # Same content = same fingerprint
    assert fp1 != fp3  # Different content = different fingerprint
    assert len(fp1) == 16


def test_categorize_line():
    """Test log line categorization."""
    assert categorize_line("ERROR Something went wrong") == 'ERROR'
    assert categorize_line("FATAL: Critical failure") == 'ERROR'
    assert categorize_line("WARNING: Low disk space") == 'WARNING'
    assert categorize_line("INFO: Process started") == 'INFO'
    assert categorize_line("DEBUG: Variable x=5") == 'DEBUG'


def test_mine_logs():
    """Test full log mining process."""
    # Create temporary log file with repeated patterns
    with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
        f.write("""2025-10-06T12:00:00Z ERROR Connection timeout
2025-10-06T12:01:00Z INFO Process started
2025-10-06T12:02:00Z ERROR Connection timeout
2025-10-06T12:03:00Z ERROR Connection timeout
2025-10-06T12:04:00Z INFO Process started
2025-10-06T12:05:00Z WARNING Low memory
""")
        temp_path = Path(f.name)

    try:
        analysis = mine_logs([temp_path], min_count=2)

        assert 'summary' in analysis
        assert analysis['summary']['total_lines'] == 6
        assert 'patterns' in analysis
        assert len(analysis['patterns']) >= 2  # At least 2 repeated patterns

        # Check that "Connection timeout" pattern was detected (appears 3 times)
        timeout_pattern = None
        for pattern in analysis['patterns']:
            if 'Connection timeout' in pattern['normalized']:
                timeout_pattern = pattern
                break

        assert timeout_pattern is not None
        assert timeout_pattern['count'] == 3
        assert timeout_pattern['primary_category'] == 'ERROR'
    finally:
        temp_path.unlink()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
