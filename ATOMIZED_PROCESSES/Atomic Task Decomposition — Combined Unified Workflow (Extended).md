Atomic Task Decomposition — Combined Unified Workflow (Extended)
This document extends the earlier atomic decomposition to include additional tasks introduced by the Simultaneous Execution with Git Worktrees workflow. The original unified pipeline (from COMBINED.nested.yaml, COMBINED.deepmerge.yaml and COMBINED.multi.yaml) defined atoms up through atom_129. New atoms begin at atom_130 and correspond to multi‑stream creation, parallel execution with priority queues, merge coordination and Git worktree isolation. Each atom retains the single‑responsibility principle and is assigned to a role that best reflects ownership of the operation.
Carry‑forward Atoms (1‒129)
For completeness the atoms from the existing unified workflow are preserved in prior files. Atoms 1‒129 are defined in atomic_decomposition_combined_updated.md and are unchanged here.
Simultaneous Execution & Git Worktree Workflow
These atoms represent the lifecycle of simultaneous work‑stream execution, parallel dispatch, merge queue management and final verification. They are derived from the Simultaneous execution with get work trees.md description, which outlines how workstreams are created, queued, executed in parallel via a priority queue, merged and persisted. Each step is decomposed into atomic operations with a single responsible role.
atom_130: Work Stream Creation: analyze_file_scope_requirements | Role: planning_ai
atom_131: Work Stream Creation: identify_non_conflicting_streams | Role: planning_ai
atom_132: Work Stream Creation: create_workstream_record | Role: orchestrator
atom_133: Work Stream Creation: assign_stream_priorities | Role: orchestrator
atom_134: Work Stream Creation: configure_multistream_definitions | Role: orchestrator
atom_135: Execution Planning: define_execution_order | Role: orchestrator
atom_136: Execution Planning: manage_path_claims | Role: merge_coordinator
atom_137: Execution Planning: allocate_git_worktrees | Role: repo_ai
atom_138: Execution Planning: manage_dependencies | Role: planning_ai
atom_139: Work Stream Execution: list_available_streams | Role: orchestrator
atom_140: Work Stream Execution: queue_workstream_priority | Role: orchestrator
atom_141: Work Stream Execution: dispatch_parallel_execution | Role: orchestrator
atom_142: Work Stream Execution: spawn_worker_threads | Role: orchestrator
atom_143: Work Stream Execution: execute_stream | Role: orchestrator
atom_144: Work Stream Execution: retrieve_phases_for_stream | Role: orchestrator
atom_145: Work Stream Execution: execute_phase | Role: orchestrator
atom_146: Work Stream Execution: track_phase_completion | Role: orchestrator
atom_147: Work Stream Execution: update_workstream_status | Role: orchestrator
atom_148: Work Stream Execution: save_artifacts_to_directory | Role: orchestrator
atom_149: Work Stream Execution: create_merge_queue_item | Role: merge_coordinator
atom_150: Merge Queue: pre_merge_lint_check | Role: qa_test_agent
atom_151: Merge Queue: pre_merge_test_check | Role: qa_test_agent
atom_152: Merge Queue: pre_merge_security_check | Role: security_compliance
atom_153: Merge Queue: estimate_wait_time | Role: merge_coordinator
atom_154: Merge Queue: detect_conflicts | Role: merge_coordinator
atom_155: Merge Queue: merge_branches | Role: merge_coordinator
atom_156: Merge Queue: update_merge_status | Role: merge_coordinator
atom_157: Persistence: update_state_files | Role: orchestrator
atom_158: Persistence: update_merge_queue_state_file | Role: merge_coordinator
atom_159: Monitoring: display_real_time_status | Role: orchestrator
atom_160: Monitoring: perform_health_check | Role: qa_test_agent
atom_161: IPT Verification: verify_execution_results | Role: planning_ai
atom_162: Work Stream Cleanup: finalize_and_cleanup | Role: orchestrator
Notes on Roles and Responsibilities
•	planning_ai handles the initial analysis: understanding file scopes, identifying work stream boundaries, ensuring dependencies are respected and verifying results at the end of execution. These tasks require reasoning over the project structure and planning concurrency.
•	orchestrator manages most of the operational flow. It creates workstream records in the database, assigns priorities, reads multi‑stream definitions, determines execution order, lists streams, enqueues and dispatches work streams, spawns workers, executes phases, tracks completion and updates persistent state files. Orchestrator also displays real‑time status to users.
•	merge_coordinator focuses on merge‑specific concerns: creating items in the merge queue, performing pre‑merge checks (with help from QA and security roles), estimating wait times, detecting conflicts, merging branches and updating merge statuses. It also maintains the merge queue state file and manages exclusive path claims to avoid concurrency issues.
•	repo_ai is responsible for Git‑related operations such as allocating isolated worktrees for each stream.
•	qa_test_agent runs linting and test checks both in the work streams and during the merge queue pre‑merge phase, and performs periodic health checks on the project structure.
•	security_compliance conducts pre‑merge security reviews as part of the merge queue.
This extended atom list ensures that the simultaneous execution workflow is explicitly represented in the unified atomic pipeline, enabling deterministic scheduling, clear role assignment and reliable parallel development across isolated worktrees.
________________________________________
