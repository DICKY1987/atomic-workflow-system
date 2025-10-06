Generic Atomic Workflow (Tool-Agnostic)
PHASE 0: Environment & Policy (Foundations)
0A. System Preconditions
atom_0001: detect_os_shell_and_permissions
atom_0002: verify_network_connectivity_and_dns
atom_0003: ensure_disk_space_min_threshold
atom_0004: set_execution_policy_noninteractive
atom_0005: initialize_logging_and_run_id

0B. Policy & Config
atom_0006: locate_or_create_config_file
atom_0007: validate_config_schema_and_required_keys
atom_0008: load_guardrails (allowed_paths, branch_policies, secrets_policy)
atom_0009: choose_language_runtime_versions (e.g., python_version)
atom_0010: lock_environment (resolver=any; lockfile=on)

PHASE 1: Intake & Scoping
1A. Intake Artifacts
atom_0011: collect_change_requests_or_goals
atom_0012: ingest_repo_state (structure, branches, tags)
atom_0013: discover_constraints (security, licensing, governance)
atom_0014: enumerate_dependencies (runtime, dev, ops)
atom_0015: detect_existing_ci_policies_and_quality_gates

1B. Initial Triage
atom_0016: classify_changes_by_domain (cli, api, db, tests, docs)
atom_0017: estimate_complexity (simple/moderate/complex)
atom_0018: map_affected_paths_and_overlap
atom_0019: identify_risks (conflicts, migrations, secrets)
atom_0020: decide_parallelization_candidates

PHASE 2: Planning & Routing
2A. Plan Build-Up
atom_0021: decompose_into_atomic_tasks
atom_0022: define_quality_gates_per_task (lint, type, unit, contract, security)
atom_0023: assign_cost_budget_and_retries
atom_0024: define_rollback_points_and_checkpoints
atom_0025: select_primary_execution_modes (parallel/sequential/hybrid)

2B. Routing (Tool/Agent Neutral)
atom_0026: score_task_complexity_and_routing_hints
atom_0027: map_tasks_to_generic_roles (planner, editor, tester, validator, integrator)
atom_0028: provision_fallback_chains_per_role
atom_0029: verify_role_availability (local/remote/autonomous)
atom_0030: freeze_execution_plan (v1) for auditability

PHASE 3: Workspace Preparation
3A. Isolation & Branching
atom_0031: create_isolated_workspaces (worktrees/containers/temp_dirs)
atom_0032: create_feature_branches_per_workstream
atom_0033: seed_workspace_configs (.env, settings, policy files)
atom_0034: register_workspaces_in_observability
atom_0035: write_precommit_or_prepush_hooks (policy-enforcing, non-vendor specific)

3B. Baseline Health
atom_0036: run_local_ci_baseline (lint/types/minimal_unit)
atom_0037: snapshot_repo_state (before_changes)
atom_0038: export_public_surface (apis/contracts) for golden-diff
atom_0039: warm_caches (lockfile, env, test discovery)
atom_0040: gate_ready_to_edit

PHASE 4: Execute Atomic Changes
4A. Edit Cycle (Deterministic Loop)
atom_0041: apply_minimal_change_set (one atom at a time)
atom_0042: record_diff_and_metadata (who/when/why)
atom_0043: run_quick_validators (lint/type/targeted_tests)
atom_0044: annotate_findings (failures, hints)
atom_0045: decide_retry_or_requeue (bounded attempts)

4B. Self-Healing & Fallback
atom_0046: retry_with_backoff
atom_0047: switch_role_or_strategy_on_persistent_failure
atom_0048: partial_rollback_to_last_checkpoint
atom_0049: open_issue_ticket_or_human_escalation
atom_0050: mark_atom_complete (pass/fail/fallback_used)

PHASE 5: Validation (Per-Workstream)
5A. Quality Verification
atom_0051: run_lint_and_style_suite
atom_0052: run_typecheck_suite (per_policy)
atom_0053: run_unit_tests_with_coverage
atom_0054: run_contract_checks (api/db/events)
atom_0055: run_security_scans (policy, not vendor-bound)

5B. Packaging & Evidence
atom_0056: compute_coverage_thresholds_and_regressions
atom_0057: export_artifacts (junit, coverage, html reports, diffs)
atom_0058: update_observability_with_results
atom_0059: freeze_workstream_summary (sha, metrics, status)
atom_0060: gate_ready_for_integration

PHASE 6: Integration & Fan-In
6A. Merge Strategy
atom_0061: choose_merge_sequence (risk-aware order)
atom_0062: dry_run_merge_train (conflict_scan)
atom_0063: integrate_workstream_1 → integration_branch
atom_0064: validate_integration_gates (unit/integration/contracts/security)
atom_0065: iterate_for_remaining_workstreams

6B. Conflict Handling
atom_0066: detect_and_classify_conflicts (file/logical/resource/semantic)
atom_0067: generate_resolution_options
atom_0068: apply_resolution_and_retest
atom_0069: escalate_if_blocked (human/role)
atom_0070: mark_integration_phase_complete

PHASE 7: CI/CD & Release
7A. CI Orchestration
atom_0071: trigger_pipeline (lint→types→unit→integration)
atom_0072: publish_artifacts (coverage, junit, reports)
atom_0073: enforce_quality_gates (fail_fast)
atom_0074: notify_channels (chat/email/webhook)
atom_0075: capture_ci_run_ids_for_audit

7B. Release & Deployment
atom_0076: tag_release_candidate
atom_0077: finalize_merge (squash/rebase per policy)
atom_0078: deploy_to_target_env (abstract provider)
atom_0079: verify_post_deploy_health
atom_0080: publish_release_notes_and_changelog

PHASE 8: Observe, Learn, Improve
8A. Metrics & Post-Run
atom_0081: aggregate_run_metrics (success_rate, retries, coverage, duration)
atom_0082: compute_cost_and_resource_usage
atom_0083: archive_logs_and_artifacts (retention_policy)
atom_0084: update_dashboards_and_scorecards
atom_0085: generate_postmortem_or_continuous_improvement_items

8B. Feedback Loop
atom_0086: mine_patterns_and_smells (recurring failures)
atom_0087: propose_policy_updates (gates, retries, thresholds)
atom_0088: refine_routing_and_parallelization_rules
atom_0089: refresh_lockfiles_and_env_pins_as_needed
atom_0090: close_run_and_prepare_next_cycle

CROSS-CUTTING (Always-On)
CC1. State, Audit, and Safety
atom_0091: maintain_state_checkpoints_per_phase
atom_0092: ensure_audit_trails (atoms, authorship, evidence)
atom_0093: enforce_guardrails (paths, branches, secrets)
atom_0094: deterministic_replay_support (inputs→outputs)
atom_0095: privacy_and_least_privilege_controls

CC2. Error Handling & Resilience
atom_0096: classify_errors (transient/persistent/systemic)
atom_0097: bounded_retries_and_backoff
atom_0098: circuit_breakers_and_quarantine
atom_0099: consistent_rollback_strategy
atom_0100: human_escalation_protocol