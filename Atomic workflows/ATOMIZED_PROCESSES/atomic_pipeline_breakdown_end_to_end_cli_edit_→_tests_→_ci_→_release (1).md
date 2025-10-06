# Atomic Pipeline Breakdown — End-to-End (CLI Edit → Tests → CI → Release)

**Core philosophy:** Every step is an **atom** with a single responsibility, independently testable, and swappable without affecting neighbors. Names are machine-friendly to wire into scripts/automations.

---

## The Stack (Tools & Applications)

> Single sources of truth first: pick **one** dependency locker (prefer **uv** or pip-tools) and **one** task runner (**Taskfile** or **nox**). Key caches to the lockfile hash so CI = Local.

### Runtimes & Base Tooling
- **Python 3.12** (baseline; CI matrix can include 3.11)
- **PowerShell 7** (Windows scripts, Pester)
- **Git** (VCS, branch/PR automation)
- **Node.js (optional)** (VS Code extension support)
- **Docker Desktop (optional)** (containerized integration/E2E)

### Editor & UX
- **VS Code** with extensions:
  - Python, Pylance, PowerShell
  - GitHub Copilot (optional)
  - Error Lens, Coverage Gutters, YAML, GitLens
  - Pre-commit Helper, Better Comments, Todo Tree (optional)

### Python Quality & Testing Stack
- **pytest** (+ **pytest-cov**, **pytest-xdist**, **pytest-timeout**, **pytest-mock**, **pytest-asyncio**)
- **ruff**, **black**, **mypy** (lint/format/types)
- **pre-commit** (local hooks)
- **coverage.py** (XML/HTML reports)
- **bandit**, **safety** (security scans; CI preferred)

### PowerShell Quality
- **Pester** (tests)
- **PSScriptAnalyzer** (lint)

### DevOps & CLI Utilities
- **GitHub CLI (gh)** (PRs, releases)
- **jq / yq** (JSON/YAML transforms in guardrails & CI)
- **ripgrep (rg) / fd** (fast code search)
- **7-Zip** (artifact bundling)
- **Taskfile** *or* **nox** *or* **Make** (choose one for local CI orchestration)

### CI & Observability
- **GitHub Actions** (jobs: lint/types, unit, integration, e2e, pester)
- **Codecov (optional)** (coverage trends & PR comments)
- **Slack GitHub Action (optional)** (alerts)

### Optional Generators
- **auger-python** (manual, curated unit test generation)

### Stack ↔ Atom Mapping (high level)
- **Bootstrap/Config (Phase 0–1):** Python, Git, PowerShell, Node/Docker, VS Code, pre-commit
- **Guardrailed CLI (Phase 2–3):** gh/CLI tool + jq/yq + rg/fd + git
- **Static Triage (Phase 4):** ruff, black (check), mypy
- **Unit Loop (Phase 5–7):** pytest (+plugins), coverage, Task/nox runner
- **Auto-Fix (Phase 8):** Task/nox orchestrating bounded retries
- **Integration/E2E (Phase 9–10):** pytest markers, Docker (if needed)
- **Reports/CI (Phase 11–13):** coverage xml/html, GitHub Actions, Codecov, Slack
- **Powershell Track:** Pester, PSScriptAnalyzer on Windows job
- **Generators (Phase 14):** auger-python (local only)

## PHASE 0 — Machine & Workspace Bootstrap (foundations)
```yaml
atom_000: detect_host_os_and_shell               # windows/linux/macos; bash/pwsh
atom_001: install_python_runtime                 # 3.11+ baseline
atom_002: install_git_cli                        # vcs operations
atom_003: install_powershell_if_applicable       # pester & tasks (optional on *nix)
atom_004: install_node_optional_for_vscode       # some extensions require it (optional)
atom_005: install_docker_optional                # for containerized tests (optional)
atom_006: create_project_directory_structure     # src/, tests/, scripts/, .vscode/, .github/
atom_007: initialize_git_repository              # git init, default branch, remotes
atom_008: configure_gitignore_and_attributes     # keep caches/artifacts out of vcs
atom_009: create_virtual_environment             # .venv via uv/venv
atom_010: choose_dependency_manager              # uv (preferred) or pip/pip-tools
atom_011: compile_lockfile_and_sync              # deterministic installs
atom_012: verify_toolchain_versions              # python/pip/pytest/ruff/mypy present
```

## PHASE 1 — Project Configuration (single-source-of-truth)
```yaml
atom_013: author_pyproject_toml_core             # project metadata & deps
atom_014: configure_pytest_plugins_and_markers   # unit/integration/e2e/contracts, addopts
atom_015: configure_coverage_thresholds          # fail-under; xml/html reports
atom_016: configure_ruff_black_mypy              # line-length, target-version, strictness
atom_017: scaffold_test_pyramid_directories      # tests/unit|integration|e2e|contracts
atom_018: add_conftest_shared_fixtures           # tmp paths, httpx client, git repo fakes
atom_019: create_precommit_config                # ruff/black/yaml + optional mypy/bandit
atom_020: seed_vscode_settings_tasks_extensions  # testing, coverage gutters, error lens
atom_021: create_ci_workflow_skeleton            # .github/workflows/ci.yml jobs & caches
```

## PHASE 2 — Guardrailed CLI Edit Session (when AI/CLI edits code)
```yaml
atom_022: start_cli_edit_guardrail               # wrap Codex/Claude/Gemini with timeout
atom_023: capture_pre_edit_snapshot              # git status/diff, file hashes
atom_024: execute_cli_tool_with_policies         # working dir, allowlist, resource caps
atom_025: archive_cli_session_logs               # transcripts + stdout/stderr to artifacts/
atom_026: detect_cli_completion_signal           # exit code, file system events
```

## PHASE 3 — Trigger & Isolation (post-edit safety)
```yaml
atom_027: detect_modified_paths_since_snapshot   # compute changed files list
atom_028: create_fix_branch_and_checkpoint       # git switch -c fix/<topic> + commit
atom_029: annotate_commit_with_cli_metadata      # tool name, time, seed, config
atom_030: write_artifact_index_json              # pointers to logs, diffs, reports
```

## PHASE 4 — Fast Static Triage (seconds)
```yaml
atom_031: run_ruff_lint                          # style/errors; autofix off in CI
atom_032: run_black_check                        # formatting check only
atom_033: run_mypy_typecheck                     # strict on changed paths first
atom_034: aggregate_static_findings              # machine-readable SARIF/JSON
atom_035: classify_static_failures               # lint|format|type → pick fix-lane
```

## PHASE 5 — Targeted Unit Tests (minutes → fast)
```yaml
atom_036: select_impacted_unit_tests             # map changed src → nearest tests
atom_037: run_pytest_unit_with_coverage          # --cov=src; stop on first failure
atom_038: parallelize_unit_suite_optional        # -n auto (xdist)
atom_039: enforce_coverage_budget                # fail-under gate
atom_040: export_junit_and_coverage_artifacts    # junit.xml, coverage.xml, htmlcov/
```

## PHASE 6 — Red/Green Rapid Loop (developer feedback)
```yaml
atom_041: start_loop_on_fail                     # pytest --lf --maxfail=1 or ptw
atom_042: route_fix_lane_lint_format             # apply ruff --fix / black (local only)
atom_043: route_fix_lane_types_interfaces        # repair signatures, Protocols, TypedDicts
atom_044: route_fix_lane_behavior                # adjust logic + add/repair unit tests
atom_045: update_shared_fixtures_as_needed       # conftest: tmp projects, httpx, git
atom_046: repeat_unit_tests_until_green
```

## PHASE 7 — Local CI Bundle (single command gate)
```yaml
atom_047: run_local_ci_script                    # scripts/local_ci.(sh|ps1)
atom_048: stage1_lint_types                      # ruff/black --check/mypy changed→all
atom_049: stage2_unit_tests                      # pytest -q tests/unit --cov
atom_050: stage3_static_artifacts_emit           # junit/coverage/sarif to artifacts/
atom_051: compute_local_ci_exit_code             # gate push if non-zero
```

## PHASE 8 — Autonomous Fix Loop (optional, bounded)
```yaml
atom_052: configure_auto_fix_iterations          # N tries, stop on first green
atom_053: run_auto_fix_cycle_once                # re-run local CI → propose patch
atom_054: apply_guarded_patch                    # minimal diff; never commit automatically
atom_055: emit_auto_fix_report                   # what changed and why
atom_056: terminate_auto_fix_on_green_or_limit   # green → proceed; else manual
```

## PHASE 9 — Integration Tests (systems interaction)
```yaml
atom_057: provision_integration_env              # temp dirs, fake repos, env vars
atom_058: run_pytest_integration                 # -m integration; moderate speed
atom_059: exercise_adapters_and_endpoints        # git ops, filesystem, FastAPI TestClient
atom_060: collect_integration_artifacts          # logs, junit, coverage (partial)
atom_061: gate_on_integration_results            # required for PRs
```

## PHASE 10 — E2E/Feature Tests (critical paths)
```yaml
atom_062: stage_e2e_preconditions                # mock services; opt. container spin-up
atom_063: run_pytest_e2e                         # -m e2e; slower, real CLI commands
atom_064: simulate_quality_workflow              # lint→fix→test→commit full path
atom_065: capture_e2e_artifacts                  # screenshots/logs/junit
atom_066: mark_e2e_required_on_main              # not required on PRs, yes on main
```

## PHASE 11 — Reports & Observability
```yaml
atom_067: generate_coverage_xml_html             # for dashboards and Codecov
atom_068: publish_local_reports_index            # artifacts/index.html for quick triage
atom_069: summarize_test_outcomes_for_pr         # short report → PR template/comment
```

## PHASE 12 — Commit, PR, and Branch Protections
```yaml
atom_070: commit_fix_with_conventional_message   # feat/fix/test: scope + summary
atom_071: push_branch_and_open_pr                # link artifacts; assign reviewers
atom_072: enforce_branch_protection_rules        # required checks, review, linear history
```

## PHASE 13 — CI Orchestration (GitHub Actions)
```yaml
atom_073: ci_job_lint_types                      # fast fail job
atom_074: ci_job_unit_linux_matrix               # 3.11/3.12 matrix, cache by lock hash
atom_075: ci_job_integration_linux               # gated on unit success
atom_076: ci_job_pester_windows_optional         # run PowerShell tests when scripts/
atom_077: ci_job_e2e_on_main_nightly             # heavier path; scheduled nightly too
atom_078: ci_publish_artifacts                   # junit.xml, coverage.xml, htmlcov/
atom_079: ci_codecov_upload_optional             # coverage trend & PR comments
atom_080: ci_slack_notification_on_failure       # link to failing job/run
```

## PHASE 14 — Optional: Auger-Assisted Test Generation (manual, curated)
```yaml
atom_081: select_pure_module_for_recording       # deterministic inputs/outputs only
atom_082: author_minimal_driver_script           # tools/record_<module>.py
atom_083: wrap_driver_with_auger_magic           # with auger.magic([target]): main()
atom_084: execute_driver_in_isolated_env         # poetry or venv per service
atom_085: collect_generated_unittest_files       # under tests/auger/<module>/
atom_086: curate_and_deduplicate_cases           # remove brittle I/O/time cases
atom_087: mark_generated_tests_for_selection     # @pytest.mark.generated or folder mark
atom_088: run_pytest_and_commit_curated_tests    # add to coverage; track stability
```

## PHASE 15 — Merge, Release, and Cleanup
```yaml
atom_089: merge_pr_via_squash_or_merge           # follow repo policy
atom_090: tag_release_if_applicable              # semantic version; changelog
atom_091: delete_feature_branch                  # cleanup remote & local
atom_092: sync_local_main_and_dependencies       # pull --rebase; lock refresh if needed
```

## PHASE 16 — Parallelization & Multi-Workstream Coordination (optional advanced)
```yaml
atom_093: enumerate_workflows_from_backlog       # map changes → independent streams
atom_094: build_dependency_graph_across_streams  # explicit + inferred deps
atom_095: detect_conflicts_and_overlaps          # file scope, API/schema, resources
atom_096: score_parallelization_opportunities    # independence vs risk/contention
atom_097: form_parallel_execution_clusters       # safe groups + isolation boundaries
atom_098: schedule_clustered_execution_levels    # topo levels with per-level parallel
atom_099: instrument_real_time_monitoring        # progress/quality/cost dashboards
atom_100: enact_dynamic_adjustments_or_rollback  # isolate failures; re-plan quickly
```

## PHASE 17 — Cross-Cutting: Security, Secrets, and Compliance
```yaml
atom_101: manage_env_and_secrets_safely          # .env templates, GH secrets only
atom_102: run_security_linters_and_scans         # bandit/safety in CI (optionally pre-push)
atom_103: enforce_artifact_privacy_and_retention # redact secrets; retention policy
atom_104: audit_logging_for_tooling_and_ci       # who ran what and when
```

## PHASE 18 — Cross-Cutting: Error Handling & Recovery
```yaml
atom_105: classify_pipeline_failures             # static|unit|integration|e2e|infra
atom_106: surface_actionable_diagnostics         # link logs, diffs, repro commands
atom_107: implement_checkpoint_and_retry_policies# re-run flaky tests with bounds
atom_108: support_manual_override_and_escalation # notify + owner playbooks
```

## PHASE 19 — Cross-Cutting: Performance & Cost
```yaml
atom_109: cache_dependencies_effectively         # keyed by os+py+lockhash
atom_110: shard_and_parallelize_tests_where_safe # xdist; exclude slow on PR
atom_111: watch_ci_duration_and_flakiness        # trend dashboards; alert on regressions
```

## PHASE 20 — Definition of Done (per change)
```yaml
atom_112: precommit_hooks_clean                  # ruff/black/yaml (and optional mypy)
atom_113: local_ci_green                         # lint/types/unit passing locally
atom_114: unit_coverage_meets_threshold          # fail-under satisfied
atom_115: integration_pass_for_affected_areas    # adapters/endpoints when touched
atom_116: e2e_pass_on_main_if_critical_path      # guarded on branch policy
atom_117: artifacts_uploaded_and_linked          # junit/coverage/htmlcov in CI
atom_118: pr_checks_green_and_approved           # required reviewers + checks
```

---

### Minimal Command Map (wire atoms into scripts)
```
local: scripts/local_ci.(sh|ps1)
  → ruff . && black --check . && mypy src/
  → pytest -q tests/unit --cov=src --maxfail=1

on-demand: pytest --lf  # re-run last failures
watch: ptw tests/unit/  # or pytest --looponfail
integration: pytest -m integration -q
E2E: pytest -m e2e -q
coverage html/xml: pytest --cov=src --cov-report=xml --cov-report=html
```

---

## Appendix — Folder & Artifact Conventions
```
/
  src/                    # application code
  tests/
    unit/                 # fast, isolated
    integration/          # adapters, endpoints, fs/git
    e2e/                  # full workflows
    contracts/            # schema/contract tests
    auger/                # curated auto-generated tests (optional)
    fixtures/             # static inputs
  artifacts/
    cli_runs/<tool>/<ts>/ # logs/diffs from guardrailed CLI sessions
    reports/              # junit.xml, coverage.xml, htmlcov/
  .github/workflows/      # CI jobs
  .vscode/                # workspace settings & tasks
  scripts/                # local_ci, guardrail launchers, helpers
```

**Use this as the master checklist**—you can implement atoms incrementally and still keep the pipeline coherent, deterministic, and observable.

