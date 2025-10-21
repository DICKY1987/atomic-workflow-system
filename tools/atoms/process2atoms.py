#!/usr/bin/env python3
"""
Process-doc → Atoms pipeline (non-interactive).

Parses an atomized process Markdown document with PHASE sections and YAML-like
code blocks listing atoms (e.g., `atom_001: title | Role: role`).
Generates per-atom YAML files with ULIDs and atom_keys, validates them,
and appends entries to an append-only JSONL registry.

Usage example:
  python tools/atoms/process2atoms.py \
    --doc ATOMIZED_PROCESSES/Tool-Agnostic Multi-Agent Code Modification Pipeline.md \
    --namespace cli --workflow code-mod-pipeline --version v1 \
    --atoms-dir atoms \
    --registry tools/atomic-workflow-system/atoms.registry.jsonl
"""

from __future__ import annotations

import argparse
import dataclasses
import datetime as dt
import json
import os
import re
import sys
from pathlib import Path

import structlog
import yaml

# Ensure local tools are importable when run from repo root
TOOLS_DIR = Path(__file__).parent
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

from atom_validator import validate_atom as validate_atom_file
from id_utils import build_atom_key, generate_ulid, validate_atom_key, validate_ulid

log = structlog.get_logger()


PHASE_HEADER_RE = re.compile(r"^##\s*PHASE\s*(?P<num>\d+)\s*:\s*(?P<title>.+?)\s*$", re.IGNORECASE)
SUBSECTION_RE = re.compile(
    r"^###\s*(?P<title>.*?)\s*(?:\[(?P<tag>AI MAKES DECISIONS|DETERMINISTIC)\])?.*$",
    re.IGNORECASE,
)
ATOM_LINE_RE = re.compile(r"^\s*atom_(?P<seq>\d{3})\s*:\s*(?P<title>[^|]+?)\s*\|\s*Role\s*:\s*(?P<role>.+?)\s*$",
                          re.IGNORECASE)


def slugify(text: str, max_len: int = 64) -> str:
    s = text.strip().lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = re.sub(r"-+", "-", s).strip("-")
    if max_len and len(s) > max_len:
        s = s[:max_len].rstrip("-")
    return s or "n-a"


def titleize(text: str) -> str:
    t = text.replace("_", " ").strip()
    # Keep acronyms readable; basic title case is fine here
    return re.sub(r"\s+", " ", t).title()


@dataclasses.dataclass
class AtomSpec:
    phase_slug: str
    lane: str  # 'ai' | 'det' | 'all'
    sequence: int
    raw_title: str
    role: str
    source_doc: Path

    @property
    def display_title(self) -> str:
        return titleize(self.raw_title)


def map_tag_to_lane(tag: str | None) -> str:
    if not tag:
        return "all"
    tag_norm = tag.strip().lower()
    if "ai makes decisions" in tag_norm:
        return "ai"
    if "deterministic" in tag_norm:
        return "det"
    return "all"


def parse_process_doc(doc_path: Path) -> tuple[str, list[AtomSpec]]:
    """
    Parse the process Markdown and return workflow title and list of AtomSpec.
    """
    text = doc_path.read_text(encoding="utf-8")
    lines = text.splitlines()

    workflow_title = None
    current_phase_slug = None
    current_lane = "all"
    in_code = False
    atoms: list[AtomSpec] = []

    # Workflow title from first H1 if present
    for ln in lines:
        if ln.startswith("# "):
            workflow_title = ln[2:].strip()
            break

    i = 0
    while i < len(lines):
        line = lines[i]

        m_phase = PHASE_HEADER_RE.match(line)
        if m_phase:
            num = int(m_phase.group("num"))
            title = m_phase.group("title").strip()
            current_phase_slug = f"p{num:02d}-{slugify(title)}"
            log.info("phase.detected", phase=current_phase_slug)
            i += 1
            continue

        m_sub = SUBSECTION_RE.match(line)
        if m_sub:
            tag = m_sub.group("tag")
            # Fallback: scan line for known tags if regex group missing
            raw_line = line.strip()
            if tag is None:
                if re.search(r"\[\s*AI MAKES DECISIONS\s*\]", raw_line, re.IGNORECASE):
                    tag = "AI MAKES DECISIONS"
                elif re.search(r"\[\s*DETERMINISTIC\s*\]", raw_line, re.IGNORECASE):
                    tag = "DETERMINISTIC"
            current_lane = map_tag_to_lane(tag)
            log.info(
                "subsection.detected",
                lane=current_lane,
                title=m_sub.group("title").strip(),
                tag=tag or "",
            )
            i += 1
            continue

        if line.strip().startswith("```"):
            in_code = not in_code
            i += 1
            continue

        if in_code:
            m_atom = ATOM_LINE_RE.match(line)
            if m_atom and current_phase_slug:
                seq = int(m_atom.group("seq"))
                raw_title = m_atom.group("title").strip()
                role = m_atom.group("role").strip().lower().replace(" ", "_")
                atoms.append(AtomSpec(
                    phase_slug=current_phase_slug,
                    lane=current_lane or "all",
                    sequence=seq,
                    raw_title=raw_title,
                    role=role,
                    source_doc=doc_path,
                ))
        i += 1

    # Dedup by (phase,lane,seq) keeping last occurrence
    dedup: dict[tuple[str, str, int], AtomSpec] = {}
    for a in atoms:
        dedup[(a.phase_slug, a.lane, a.sequence)] = a
    atoms_dedup = list(dedup.values())
    atoms_dedup.sort(key=lambda a: (a.phase_slug, a.lane, a.sequence))

    return workflow_title or slugify(doc_path.stem).replace("-", " "), atoms_dedup


def ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def read_registry_map(registry_path: Path) -> dict[str, str]:
    """Return map of atom_key -> last known atom_uid from JSONL registry."""
    if not registry_path.exists():
        return {}
    mp: dict[str, str] = {}
    with registry_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except Exception:
                continue
            uid = obj.get("atom_uid")
            key = obj.get("atom_key")
            if isinstance(uid, str) and isinstance(key, str):
                mp[key] = uid
    return mp


def append_registry_entries(registry_path: Path, entries: list[dict]) -> None:
    """Append entries atomically (best-effort lock file)."""
    # Simple lock file on Windows/Linux
    lock_path = registry_path.with_suffix(registry_path.suffix + ".lock")
    for _ in range(100):
        try:
            fd = os.open(str(lock_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.close(fd)
            break
        except FileExistsError:
            import time
            time.sleep(0.05)
    else:
        # Proceed without lock to avoid deadlock
        pass

    try:
        ensure_dir(registry_path.parent)
        with registry_path.open("a", encoding="utf-8") as f:
            for e in entries:
                f.write(json.dumps(e, ensure_ascii=False) + "\n")
    finally:
        try:
            if lock_path.exists():
                lock_path.unlink()
        except Exception:
            pass


def generate_yaml_and_registry(
    atoms: list[AtomSpec],
    *,
    namespace: str,
    workflow: str,
    version: str,
    atoms_dir: Path,
    registry_path: Path,
    dry_run: bool = False,
) -> dict[str, object]:
    registry_map = read_registry_map(registry_path)
    created, updated, skipped = 0, 0, 0
    out_files: list[str] = []
    reg_entries: list[dict] = []

    now = dt.datetime.utcnow().replace(tzinfo=dt.timezone.utc).isoformat()

    for a in atoms:
        atom_key = build_atom_key(namespace, workflow, version, a.phase_slug, a.lane, a.sequence)
        uid = registry_map.get(atom_key) or generate_ulid()
        if not validate_atom_key(atom_key):
            raise ValueError(f"Invalid atom_key generated: {atom_key}")
        if not validate_ulid(uid):
            raise ValueError(f"Invalid ULID generated/read: {uid}")

        rel_dir = Path(namespace) / workflow / version / a.phase_slug / a.lane
        dir_path = atoms_dir / rel_dir
        ensure_dir(dir_path)
        fname = f"{a.sequence:03d}_{slugify(a.raw_title, 48)}.yaml"
        file_path = dir_path / fname

        atom_yaml = {
            "atom_uid": uid,
            "atom_key": atom_key,
            "title": a.display_title,
            "role": a.role,
            # Helpful metadata (ignored by validator)
            "source_doc": str(a.source_doc),
            "mode": "ai" if a.lane == "ai" else ("deterministic" if a.lane == "det" else "unspecified"),
            "created_at": now,
        }

        existed = file_path.exists()
        if not dry_run:
            with file_path.open("w", encoding="utf-8") as f:
                yaml.safe_dump(atom_yaml, f, sort_keys=False)

            # Validate
            errors = validate_atom_file(file_path)
            if errors:
                raise RuntimeError(f"Validation failed for {file_path}: {errors}")

        action = "upsert" if atom_key in registry_map else "insert"
        reg_entries.append({
            "action": action,
            "atom_uid": uid,
            "atom_key": atom_key,
            "title": a.display_title,
            "role": a.role,
            "source_doc": str(a.source_doc),
            "version": version,
            "timestamp": now,
        })

        out_files.append(str(file_path))
        if existed:
            updated += 1
        else:
            created += 1

    if not dry_run and reg_entries:
        append_registry_entries(registry_path, reg_entries)

    return {
        "created": created,
        "updated": updated,
        "skipped": skipped,
        "files": out_files,
        "registry_appended": 0 if dry_run else len(reg_entries),
    }


def configure_logging() -> None:
    structlog.configure(
        processors=[
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer()
        ]
    )


def infer_workflow_slug(title: str) -> str:
    return slugify(title)


def main(argv: list[str] | None = None) -> int:
    configure_logging()
    p = argparse.ArgumentParser(description="Convert process doc to YAML atoms and update registry")
    src = p.add_mutually_exclusive_group(required=True)
    src.add_argument("--doc", help="Path to process Markdown document")
    src.add_argument("--docs-dir", help="Process all .md under this directory (non-recursive)")
    p.add_argument("--namespace", required=False, default="cli", help="Namespace (e.g., cli, hp)")
    p.add_argument("--workflow", required=False, help="Workflow slug (defaults from doc title)")
    p.add_argument("--version", required=False, default="v1", help="Workflow version (e.g., v1)")
    p.add_argument("--atoms-dir", required=False, default="atoms", help="Output atoms directory root")
    p.add_argument("--registry", required=False, default=str(Path("tools/atomic-workflow-system/atoms.registry.jsonl")),
                  help="Path to append-only JSONL registry")
    p.add_argument("--dry-run", action="store_true", help="Do not write files or registry; print summary")

    args = p.parse_args(argv)

    targets: list[Path] = []
    if args.doc:
        doc_path = Path(args.doc)
        if not doc_path.exists():
            print(f"Document not found: {doc_path}", file=sys.stderr)
            return 2
        targets = [doc_path]
    else:
        d = Path(args.docs_dir)
        if not d.exists() or not d.is_dir():
            print(f"Docs dir not found: {d}", file=sys.stderr)
            return 2
        targets = list(d.glob("*.md"))
        if not targets:
            print("No .md files found in docs-dir.", file=sys.stderr)
            return 3

    atoms_dir = Path(args.atoms_dir)
    registry_path = Path(args.registry)

    overall = {"ok": True, "runs": []}

    for doc_path in targets:
        workflow_title, atoms = parse_process_doc(doc_path)
        if not atoms:
            overall["runs"].append({"doc": str(doc_path), "ok": False, "error": "no_atoms"})
            overall["ok"] = False
            continue

        workflow = args.workflow or infer_workflow_slug(workflow_title)
        log.info("pipeline.start", workflow=workflow, namespace=args.namespace, version=args.version,
                 atoms_count=len(atoms), doc=str(doc_path))

        try:
            summary = generate_yaml_and_registry(
                atoms,
                namespace=args.namespace,
                workflow=workflow,
                version=args.version,
                atoms_dir=atoms_dir,
                registry_path=registry_path,
                dry_run=args.dry_run,
            )
        except Exception as e:
            log.error("pipeline.error", error=str(e), doc=str(doc_path))
            overall["runs"].append({"doc": str(doc_path), "ok": False, "error": str(e)})
            overall["ok"] = False
            continue

        res = {"doc": str(doc_path), "ok": True, "namespace": args.namespace, "workflow": workflow, "version": args.version, **summary}
        overall["runs"].append(res)
        log.info("pipeline.end", **res)

    print(json.dumps(overall, indent=2))
    return 0 if overall["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
