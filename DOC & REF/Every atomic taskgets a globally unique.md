* Every **atomic task** gets a **globally unique, permanent ID** (for linking across workflows), plus a **human-readable key** that is stable within its workflow and friendly for docs.
* IDs remain stable even if you reorder phases or merge workflows.
* Collisions are impossible by construction.

# The Two-ID Rule (works great in practice)

1. **atom_uid** (machine ID, immutable, globally unique)

   * Format: **ULID** (26 chars, time-sortable) or **UUIDv7**.
   * Example: `01J9W4V4R8D8W0Q2Y5J7B0W4ZQ`
   * Purpose: cross-workflow linking, database keys, never changes.

2. **atom_key** (human key, structured, stable within workflow)

   * Format (recommended):

     ```
     <NS>/<WF>/<WFv>/<PH>/<LANE>/<SEQ>[-<VAR>][-r<REV>]
     ```
   * Where:

     * `NS`: namespace (org or program), e.g., `hp` or `cli`
     * `WF`: workflow slug, e.g., `dev-setup`, `multi-merge`
     * `WFv`: workflow version, `v1`, `v2`
     * `PH`: phase slug, e.g., `init`, `prep`, `exec`, `val`, `ci`, `obs`
     * `LANE`: optional lane (`simple`, `mod`, `complex`, or `all`)
     * `SEQ`: zero-padded sequence, `001`, `002`, …
     * `VAR`: optional variant (e.g., `win`, `linux`, `mac`, `api`, `db`)
     * `REV`: revision bump if task semantics change incompatibly
   * Example:

     * `cli/dev-setup/v1/init/all/003`
     * `cli/multi-merge/v2/exec/mod/014-api`
     * `hp/orchestrate/v3/val/complex/021-r2`
   * Purpose: easy to read, diff, and discuss; sortable; no global uniqueness guarantee needed because **atom_uid** is the canonical key.

> Rule of thumb: **Use `atom_uid` for machines, `atom_key` for humans.**

---

# Canonical Atom Schema (minimal + durable)

```yaml
atom_uid: 01J9W4V4R8D8W0Q2Y5J7B0W4ZQ   # ULID, immutable
atom_key: cli/dev-setup/v1/init/all/003
title: "Initialize .env and secrets policy"
role: "orchestrator"
inputs: [ ... ]
outputs: [ ... ]
deps:    # references are by atom_uid, not numbers
  - 01J9W4R0T1A5M3...                # upstream atom_uid
rev_notes: "bumped to r2 to enforce new policy format"
```

* **deps** should always point to **atom_uid** (never the human key), so cross-workflow links are stable even if a workflow slug or phase changes.

---

# Namespacing & Versioning Guidance

* **Namespace (`NS`)**: keep it short and stable (e.g., `cli`, `hp`, `eafix`). If you operate multiple orgs, use `org.project`.
* **Workflow version (`WFv`)**: bump when the workflow logic changes in a way that reorders or retitles atoms.
* **Revision (`-r<REV>`)**: bump when the atom’s semantics change incompatibly; keep the same `atom_uid` only if the change is truly backward-compatible. Otherwise: **new `atom_uid`**.

> Practical rule: **If consumers might break, mint a new `atom_uid`.**

---

# Sequencing Without Collisions

* Sequence **per phase per lane** (`/PH/LANE/SEQ`)—keeps numbers small and meaningful.
* Use **zero-padding** (`001`) so sorting works in file systems and spreadsheets.
* If you insert a task between `003` and `004`, append a variant:

  * `003a` (human key only) **or** better: `003-win`, `003-linux`.
  * The **atom_uid** is new and guarantees no collision.
* If a phase grows too large, start a new phase segment (`exec-2`) instead of renumbering.

---

# ID Minting Workflow (lightweight & deterministic)

1. **Create atom_key** from context (namespace, workflow, phase, lane, next seq).
2. **Generate atom_uid** using ULID/UUIDv7 at creation time.
3. **Register** in a repo-local registry (JSONL is fine):

   ```json
   {"atom_uid":"01J9W4...","atom_key":"cli/dev-setup/v1/init/all/003","title":"Initialize .env"}
   ```
4. **Pre-commit hook** validates:

   * `atom_uid` format
   * uniqueness of `atom_uid`
   * no duplicate `atom_key` within the same workflow version
   * deps reference existing `atom_uid`s
5. **CI gate** re-validates registry + cross-refs.

---

# Cross-Workflow Linking

* In any workflow, when you depend on external atoms, **reference their atom_uid** in `deps`.
* Optionally mirror the human key for readability:

  ```yaml
  deps:
    - uid: 01J9W4...ZQ
      key_hint: cli/multi-merge/v2/val/all/009
  ```
* To create **larger meta-workflows**, compose by `deps` only; `atom_key` is display sugar.

---

# Migration Plan from “Duplicate Numbers”

1. **Scan** all existing atoms; generate **atom_uid** for any missing.
2. **Compute** a new `atom_key` using the scheme; preserve original numbers as a new field `legacy_id` for traceability.
3. **Rewrite deps** to use `atom_uid` (keep `legacy_id_hint` if helpful).
4. **Introduce** a repo-level `atoms.registry.jsonl` and a pre-commit checker.
5. **Freeze**: disallow new atoms without both IDs.

---

# Example Set (shows differentiation clearly)

```
# Same semantic operation across 3 workflows is fine:
cli/dev-setup/v1/init/all/003
hp/orchestrate/v3/init/all/003
eafix/pipeline/v2/init/all/003

# Each has a different atom_uid (machine-unique), so no collisions.
```

---

# Practical Regex & Conventions

* **atom_key regex** (example):

  ```
  ^[a-z0-9-]+/[a-z0-9-]+/v[0-9]+/[a-z0-9-]+/[a-z0-9-]+/[0-9]{3}(-[a-z0-9-]+)?(-r[0-9]+)?$
  ```
* **File layout**:

  * `/atoms/<workflow>/<version>/<phase>/<lane>/<seq>_<slug>.yaml`
* **Git discipline**:

  * Include `atom_uid` in commit messages when a commit implements that atom.

---

# Why this works

* **Scales**: ULIDs remove global coordination; local sequences stay human-sized.
* **Stable linking**: deps by `atom_uid` survive renames/reorders/merges.
* **Readable**: `atom_key` gives immediate context in reviews and dashboards.
* **Auditable**: registry + hooks + CI = zero surprise collisions.

If you want, I can draft:

* a tiny **JSON Schema** for atom files,
* a **pre-commit** checker (PowerShell/Python),
* and a **one-shot migrator** to mint IDs and update deps across your current repos.
