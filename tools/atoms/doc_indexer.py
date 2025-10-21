#!/usr/bin/env python3
"""
Documentation indexer - builds hierarchical _index.json and _index.md.

Scans documentation directories and creates:
- _index.json: Machine-readable hierarchical index
- _index.md: Human-readable table of contents

Usage:
    python doc_indexer.py /path/to/docs --output-dir /path/to/docs
"""
import argparse
import json
import sys
from pathlib import Path
from typing import Optional

import structlog

log = structlog.get_logger()


def scan_directory(
    dir_path: Path,
    base_path: Path,
    max_depth: int = 10,
    current_depth: int = 0
) -> dict:
    """
    Recursively scan directory and build index structure.

    Args:
        dir_path: Directory to scan
        base_path: Base path for relative path calculation
        max_depth: Maximum depth to scan
        current_depth: Current recursion depth

    Returns:
        Dictionary representing directory structure
    """
    if current_depth >= max_depth:
        return None

    index = {
        'name': dir_path.name,
        'path': str(dir_path.relative_to(base_path)),
        'type': 'directory',
        'children': []
    }

    try:
        # Get all items in directory
        items = sorted(dir_path.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower()))

        for item in items:
            # Skip hidden files and index files
            if item.name.startswith('.') or item.name.startswith('_index'):
                continue

            if item.is_dir():
                # Recursively scan subdirectory
                subdir_index = scan_directory(item, base_path, max_depth, current_depth + 1)
                if subdir_index:
                    index['children'].append(subdir_index)
            elif item.is_file():
                # Add file entry
                file_entry = {
                    'name': item.name,
                    'path': str(item.relative_to(base_path)),
                    'type': 'file',
                    'extension': item.suffix
                }

                # Try to extract title from markdown files
                if item.suffix in ['.md', '.markdown']:
                    title = extract_markdown_title(item)
                    if title:
                        file_entry['title'] = title

                index['children'].append(file_entry)

    except PermissionError:
        log.warning("doc_indexer.permission_denied", path=str(dir_path))

    return index


def extract_markdown_title(md_path: Path) -> Optional[str]:
    """
    Extract title from markdown file (first # heading).

    Args:
        md_path: Path to markdown file

    Returns:
        Title string or None
    """
    try:
        with open(md_path, encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line.startswith('# ') and not line.startswith('## '):
                    return line[2:].strip()
                # Stop after first 50 lines
                if f.tell() > 5000:
                    break
    except Exception as e:
        log.debug("doc_indexer.title_extract_failed", path=str(md_path), error=str(e))

    return None


def generate_markdown_toc(index: dict, level: int = 0) -> str:
    """
    Generate markdown table of contents from index.

    Args:
        index: Index dictionary
        level: Current indentation level

    Returns:
        Markdown string
    """
    lines = []
    indent = '  ' * level

    if index['type'] == 'directory':
        if level > 0:  # Don't show root directory
            lines.append(f"{indent}- **{index['name']}/**")

        for child in index.get('children', []):
            child_md = generate_markdown_toc(child, level + 1 if level > 0 or index.get('name') != '.' else level)
            if child_md:
                lines.append(child_md)

    elif index['type'] == 'file':
        title = index.get('title', index['name'])
        path = index['path']
        lines.append(f"{indent}- [{title}]({path})")

    return '\n'.join(lines)


def build_index(
    docs_path: Path,
    output_dir: Optional[Path] = None,
    max_depth: int = 10
) -> dict:
    """
    Build index files for documentation directory.

    Args:
        docs_path: Path to documentation root
        output_dir: Directory to write index files (default: docs_path)
        max_depth: Maximum directory depth to scan

    Returns:
        Index dictionary
    """
    log.info("doc_indexer.building", path=str(docs_path))

    if not docs_path.is_dir():
        raise ValueError(f"Not a directory: {docs_path}")

    if output_dir is None:
        output_dir = docs_path

    # Build index structure
    index = scan_directory(docs_path, docs_path, max_depth)

    # Write JSON index
    json_path = output_dir / '_index.json'
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(index, f, indent=2, ensure_ascii=False)
    log.info("doc_indexer.json_written", path=str(json_path))

    # Generate and write markdown TOC
    toc = f"""# Documentation Index

Auto-generated index of documentation files.

{generate_markdown_toc(index)}

---
*Generated by doc_indexer.py*
"""

    md_path = output_dir / '_index.md'
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(toc)
    log.info("doc_indexer.md_written", path=str(md_path))

    # Log statistics
    file_count = count_files(index)
    dir_count = count_directories(index)
    log.info("doc_indexer.complete",
             files=file_count,
             directories=dir_count,
             json=str(json_path),
             md=str(md_path))

    return index


def count_files(index: dict) -> int:
    """Count total files in index."""
    if index['type'] == 'file':
        return 1
    count = 0
    for child in index.get('children', []):
        count += count_files(child)
    return count


def count_directories(index: dict) -> int:
    """Count total directories in index."""
    if index['type'] == 'file':
        return 0
    count = 1
    for child in index.get('children', []):
        if child['type'] == 'directory':
            count += count_directories(child)
    return count


def main():
    """CLI entry point."""
    structlog.configure(
        processors=[
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer()
        ]
    )

    parser = argparse.ArgumentParser(description='Build documentation index files')
    parser.add_argument('docs_path', help='Path to documentation directory')
    parser.add_argument('--output-dir', help='Output directory for index files (default: docs_path)')
    parser.add_argument('--max-depth', type=int, default=10, help='Maximum directory depth (default: 10)')

    args = parser.parse_args()

    try:
        docs_path = Path(args.docs_path)
        output_dir = Path(args.output_dir) if args.output_dir else None

        build_index(docs_path, output_dir, args.max_depth)

    except Exception as e:
        log.error("doc_indexer.failed", error=str(e))
        sys.exit(1)


if __name__ == '__main__':
    main()
