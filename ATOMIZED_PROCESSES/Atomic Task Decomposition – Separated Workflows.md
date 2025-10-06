Atomic Task Decomposition – Separated Workflows
This document follows the style of the project’s atomic pipeline breakdown. Each workflow identified in the repository is decomposed into atomic tasks. Tasks are presented as YAML‑friendly identifiers (atom_xxx) with descriptive names and optional comments. Where relevant, citations reference the source lines that describe the task.
________________________________________
Multi‑CLI Orchestrator (MO)
The TaskOrchestrator class orchestrates code edits by analysing task complexity, selecting tools and executing commands. Its atoms are grouped by function.
# Phase MO0 – Context and Analysis
mo_atom_000: create_context_object                  # initialize context with ID and metadata
mo_atom_001: record_start_time_and_prompt           # capture start time and user prompt
mo_atom_002: count_files_and_lines                  # compute number of files and total lines
mo_atom_003: scan_for_keywords                      # search prompts/files for complexity keywords
mo_atom_004: compute_complexity_score               # derive complexity level (simple/moderate/complex)

# Phase MO1 – Planning
mo_atom_005: select_toolchain_based_on_complexity    # choose Aider/Copilot/Claude or fallback
mo_atom_006: check_hard_constraints                  # verify git clean and path allowlist (not explicitly shown but implied)
mo_atom_007: assemble_execution_plan                 # build ordered list of tools and steps

# Phase MO2 – Execution
mo_atom_008: invoke_cli_tool                         # run tool command for current step
mo_atom_009: capture_tool_output                     # store stdout/stderr for parsing
mo_atom_010: detect_file_changes                     # check which files were modified
mo_atom_011: parse_delegation_suggestions            # inspect output for recommended delegation
mo_atom_012: update_plan_with_delegations            # adjust plan if another tool is suggested
mo_atom_013: iterate_over_plan                       # loop through remaining steps

# Phase MO3 – Summary
mo_atom_014: compile_results_summary                 # summarise tools used and reasoning
mo_atom_015: emit_final_output                       # return summary to caller
________________________________________
Free‑Tier Orchestrator (FT)
The free_tier_orchestrator.ps1 script manages lanes and token quotas. Atoms are grouped by command.
# Command: init
ft_atom_000: create_ai_directory_and_gitignore      # ensure .ai directory exists
ft_atom_001: initialize_quota_tracker               # create quota‑tracker.json
ft_atom_002: select_best_service_by_quota           # choose local/HF/Claude based on token availability
ft_atom_003: pull_local_models_with_ollama          # download models like codellama/phi
ft_atom_004: verify_model_runtime                   # test that models run successfully

# Command: init‑lane
ft_atom_005: create_git_worktree_for_lane           # git worktree add for new lane
ft_atom_006: copy_configuration_to_lane             # clone .ai and tool configs into lane
ft_atom_007: register_lane_watchers                 # configure watchers and deadlines

# Command: start‑lane
ft_atom_008: verify_lane_exists                     # check branch/worktree presence
ft_atom_009: display_vscode_command                 # show code --reuse-window command
ft_atom_010: list_available_tools_and_deadlines      # print allowed tools and time limits

# Command: submit‑lane
ft_atom_011: validate_changed_files                 # ensure only allowed files changed
ft_atom_012: run_precommit_checks                   # ruff/mypy/pytest pre‑commit scripts
ft_atom_013: commit_and_push_lane                   # commit with message and push to remote
ft_atom_014: notify_watchers_of_submission          # send notifications upon submission

# Command: integrate
ft_atom_015: merge_lane_into_integration            # reset integration branch and merge lane
ft_atom_016: run_integration_tests                  # execute project’s integration tests
ft_atom_017: fast_forward_or_rollback               # fast‑forward on success or revert on failure

# Command: status
ft_atom_018: show_token_quota_status                # display spent and remaining tokens
ft_atom_019: report_lane_statuses                   # list active lanes and integration status
________________________________________
Granular Multi‑Phase Workflow (GF)
This document outlines a robust multi‑phase workflow for large tasks. The phases and tasks are captured below.
# Phase GF1 – System Preparation & Inventory
gf_atom_000: create_ai_directory_and_worktrees      # ensure .ai and multiple worktrees exist
gf_atom_001: initialize_quota_tracker_and_tools     # set up quota tracker and validate tools
gf_atom_002: scan_file_inventory                    # list files and gather size/line metrics
gf_atom_003: parse_project_documentation            # read README and docs for requirements

# Phase GF2 – Gap Analysis & Routing
gf_atom_004: perform_gap_analysis                   # compare current code with requirements
gf_atom_005: estimate_task_complexity               # assign complexity categories and token counts
gf_atom_006: route_tasks_via_decision_matrix        # map tasks to simple/moderate/complex lanes
gf_atom_007: request_user_approval_for_premium      # prompt user for cost approvals

# Phase GF3 – Execution
gf_atom_008: init_simple_worktree_and_run_gemini     # create simple lane and run gemini CLI
gf_atom_009: auto_test_and_commit_simple_changes     # run tests and auto‑commit successful changes
gf_atom_010: init_moderate_worktree_and_run_aider    # create moderate lane and engage Aider
gf_atom_011: run_tests_and_commit_moderate           # execute tests and commit moderate lane
gf_atom_012: init_complex_worktree_and_run_claude    # set up complex lane and call Claude Code
gf_atom_013: implement_complex_features             # multi‑step code generation (models, routes, tests)
gf_atom_014: triage_failing_tests_with_vscode        # start VS Code diagnostics and export report
gf_atom_015: categorize_and_route_issues             # classify issues into auto‑fix, Aider or manual

# Phase GF4 – Integration & Quality Assurance
gf_atom_016: resolve_dependencies_and_update         # align dependencies across lanes
gf_atom_017: run_integration_tests_and_fixtures      # execute integration tests and fix issues
gf_atom_018: perform_security_and_quality_scans      # run bandit/safety/lint

# Phase GF5 – Merge & Finalization
gf_atom_019: sequential_merge_branches              # merge lanes back sequentially
gf_atom_020: conduct_final_validation               # final smoke tests and manual checks
________________________________________
Symbiotic CLI Workflows (SY)
These workflows describe how Claude Code and OpenAI Codex collaborate. Each workflow is treated separately.
# Workflow SY1 – Feature Implementation & Tests
sy1_atom_000: capture_feature_request               # parse high‑level feature description
sy1_atom_001: run_claude_for_planning_and_impl       # Claude analyses code and implements changes
sy1_atom_002: identify_modified_files               # list files/functions changed by Claude
sy1_atom_003: generate_unit_tests_with_codex        # use Codex to write tests for each change
sy1_atom_004: run_tests_and_iterate                 # run tests; if failures, loop back to Claude
sy1_atom_005: commit_successful_changes             # commit once tests pass

# Workflow SY2 – Refactoring & Documentation
sy2_atom_000: refactor_code_with_claude             # perform structural refactoring
sy2_atom_001: add_docstrings_and_types_with_codex   # Codex adds docstrings/type hints
sy2_atom_002: run_tests_and_commit                  # test and commit changes after docs

# Workflow SY3 – Cross‑Language Tasks
sy3_atom_000: define_cross_language_goal            # describe backend + frontend feature
sy3_atom_001: implement_backend_with_claude         # Claude writes backend code
sy3_atom_002: implement_frontend_with_codex         # Codex produces JS/TS snippet
sy3_atom_003: integrate_and_test                    # combine both sides and test
sy3_atom_004: commit_final_implementation           # finalize after passing tests
________________________________________
Routing Engine (RT)
The IntelligentRouter evaluates tasks to select the most appropriate tool. Its atoms follow the decision flow.
rt_atom_000: check_git_clean_and_paths             # enforce hard constraints; else route to VS Code
rt_atom_001: compute_file_and_line_counts          # count files, lines and average sizes
rt_atom_002: assess_prompt_complexity              # measure complexity of the prompt
rt_atom_003: calculate_overall_complexity_score    # compute weighted complexity
rt_atom_004: evaluate_tool_candidates              # estimate cost/duration for each tool
rt_atom_005: select_tool_with_confidence           # choose the best tool and explain reasoning
________________________________________
Predetermined Workflow – PY_EDIT_V2 (PW)
This deterministic workflow always follows the same path based on file counts and sizes.
# Phase PW0 – Preparation
pw_atom_000: initialize_workflow_context           # record start state[1]
pw_atom_001: evaluate_git_and_file_constraints     # check git clean and allowed paths[2]

# Phase PW1 – Tool Selection
pw_atom_002: decide_between_aider_claude_vscode    # choose aider, claude or vscode based on size[3][4][5]

# Phase PW2 – Execution
pw_atom_003: run_selected_tool                     # execute predetermined CLI command[3][4]
pw_atom_004: perform_quality_checks                # run ruff, mypy and pytest[3][4]

# Phase PW3 – Finalization
pw_atom_005: commit_with_conventional_message      # commit changes with prefix[3][4]
pw_atom_006: push_changes_to_remote                # push to remote repository[3][4]
________________________________________
Workflow Enhancements (WH)
These atoms provide observability and logging features.
wh_atom_000: capture_pre_and_post_git_snapshots     # record branch, hash, commits and uncommitted files[6]
wh_atom_001: generate_run_identifier                # create run ID like yyyyMMdd-HHmmss-hex[7]
wh_atom_002: display_execution_banner               # show banner with workflow name and run ID[8]
wh_atom_003: produce_exit_summary                   # report duration, steps, tokens and git changes[9]
wh_atom_004: write_manifest_to_artifacts            # output manifest json with snapshots and stats[10]
wh_atom_005: log_activity_events                    # write structured logs to logs/workflow_execution.log[11]
wh_atom_006: rotate_logs_as_needed                  # perform log rotation beyond size limits[12]
________________________________________
Simplified Workflow Mode (SW)
This mode converts declarative operations into a lightweight execution plan.
sw_atom_000: enable_simplified_mode                 # set simplified: true or provide operations list[13]
sw_atom_001: map_operations_to_roles                # use RoleManager for 5-role mapping[13]
sw_atom_002: select_tool_via_simplified_router      # run SimplifiedRouter decision matrix[13]
sw_atom_003: estimate_tokens_with_costtracker       # log token usage estimates before execution[13]
sw_atom_004: execute_or_dry_run_operations          # convert operations to steps and run via adapters[14]
________________________________________
API Execution Workflows (AP)
Atoms here describe how to run workflows via the HTTP API.
ap_atom_000: post_workflow_execution_request        # send POST request with workflow_file, files, lane and tokens[15]
ap_atom_001: parse_execution_response               # extract execution_id, success, artifacts and metrics[16]
ap_atom_002: execute_dry_run                        # call API with dry_run: true for preview[17]
ap_atom_003: pass_custom_parameters                 # include analysis_depth, fix_suggestions, output_format etc.[18]
ap_atom_004: handle_large_codebase_parameters       # set max_tokens and exclude paths accordingly[19]
ap_atom_005: interpret_error_responses              # handle missing workflows, token overages and auth errors[20][21]
ap_atom_006: use_client_libraries                   # call API via Python or JavaScript SDKs[22][23]
ap_atom_007: monitor_execution_status               # query status, list executions and download artifacts[24]
________________________________________
Each atomic task encapsulates a single responsibility and can be composed into larger workflows or automated scripts. By separating workflows and enumerating their atoms, teams can implement, test and replace individual steps without impacting adjacent components.
________________________________________
[1] [2] [3] [4] [5] workflow-guide.md
https://github.com/DICKY1987/CLI_RESTART/blob/96d267ac92f1fc845dd1dc5614b49b387bbd4372/docs/workflow-guide.md
[6] [7] [8] [9] [10] [11] [12] workflow-enhancements.md
https://github.com/DICKY1987/CLI_RESTART/blob/96d267ac92f1fc845dd1dc5614b49b387bbd4372/docs/workflow-enhancements.md
[13] [14] simplified-workflow-guide.md
https://github.com/DICKY1987/CLI_RESTART/blob/96d267ac92f1fc845dd1dc5614b49b387bbd4372/docs/simplified-workflow-guide.md
[15] [16] [17] [18] [19] [20] [21] [22] [23] [24] workflow-execution.md
https://github.com/DICKY1987/CLI_RESTART/blob/96d267ac92f1fc845dd1dc5614b49b387bbd4372/docs/api/examples/workflow-execution.md
