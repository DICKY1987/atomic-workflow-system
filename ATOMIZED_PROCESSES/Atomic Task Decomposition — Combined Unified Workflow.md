Atomic Task Decomposition — Combined Unified Workflow
This document enumerates all atomic tasks present in the COMBINED.nested.yaml workflow. Each task is a single-responsibility operation assigned to a specific role. Branching tasks—where the same operation is performed by different roles—are listed separately.
Pipeline Layers (Seed Draft → Release & Observe)
atom_001: Seed Draft: collect_context | Role: planning_ai
atom_002: Seed Draft: structure_seed | Role: planning_ai
atom_003: Requirements: derive_requirements | Role: planning_ai
atom_004: Requirements: classify_requirements | Role: thinking_ai
atom_005: Scope: compose_scope | Role: planning_ai
atom_006: Architecture: model_architecture | Role: planning_ai
atom_007: Contracts: produce_openapi | Role: contract_validator
atom_008: Contracts: produce_db_schema | Role: contract_validator
atom_009: Contracts: produce_event_contracts | Role: contract_validator
atom_010: Task Decomposition: decompose | Role: planning_ai
atom_011: Task Decomposition: sequence | Role: thinking_ai
atom_012: Initial Codegen: codegen | Role: codegen_ai
atom_013: Test Hardening: build_test_matrix | Role: qa_test_agent
atom_014: Test Hardening: add_tests | Role: qa_test_agent
atom_015: Test Hardening: establish_coverage | Role: qa_test_agent
atom_016: Review & Compliance: review | Role: human_reviewer
atom_017: Review & Compliance: review | Role: static_analysis
atom_018: Release & Observe: release_plan | Role: orchestrator
atom_019: Release & Observe: configure_observability | Role: orchestrator
atom_020: Release & Observe: post_deploy | Role: orchestrator
atom_021: Release & Observe: capture_learnings | Role: orchestrator
Bridge L11 — Artifact Translation & Repo Bootstrap
atom_022: Artifact Translation & Repo Bootstrap: repo_init_or_update | Role: git_ops
atom_023: Artifact Translation & Repo Bootstrap: contracts_transform | Role: contract_validator
atom_024: Artifact Translation & Repo Bootstrap: build_moddoc | Role: brainstorm_bridge
atom_025: Artifact Translation & Repo Bootstrap: workplan_to_execution_plan | Role: brainstorm_bridge
atom_026: Artifact Translation & Repo Bootstrap: backlog_to_change_requests | Role: brainstorm_bridge
atom_027: Artifact Translation & Repo Bootstrap: handoff_gate | Role: gate
Workflow Phase: Plan & Route
atom_028: Plan & Route > Change Analysis: parse_change_request | Role: planning_ai
atom_029: Plan & Route > Change Analysis: analyze_affected_files | Role: planning_ai
atom_030: Plan & Route > Change Analysis: assess_change_complexity | Role: thinking_ai
atom_031: Plan & Route > Change Analysis: calculate_resource_requirements | Role: cost_resource_manager
atom_032: Plan & Route > Tool & Role Selection: select_primary_tools | Role: orchestrator
atom_033: Plan & Route > Tool & Role Selection: establish_fallback_chains | Role: orchestrator
atom_034: Plan & Route > Tool & Role Selection: validate_tool_availability | Role: orchestrator
atom_035: Plan & Route > Tool & Role Selection: enforce_cost_limits | Role: cost_resource_manager
atom_036: Plan & Route > Execution Planning: decompose_requirements | Role: planning_ai
atom_037: Plan & Route > Execution Planning: create_workstreams | Role: orchestrator
atom_038: Plan & Route > Execution Planning: establish_quality_gates | Role: qa_test_agent
atom_039: Plan & Route > Execution Planning: configure_rollback_points | Role: resilience_agent
atom_040: Plan & Route > Preflight Gates: schema_check | Role: orchestrator
atom_041: Plan & Route > Preflight Gates: secrets_license_policy_scan | Role: security_compliance
atom_042: Plan & Route > Preflight Gates: record_gate_results | Role: orchestrator
Workflow Phase: Execute & Validate
atom_043: Execute & Validate > Code Generation: generate_code_modifications | Role: work_cli_tools
atom_044: Execute & Validate > Code Generation: apply_changes_atomically | Role: repo_ai
atom_045: Execute & Validate > Code Generation: validate_with_vscode | Role: ide_code_editor
atom_046: Execute & Validate > Quality Validation: linting_formatting_typecheck | Role: qa_test_agent
atom_047: Execute & Validate > Quality Validation: security_scanning | Role: security_compliance
atom_048: Execute & Validate > Quality Validation: performance_checks | Role: qa_test_agent
atom_049: Execute & Validate > Testing: run_existing_tests | Role: qa_test_agent
atom_050: Execute & Validate > Testing: generate_new_tests_if_needed | Role: planning_ai
atom_051: Execute & Validate > Testing: measure_coverage_and_regressions | Role: qa_test_agent
atom_052: Execute & Validate > Resilience & Recovery: rollback_branch | Role: resilience_agent
atom_053: Execute & Validate > Resilience & Recovery: retry_with_backoff_or_fallback | Role: resilience_agent
atom_054: Execute & Validate > Resilience & Recovery: requeue_modified_plan | Role: orchestrator
Workflow Phase: Ship & Monitor
atom_055: Ship & Monitor > Merge Coordination: create_integration_branch | Role: merge_coordinator
atom_056: Ship & Monitor > Merge Coordination: apply_merge_train_strategy | Role: merge_coordinator
atom_057: Ship & Monitor > Merge Coordination: resolve_conflicts | Role: merge_coordinator
atom_058: Ship & Monitor > Merge Coordination: escalate_failures | Role: resilience_agent
atom_059: Ship & Monitor > Merge Coordination: run_integration_gates | Role: qa_test_agent
atom_060: Ship & Monitor > Merge Coordination: run_integration_gates | Role: security_compliance
atom_061: Ship & Monitor > Pull Request & Review: generate_pr_documentation | Role: docs_summarizer
atom_062: Ship & Monitor > Pull Request & Review: open_pr | Role: repo_ai
atom_063: Ship & Monitor > Pull Request & Review: automated_review_analysis | Role: thinking_ai
atom_064: Ship & Monitor > Pull Request & Review: automated_review_analysis | Role: qa_test_agent
atom_065: Ship & Monitor > Pull Request & Review: human_review_if_needed | Role: human_oversight
atom_066: Ship & Monitor > Final Merge & Deployment: squash_merge | Role: repo_ai
atom_067: Ship & Monitor > Final Merge & Deployment: tag_release_candidate | Role: repo_ai
atom_068: Ship & Monitor > Final Merge & Deployment: validate_post_merge_deployment | Role: qa_test_agent
atom_069: Ship & Monitor > Observability & Optimization: collect_metrics | Role: orchestrator
atom_070: Ship & Monitor > Observability & Optimization: collect_metrics | Role: cost_resource_manager
atom_071: Ship & Monitor > Observability & Optimization: analyze_trends_and_bottlenecks | Role: thinking_ai
atom_072: Ship & Monitor > Observability & Optimization: propose_improvements | Role: docs_summarizer
atom_073: Ship & Monitor > Observability & Optimization: propose_improvements | Role: planning_ai
Extended Deterministic Pipeline Stages & Workstreams
The following atoms extend the pipeline with additional deterministic stages and parallel workstreams from the deep-merge/multi configuration.
atom_074: Stage 0 — Prep Environment: install_dependencies_lock | Role: cost_resource_manager
atom_075: Stage 0 — Prep Environment: audit_dependencies | Role: security_compliance
atom_076: Stage 1 — Hygiene: format_code | Role: qa_test_agent
atom_077: Stage 1 — Hygiene: lint_code_fix | Role: qa_test_agent
atom_078: Stage 2 — Correctness: typecheck_code | Role: qa_test_agent
atom_079: Stage 2 — Correctness: run_tests | Role: qa_test_agent
atom_080: Stage 2 — Correctness: enforce_coverage | Role: qa_test_agent
atom_081: Stage 3 — Contracts & Migrations: api_contract_check | Role: contract_validator
atom_082: Stage 3 — Contracts & Migrations: db_contract_check | Role: contract_validator
atom_083: Stage 4 — Security & Advisory: security_review | Role: security_compliance
atom_084: Stage 4 — Security & Advisory: advisory_review | Role: human_reviewer
atom_085: Stage 4 — Security & Advisory: generate_pr_comments | Role: docs_summarizer
atom_086: Stage 6 — Fan-in: collect_change_requests | Role: orchestrator
atom_087: Stage 6 — Fan-in: generate_artifacts_manifest | Role: orchestrator
atom_088: Stage 6 — Fan-in: dedupe_change_requests | Role: orchestrator
atom_089: Stage 6 — Fan-in: score_and_rank_change_requests | Role: planning_ai
atom_090: Stage 7 — Dry-Run & Conflict Scan: simulate_merge_train | Role: merge_coordinator
atom_091: Stage 7 — Dry-Run & Conflict Scan: conflict_scan | Role: merge_coordinator
atom_092: Stage 8 — Validate Aggregated: typecheck_aggregated_changes | Role: qa_test_agent
atom_093: Stage 8 — Validate Aggregated: run_aggregated_tests | Role: qa_test_agent
atom_094: Stage 8 — Validate Aggregated: enforce_aggregated_coverage | Role: qa_test_agent
atom_095: Stage 8 — Validate Aggregated: aggregated_api_contract_check | Role: contract_validator
atom_096: Stage 8 — Validate Aggregated: export_public_surface | Role: docs_summarizer
atom_097: Stage 8 — Validate Aggregated: golden_diff_public_surface | Role: qa_test_agent
atom_098: Stage 9 — Quality Gates: summarize_gates | Role: qa_test_agent
atom_099: Stage 10 — Self-Healing Loop: route_failures_to_streams | Role: resilience_agent
atom_100: Stage 11 — Prepare Merge: compose_release_notes | Role: docs_summarizer
atom_101: Stage 11 — Prepare Merge: prepare_prs | Role: repo_ai
atom_102: Stage 12 — Join & Ship: execute_merge_train | Role: merge_coordinator
atom_103: WS1_FORMAT: checkout_branch_ws_format | Role: repo_ai
atom_104: WS1_FORMAT: run_format | Role: qa_test_agent
atom_105: WS1_FORMAT: run_lint_fix | Role: qa_test_agent
atom_106: WS2_LINT: checkout_branch_ws_lint | Role: repo_ai
atom_107: WS2_LINT: run_lint | Role: qa_test_agent
atom_108: WS2_LINT: run_typecheck_warn | Role: qa_test_agent
atom_109: WS3_CONTRACTS: checkout_branch_ws_contracts | Role: repo_ai
atom_110: WS3_CONTRACTS: run_api_contract_check | Role: contract_validator
atom_111: WS3_CONTRACTS: run_db_contract_check | Role: contract_validator
atom_112: WS4_TESTS: checkout_branch_ws_tests | Role: repo_ai
atom_113: WS4_TESTS: run_tests_report | Role: qa_test_agent
atom_114: WS4_TESTS: run_coverage_min | Role: qa_test_agent
atom_115: WS5_SECURITY: checkout_branch_ws_security | Role: repo_ai
atom_116: WS5_SECURITY: run_security_review | Role: security_compliance
atom_117: WS6_DEPS: checkout_branch_ws_deps | Role: repo_ai
atom_118: WS6_DEPS: run_deps_install_lock | Role: cost_resource_manager
atom_119: WS6_DEPS: run_deps_audit | Role: security_compliance
atom_120: WS7_MIGRATIONS: checkout_branch_ws_migrations | Role: repo_ai
atom_121: WS7_MIGRATIONS: run_migrations_check | Role: contract_validator
atom_122: WS8_SURFACE: checkout_branch_ws_api_surface | Role: repo_ai
atom_123: WS8_SURFACE: export_public_surface | Role: docs_summarizer
atom_124: WS8_SURFACE: golden_diff_public_surface | Role: qa_test_agent
atom_125: WS9_DOCTEST: checkout_branch_ws_doctest | Role: repo_ai
atom_126: WS9_DOCTEST: run_doctest | Role: qa_test_agent
atom_127: WS10_MERGE_TRAIN: checkout_branch_ws_merge_train | Role: repo_ai
atom_128: WS10_MERGE_TRAIN: simulate_merge_train | Role: merge_coordinator
atom_129: WS10_MERGE_TRAIN: conflict_scan | Role: merge_coordinator
________________________________________
