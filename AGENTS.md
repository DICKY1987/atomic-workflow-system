# Repository Guidelines

## Project Structure & Module Organization
- Root folders:
  - `atomic_two_id_tooling/` – core toolkit (atoms, schema, tools, docs, CI workflow).
  - `YAML_YML/` – workflow specs and generated atomic docs (reference assets).
  - `ATOMIZED_PROCESSES/` and `DOC & REF/` – background docs and references.
- In `atomic_two_id_tooling/`:
  - `atoms/` – atom definitions (`examples/`), JSON Schema (`schema/`).
  - `tools/atoms/` – Python utilities (validation, indexing, graph export, glossary).
  - `.github/workflows/atoms-ci.yaml` – CI entry to enforce atoms hygiene.
  - `Makefile` – common tasks.
  - Tests: add under `tests/` mirroring `tools/atoms/` or next to modules as `test_*.py`.

## Build, Test, and Development Commands
- Environment (PowerShell):
  - `python -m venv .venv`
  - `./.venv/Scripts/python.exe -m pip install -U pip pyyaml jsonschema pre-commit`
  - `pre-commit install`
- Core tasks (from `atomic_two_id_tooling/`):
  - `make validate` – schema, UID, deps, and contract checks.
  - `make index` / `make graph` – write `atoms.index.json`, `atoms.graph.*`.
  - `make glossary/fix` – auto-fix glossary issues; `make glossary/query` – query examples.
  - Without `make`: `python tools/atoms/<script>.py` (e.g., `index_builder.py`).
- Run a need search: `python tools/atoms/find_by_need.py json application/json schemas/users.schema.json`.

## Coding Style & Naming Conventions
- Python, 4-space indent; prefer type hints and short docstrings for public functions.
- Names: `snake_case` (functions/vars), `PascalCase` (classes), `UPPER_SNAKE_CASE` (constants).
- Keep modules focused; small, testable units. Use pre-commit hooks before pushing.

## Testing Guidelines
- Use `pytest`; name tests `test_*.py` and mirror package paths.
- Fast unit tests by default; mark slow/integration with `@pytest.mark.slow`.
- Run: `pytest -q` (optionally `pytest -q tests/pack_or_module`).

## Commit & Pull Request Guidelines
- Conventional Commits (e.g., `feat: add index builder`, `fix(atoms): enforce UID uniqueness`).
- One logical change per PR. Include: problem, approach, tradeoffs, testing notes; link issues.
- CI must be green: run `make validate`, `make index`, and relevant tests locally.

## Security & Configuration Tips
- Do not commit secrets. Use environment variables; add `config/.env.example` if new settings are introduced.
- Validate inputs; prefer explicit allow-lists in tools.

## Agent-Specific Instructions
- Prefer minimal, surgical patches; follow the structure above.
- Read `README.md` and `docs/` before changes; run validation and index builds to verify.
