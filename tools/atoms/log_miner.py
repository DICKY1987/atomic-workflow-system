#!/usr/bin/env python3
"""
Log miner - normalizes logs deterministically and fingerprints them.

Processes log files to:
- Normalize log entries (remove timestamps, IDs, paths, etc.)
- Fingerprint normalized entries to detect repeated patterns
- Surface repeated tasks/errors as candidate atoms
- Output analysis in JSON format

Usage:
    python log_miner.py /path/to/logfile.log --output analysis.json
    python log_miner.py /path/to/logs/ --output analysis.json --min-count 3
"""
import argparse
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

import structlog

log = structlog.get_logger()


# Normalization patterns (order matters - more specific patterns first)
NORMALIZATION_PATTERNS = [
    # IDs and hashes (before numbers to avoid partial matches)
    (r'\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b', '<UUID>'),
    (r'\b[0-9a-fA-F]{64}\b', '<SHA256>'),
    (r'\b[0-9a-fA-F]{40}\b', '<SHA1>'),
    (r'\b[0-9a-fA-F]{32}\b', '<MD5>'),
    (r'\b[0-9A-HJKMNP-TV-Z]{26}\b', '<ULID>'),

    # Timestamps (before numbers)
    (r'\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2})?', '<TIMESTAMP>'),
    (r'\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2}', '<TIMESTAMP>'),

    # IP addresses (before numbers)
    (r'\b\d+\.\d+\.\d+\.\d+(?::\d+)?\b', '<IP_ADDRESS>'),

    # Durations and sizes (before numbers)
    (r'\b\d+(?:\.\d+)?\s*(?:ms|sec|min|hr|KB|MB|GB|TB)\b', '<METRIC>'),

    # Process/Thread IDs (before numbers)
    (r'\[(?:PID|TID|pid|tid):\s*\d+\]', '<PROCESS_ID>'),
    (r'(?:process|thread)\s+\d+', '<PROCESS_ID>'),

    # Unix timestamps (10-13 digits)
    (r'\b\d{10,13}\b', '<UNIX_TIMESTAMP>'),

    # Paths
    (r'[A-Za-z]:[/\\][\w\\/.-]+', '<WINDOWS_PATH>'),
    (r'/[\w/.-]+', '<UNIX_PATH>'),

    # Generic numbers (last to avoid false positives)
    (r'\b\d{1,5}\b', '<NUMBER>'),
]


def normalize_log_line(line: str) -> str:
    """
    Normalize a log line by replacing variable content with placeholders.

    Args:
        line: Raw log line

    Returns:
        Normalized log line
    """
    normalized = line.strip()

    for pattern, replacement in NORMALIZATION_PATTERNS:
        normalized = re.sub(pattern, replacement, normalized, flags=re.IGNORECASE)

    # Remove extra whitespace
    normalized = re.sub(r'\s+', ' ', normalized)

    return normalized


def fingerprint_line(normalized_line: str) -> str:
    """
    Generate a fingerprint (hash) for a normalized log line.

    Args:
        normalized_line: Normalized log line

    Returns:
        SHA256 hash of the line
    """
    return hashlib.sha256(normalized_line.encode('utf-8')).hexdigest()[:16]


def categorize_line(line: str) -> str:
    """
    Categorize a log line by severity/type.

    Args:
        line: Log line

    Returns:
        Category string (ERROR, WARNING, INFO, DEBUG, UNKNOWN)
    """
    line_upper = line.upper()

    if 'ERROR' in line_upper or 'FATAL' in line_upper or 'CRITICAL' in line_upper:
        return 'ERROR'
    elif 'WARN' in line_upper:
        return 'WARNING'
    elif 'INFO' in line_upper:
        return 'INFO'
    elif 'DEBUG' in line_upper or 'TRACE' in line_upper:
        return 'DEBUG'
    else:
        return 'UNKNOWN'


def mine_logs(
    log_paths: list[Path],
    min_count: int = 2
) -> dict:
    """
    Mine log files for patterns and repeated entries.

    Args:
        log_paths: List of log file paths
        min_count: Minimum occurrence count to include in results

    Returns:
        Analysis dictionary
    """
    log.info("log_miner.mining", files=len(log_paths))

    # Track fingerprints and their occurrences
    fingerprint_data = defaultdict(lambda: {
        'normalized': '',
        'original_samples': [],
        'count': 0,
        'categories': Counter(),
        'files': set()
    })

    total_lines = 0

    for log_path in log_paths:
        log.debug("log_miner.processing_file", file=str(log_path))

        try:
            with open(log_path, encoding='utf-8', errors='ignore') as f:
                for line_num, line in enumerate(f, 1):
                    if not line.strip():
                        continue

                    total_lines += 1

                    # Normalize and fingerprint
                    normalized = normalize_log_line(line)
                    fp = fingerprint_line(normalized)
                    category = categorize_line(line)

                    # Update fingerprint data
                    fp_data = fingerprint_data[fp]
                    fp_data['normalized'] = normalized
                    fp_data['count'] += 1
                    fp_data['categories'][category] += 1
                    fp_data['files'].add(str(log_path))

                    # Store sample (up to 3 samples per fingerprint)
                    if len(fp_data['original_samples']) < 3:
                        fp_data['original_samples'].append({
                            'line': line.strip(),
                            'file': str(log_path),
                            'line_num': line_num
                        })

        except Exception as e:
            log.error("log_miner.file_error", file=str(log_path), error=str(e))

    # Filter by minimum count and prepare results
    patterns = []

    for fp, data in fingerprint_data.items():
        if data['count'] >= min_count:
            # Convert sets to lists for JSON serialization
            data['files'] = sorted(data['files'])
            data['categories'] = dict(data['categories'])
            data['fingerprint'] = fp

            # Determine primary category
            data['primary_category'] = data['categories'].get('ERROR', 0) > 0 and 'ERROR' or \
                                       data['categories'].get('WARNING', 0) > 0 and 'WARNING' or \
                                       max(data['categories'], key=data['categories'].get)

            patterns.append(data)

    # Sort by count (descending)
    patterns.sort(key=lambda x: x['count'], reverse=True)

    # Generate candidate atoms for high-frequency patterns
    candidate_atoms = []
    for _i, pattern in enumerate(patterns[:20]):  # Top 20 patterns
        if pattern['count'] >= min_count * 2:  # Only high-frequency ones
            candidate = {
                'suggested_title': pattern['normalized'][:100],
                'fingerprint': pattern['fingerprint'],
                'occurrence_count': pattern['count'],
                'category': pattern['primary_category'],
                'files': pattern['files'],
                'normalized_pattern': pattern['normalized']
            }
            candidate_atoms.append(candidate)

    analysis = {
        'summary': {
            'total_lines': total_lines,
            'unique_patterns': len(fingerprint_data),
            'patterns_above_threshold': len(patterns),
            'candidate_atoms': len(candidate_atoms)
        },
        'patterns': patterns,
        'candidate_atoms': candidate_atoms
    }

    log.info("log_miner.complete",
             total_lines=total_lines,
             unique_patterns=len(fingerprint_data),
             patterns=len(patterns),
             candidates=len(candidate_atoms))

    return analysis


def main():
    """CLI entry point."""
    structlog.configure(
        processors=[
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer()
        ]
    )

    parser = argparse.ArgumentParser(description='Mine log files for patterns and candidate atoms')
    parser.add_argument('paths', nargs='+', help='Log files or directories to mine')
    parser.add_argument('--output', '-o', required=True, help='Output JSON file')
    parser.add_argument('--min-count', type=int, default=2,
                       help='Minimum occurrence count to include pattern (default: 2)')
    parser.add_argument('--pattern', help='Only show patterns matching this regex')

    args = parser.parse_args()

    # Collect log files
    log_files = []
    for path_str in args.paths:
        path = Path(path_str)
        if path.is_file():
            log_files.append(path)
        elif path.is_dir():
            # Find log files in directory
            log_files.extend(path.rglob('*.log'))
            log_files.extend(path.rglob('*.txt'))

    if not log_files:
        log.error("log_miner.no_files")
        sys.exit(1)

    try:
        analysis = mine_logs(log_files, args.min_count)

        # Filter by pattern if specified
        if args.pattern:
            pattern_regex = re.compile(args.pattern, re.IGNORECASE)
            analysis['patterns'] = [
                p for p in analysis['patterns']
                if pattern_regex.search(p['normalized'])
            ]
            analysis['summary']['patterns_above_threshold'] = len(analysis['patterns'])

        # Write output
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False)

        log.info("log_miner.written", output=args.output)

        # Print summary
        print("\nLog Mining Summary:")
        print(f"  Total lines: {analysis['summary']['total_lines']}")
        print(f"  Unique patterns: {analysis['summary']['unique_patterns']}")
        print(f"  Patterns above threshold: {analysis['summary']['patterns_above_threshold']}")
        print(f"  Candidate atoms: {analysis['summary']['candidate_atoms']}")
        print(f"\nOutput written to: {args.output}")

    except Exception as e:
        log.error("log_miner.failed", error=str(e))
        sys.exit(1)


if __name__ == '__main__':
    main()
