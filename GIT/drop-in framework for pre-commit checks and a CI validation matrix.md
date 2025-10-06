1) Repository layout (minimal)
/atoms/                             # atom YAML files live here (any nesting ok)
/tools/atoms/
  atom_schema.json                  # JSON Schema for atom files
  atom_validator.py                 # validates atoms + deps + keys
  registry_tools.py                 # append-only ledger ops + index builder
  id_utils.py                       # ULID/UUIDv7 generation + regex helpers
  migrate_legacy_ids.py             # one-shot migrator (optional)
/registry/
  atoms.registry.jsonl              # append-only event ledger
  atoms.index.json                  # CI-built current-state index (derived)
.pre-commit-config.yaml

2) JSON Schema for a single atom file

Save as: tools/atoms/atom_schema.json

{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://example.org/atom.schema.json",
  "type": "object",
  "required": ["atom_uid", "atom_key", "title"],
  "additionalProperties": true,
  "properties": {
    "atom_uid": {
      "type": "string",
      "description": "ULID or UUIDv7",
      "pattern": "^[0-9A-HJKMNP-TV-Z]{26}$|^[0-9a-fA-F-]{36}$"
    },
    "atom_key": {
      "type": "string",
      "pattern": "^[a-z0-9-]+/[a-z0-9-]+/v[0-9]+/[a-z0-9-]+/[a-z0-9-]+/[0-9]{3}(-[a-z0-9-]+)?(-r[0-9]+)?$"
    },
    "title": { "type": "string", "minLength": 3 },
    "role": { "type": "string" },
    "inputs": { "type": "array", "items": { "type": "string" } },
    "outputs": { "type": "array", "items": { "type": "string" } },
    "deps": {
      "type": "array",
      "items": {
        "anyOf": [
          { "type": "string" },
          {
            "type": "object",
            "required": ["uid"],
            "properties": {
              "uid": { "type": "string" },
              "key_hint": { "type": "string" }
            },
            "additionalProperties": false
          }
        ]
      }
    },
    "status": {
      "type": "string",
      "enum": ["active", "deprecated", "removed", "split", "merged"]
    },
    "superseded_by": { "type": "string" },
    "split_into": { "type": "array", "items": { "type": "string" } },
    "merged_into": { "type": "string" },
    "display_order": { "type": "integer" },
    "rev_notes": { "type": "string" },
    "legacy_id": { "type": "string" }
  }
}

3) Validator script (local + CI)

Save as: tools/atoms/atom_validator.py

#!/usr/bin/env python3
import json, sys, re, pathlib
from jsonschema import Draft202012Validator
from collections import defaultdict

ROOT = pathlib.Path(__file__).resolve().parents[2]
SCHEMA = json.load(open(ROOT / "tools/atoms/atom_schema.json", "r", encoding="utf-8"))
validator = Draft202012Validator(SCHEMA)

ULID_RE = re.compile(r"^[0-9A-HJKMNP-TV-Z]{26}$")
UUID_RE = re.compile(r"^[0-9a-fA-F-]{36}$")
ATOM_KEY_RE = re.compile(r"^[a-z0-9-]+/[a-z0-9-]+/v[0-9]+/[a-z0-9-]+/[a-z0-9-]+/[0-9]{3}(-[a-z0-9-]+)?(-r[0-9]+)?$")

def iter_atom_files():
    atoms_dir = ROOT / "atoms"
    for p in atoms_dir.rglob("*.yml"):
        yield p
    for p in atoms_dir.rglob("*.yaml"):
        yield p

def read_yaml(path):
    # small, dependency-light YAML reader: accept JSON-as-YAML too
    import yaml  # if you prefer no external deps, require PyYAML via pre-commit
    return yaml.safe_load(open(path, "r", encoding="utf-8"))

def load_registry_current():
    # derive current-state view from append-only ledger
    reg = ROOT / "registry" / "atoms.registry.jsonl"
    current = {}
    if reg.exists():
        with open(reg, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    evt = json.loads(line)
                except json.JSONDecodeError:
                    continue
                uid = evt.get("atom_uid")
                if uid:
                    # last event wins
                    current[uid] = evt
    return current

def main():
    errors = []
    seen_uids = set()
    key_scope = defaultdict(set)  # scope by (workflow, version)
    by_uid = {}

    # parse all atoms
    atoms = []
    for f in iter_atom_files():
        data = read_yaml(f)
        if not data:
            errors.append(f"{f}: empty or invalid YAML")
            continue
        # schema validation
        for e in validator.iter_errors(data):
            errors.append(f"{f}: schema error: {e.message}")
        uid = data.get("atom_uid", "")
        key = data.get("atom_key", "")
        title = data.get("title", "")
        if not (ULID_RE.match(uid) or UUID_RE.match(uid)):
            errors.append(f"{f}: atom_uid invalid format: {uid}")
        if not ATOM_KEY_RE.match(key):
            errors.append(f"{f}: atom_key invalid format: {key}")
        if uid in seen_uids:
            errors.append(f"{f}: duplicate atom_uid: {uid}")
        seen_uids.add(uid)
        # key uniqueness within workflow version
        try:
            ns, wf, ver, ph, lane, seq_and_more = key.split("/", 5)
        except ValueError:
            ns = wf = ver = None
        if ns and wf and ver:
            scope = (f"{ns}/{wf}", ver)
            if key in key_scope[scope]:
                errors.append(f"{f}: duplicate atom_key within workflow version: {key}")
            key_scope[scope].add(key)
        # store
        by_uid[uid] = {"file": str(f), "data": data}
        atoms.append((f, data))

    # dep resolution
    registry_current = load_registry_current()
    known = set(by_uid.keys()) | set(registry_current.keys())
    def norm_dep(d):
        if isinstance(d, str):
            return d
        return d.get("uid")

    for f, data in atoms:
        for d in data.get("deps", []) or []:
            uid = norm_dep(d)
            if not uid:
                errors.append(f"{f}: dep entry missing uid")
                continue
            if uid not in known:
                errors.append(f"{f}: dep uid not found in atoms or registry: {uid}")

    # report and exit
    if errors:
        print("VALIDATION ERRORS:")
        for e in errors:
            print(" -", e)
        sys.exit(1)
    else:
        print(f"OK: {len(atoms)} atom files validated, {len(seen_uids)} unique UIDs, deps resolved.")

if __name__ == "__main__":
    main()


Notes

Uses JSON Schema + simple regexes.

Validates: schema, UID format, key format, UID uniqueness, key uniqueness per workflow version, dep UIDs resolvable (either in current repo or present in registry ledger).

4) Registry tools (append-only ledger + index builder)

Save as: tools/atoms/registry_tools.py

#!/usr/bin/env python3
import json, sys, pathlib, datetime

ROOT = pathlib.Path(__file__).resolve().parents[2]
REG = ROOT / "registry" / "atoms.registry.jsonl"
IDX = ROOT / "registry" / "atoms.index.json"

def append_event(evt: dict):
    REG.parent.mkdir(parents=True, exist_ok=True)
    evt.setdefault("timestamp", datetime.datetime.utcnow().isoformat() + "Z")
    with open(REG, "a", encoding="utf-8") as f:
        f.write(json.dumps(evt, ensure_ascii=False) + "\n")

def build_index():
    latest = {}
    if REG.exists():
        with open(REG, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    evt = json.loads(line)
                except json.JSONDecodeError:
                    continue
                uid = evt.get("atom_uid")
                if uid:
                    latest[uid] = evt
    IDX.write_text(json.dumps({"atoms": latest}, indent=2), encoding="utf-8")
    print(f"Wrote {IDX} with {len(latest)} atoms")

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "build-index":
        build_index()
    else:
        print("Usage: registry_tools.py build-index")
        sys.exit(2)


Typical append events (examples):

{"event":"created","atom_uid":"01J...ZQ","atom_key":"cli/dev-setup/v1/init/all/003","status":"active"}
{"event":"moved","atom_uid":"01J...ZQ","prev_key":"cli/dev-setup/v1/exec/all/012","atom_key":"cli/dev-setup/v1/val/all/012-r2"}
{"event":"deprecated","atom_uid":"01K...AA","reason":"superseded"}
{"event":"removed","atom_uid":"01K...AA","superseded_by":"01M...BB"}
{"event":"split","atom_uid":"01K...AA","split_into":["01N...AB","01N...CD"]}
{"event":"merged","atom_uid":"01P...EE","merged_into":"01Q...FF"}

5) Pre-commit setup

Save as: .pre-commit-config.yaml

repos:
  - repo: local
    hooks:
      - id: atom-validate
        name: Validate atomic YAMLs + deps + keys
        entry: python tools/atoms/atom_validator.py
        language: system
        files: ^atoms/.*\.(ya?ml)$
      - id: atom-schema-lint
        name: Ensure atom schema is valid JSON
        entry: python -c "import json,sys;json.load(open('tools/atoms/atom_schema.json'));print('schema ok')"
        language: system
        files: ^tools/atoms/atom_schema\.json$
      - id: registry-index
        name: Build atoms index (on commit)
        entry: python tools/atoms/registry_tools.py build-index
        language: system
        stages: [commit]


Install locally:

pip install pre-commit jsonschema pyyaml
pre-commit install

6) GitHub Actions — CI validation matrix

Save as: .github/workflows/atoms-validate.yml

name: Atoms Validate

on:
  pull_request:
  push:
    branches: [ main ]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.11' }
      - run: pip install jsonschema pyyaml
      - name: Validate atoms
        run: python tools/atoms/atom_validator.py
      - name: Build registry index
        run: python tools/atoms/registry_tools.py build-index
      - name: Upload index artifact
        uses: actions/upload-artifact@v4
        with:
          name: atoms-index
          path: registry/atoms.index.json


Optional: add a Windows job that runs the same validator (mirrors your environment diversity).

7) Migration flow (adds/removes/reorders without rewrites)

Adding an atom

Create atoms/<wf>/<v>/<phase>/<lane>/<seq>_<slug>.yaml with atom_uid (new ULID) + atom_key.

Append {"event":"created", ...} to atoms.registry.jsonl.

Run pre-commit → validator passes → CI builds index.

Removing/deprecating

Change status to deprecated or removed.

Append {"event":"deprecated"} or {"event":"removed"}.

If replaced: add superseded_by.

Rewrite any deps that should move to the successor.

Commit; pre-commit validates; CI updates index.

Reordering

Prefer editing display_order (no renumbering).

If moving phase/lane, bump -r<REV> in atom_key; append {"event":"moved","prev_key":...}.

Commit; validator + CI OK.

Splits/Merges

Keep old atom; mark split or merged.

Create new atoms with new atom_uids; write events (split, merged).

Rewrite deps as needed.

Commit; checks enforce dep resolvability.

8) Safety rails that catch problems automatically

Missing/duplicate atom_uid → blocked by validator.

Bad atom_key format → blocked.

Duplicate atom_key within same workflow version → blocked.

Deps pointing to nowhere → blocked (must exist in repo or registry).

Registry edits that aren’t append-only → caught by code review convention (optional: enforce via CI by diffing last commit’s registry lines count ≤ new count).

9) Developer quick commands

Validate locally:

python tools/atoms/atom_validator.py


Build index from registry:

python tools/atoms/registry_tools.py build-index


Run pre-commit on all files:

pre-commit run --all-files