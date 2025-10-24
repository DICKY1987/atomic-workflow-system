workflow:
  namespace: WIN
  name: GET-NEW-TOOL
  version: v1
  notes: |
    Two-ID mapping for the complete Tool Installation pipeline provided by the user.
    Conventions:
      - atom_key format: NS/WF/WFv/PH/LANE/SEQ
      - PH: P00..P18 aligned to phases 0..18
      - LANE: canonical lane per phase (see each phase header)
      - SEQ: preserved from the original legacy atom number (000..114)
      - legacy_id preserves the user's original atom_* identifier
      - atom_uid to be assigned by registry (ULID/UUIDv7)

phases:
  - phase: P00
    name: Pre-Installation Analysis
    lane: PLAN
    atoms:
      - atom_uid: <assign>
        atom_key: WIN/GET-NEW-TOOL/v1/P00/PLAN/000
        legacy_id: atom_000
        title: detect_host_os_and_architecture
      - atom_uid: <assign>
        atom_key: WIN/GET-NEW-TOOL/v1/P00/PLAN/001
        legacy_id: atom_001
        title: check_admin_elevated_privileges
      - atom_uid: <assign>
        atom_key: WIN/GET-NEW-TOOL/v1/P00/PLAN/002
        legacy_id: atom_002
        title: verify_internet_connectivity
      - atom_uid: <assign>
        atom_key: WIN/GET-NEW-TOOL/v1/P00/PLAN/003
        legacy_id: atom_003
        title: check_available_disk_space
      - atom_uid: <assign>
        atom_key: WIN/GET-NEW-TOOL/v1/P00/PLAN/004
        legacy_id: atom_004
        title: detect_existing_tool_installations
      - atom_uid: <assign>
        atom_key: WIN/GET-NEW-TOOL/v1/P00/PLAN/005
        legacy_id: atom_005
        title: snapshot_system_state
      - atom_uid: <assign>
        atom_key: WIN/GET-NEW-TOOL/v1/P00/PLAN/006
        legacy_id: atom_006
        title: initialize_installation_log

  - phase: P01
    name: Package Manager Discovery & Validation
    lane: DISCOVER
    atoms:
      - atom_uid: <assign>
        atom_key: WIN/GET-NEW-TOOL/v1/P01/DISCOVER/007
        legacy_id: atom_007
        title: enumerate_available_package_managers
      - atom_uid: <assign>
        atom_key: WIN/GET-NEW-TOOL/v1/P01/DISCOVER/008
        legacy_id: atom_008
        title: verify_package_manager_functionality
      - atom_uid: <assign>
        atom_key: WIN/GET-NEW-TOOL/v1/P01/DISCOVER/009
        legacy_id: atom_009
        title: update_package_manager_indices
      - atom_uid: <assign>
        atom_key: WIN/GET-NEW-TOOL/v1/P01/DISCOVER/010
        legacy_id: atom_010
        title: prioritize_package_managers_by_policy
      - atom_uid: <assign>
        atom_key: WIN/GET-NEW-TOOL/v1/P01/DISCOVER/011
        legacy_id: atom_011
        title: check_package_manager_cache_health
      - atom_uid: <assign>
        atom_key: WIN/GET-NEW-TOOL/v1/P01/DISCOVER/012
        legacy_id: atom_012
        title: validate_package_manager_config

  - phase: P02
    name: Tool Specification & Resolution
    lane: RESOLVE
    atoms:
      - atom_uid: <assign>
        atom_key: WIN/GET-NEW-TOOL/v1/P02/RESOLVE/013
        legacy_id: atom_013
        title: parse_tool_installation_request
      - atom_uid: <assign>
        atom_key: WIN/GET-NEW-TOOL/v1/P02/RESOLVE/014
        legacy_id: atom_014
        title: normalize_tool_identifiers
      - atom_uid: <assign>
        atom_key: WIN/GET-NEW-TOOL/v1/P02/RESOLVE/015
        legacy_id: atom_015
        title: resolve_tool_version_requirements
      - atom_uid: <assign>
        atom_key: WIN/GET-NEW-TOOL/v1/P02/RESOLVE/016
        legacy_id: atom_016
        title: search_tool_in_package_repositories
      - atom_uid: <assign>
        atom_key: WIN/GET-NEW-TOOL/v1/P02/RESOLVE/017
        legacy_id: atom_017
        title: validate_tool_availability
      - atom_uid: <assign>
        atom_key: WIN/GET-NEW-TOOL/v1/P02/RESOLVE/018
        legacy_id: atom_018
        title: identify_tool_dependencies
      - atom_uid: <assign>
        atom_key: WIN/GET-NEW-TOOL/v1/P02/RESOLVE/019
        legacy_id: atom_019
        title: check_dependency_conflicts
      - atom_uid: <assign>
        atom_key: WIN/GET-NEW-TOOL/v1/P02/RESOLVE/020
        legacy_id: atom_020
        title: determine_installation_method

  - phase: P03
    name: Pre-Installation Checks
    lane: SAFETY
    atoms:
      - atom_uid: <assign>
        atom_key: WIN/GET-NEW-TOOL/v1/P03/SAFETY/021
        legacy_id: atom_021
        title: verify_tool_not_already_installed
      - atom_uid: <assign>
        atom_key: WIN/GET-NEW-TOOL/v1/P03/SAFETY/022
        legacy_id: atom_022
        title: check_conflicting_tool_versions
      - atom_uid: <assign>
        atom_key: WIN/GET-NEW-TOOL/v1/P03/SAFETY/023
        legacy_id: atom_023
        title: validate_installation_location
      - atom_uid: <assign>
        atom_key: WIN/GET-NEW-TOOL/v1/P03/SAFETY/024
        legacy_id: atom_024
        title: verify_tool_signature_and_checksum
      - atom_uid: <assign>
        atom_key: WIN/GET-NEW-TOOL/v1/P03/SAFETY/025
        legacy_id: atom_025
        title: scan_tool_for_security_issues
      - atom_uid: <assign>
        atom_key: WIN/GET-NEW-TOOL/v1/P03/SAFETY/026
        legacy_id: atom_026
        title: check_license_compatibility
      - atom_uid: <assign>
        atom_key: WIN/GET-NEW-TOOL/v1/P03/SAFETY/027
        legacy_id: atom_027
        title: create_installation_rollback_point

  - phase: P04
    name: Dependency Installation
    lane: DEPS
    atoms:
      - atom_uid: <assign>
        atom_key: WIN/GET-NEW-TOOL/v1/P04/DEPS/028
        legacy_id: atom_028
        title: enumerate_missing_dependencies
      - atom_uid: <assign>
        atom_key: WIN/GET-NEW-TOOL/v1/P04/DEPS/029
        legacy_id: atom_029
        title: sort_dependencies_topologically
      - atom_uid: <assign>
        atom_key: WIN/GET-NEW-TOOL/v1/P04/DEPS/030
        legacy_id: atom_030
        title: install_dependency_via_package_manager
      - atom_uid: <assign>
        atom_key: WIN/GET-NEW-TOOL/v1/P04/DEPS/031
        legacy_id: atom_031
        title: verify_dependency_installation
      - atom_uid: <assign>
        atom_key: WIN/GET-NEW-TOOL/v1/P04/DEPS/032
        legacy_id: atom_032
        title: configure_dependency_environment_vars
      - atom_uid: <assign>
        atom_key: WIN/GET-NEW-TOOL/v1/P04/DEPS/033
        legacy_id: atom_033
        title: update_shared_library_caches

  - phase: P05
    name: Primary Tool Installation
    lane: APPLY
    atoms:
      - atom_uid: <assign>
        atom_key: WIN/GET-NEW-TOOL/v1/P05/APPLY/034
        legacy_id: atom_034
        title: download_tool_package
      - atom_uid: <assign>
        atom_key: WIN/GET-NEW-TOOL/v1/P05/APPLY/035
        legacy_id: atom_035
        title: verify_download_integrity
      - atom_uid: <assign>
        atom_key: WIN/GET-NEW-TOOL/v1/P05/APPLY/036
        legacy_id: atom_036
        title: extract_package_if_archived
      - atom_uid: <assign>
        atom_key: WIN/GET-NEW-TOOL/v1/P05/APPLY/037
        legacy_id: atom_037
        title: execute_package_manager_install
      - atom_uid: <assign>
        atom_key: WIN/GET-NEW-TOOL/v1/P05/APPLY/038
        legacy_id: atom_038
        title: capture_installation_output
      - atom_uid: <assign>
        atom_key: WIN/GET-NEW-TOOL/v1/P05/APPLY/039
        legacy_id: atom_039
        title: monitor_installation_progress
      - atom_uid: <assign>
        atom_key: WIN/GET-NEW-TOOL/v1/P05/APPLY/040
        legacy_id: atom_040
        title: handle_installation_prompts
      - atom_uid: <assign>
        atom_key: WIN/GET-NEW-TOOL/v1/P05/APPLY/041
        legacy_id: atom_041
        title: wait_for_installation_completion
      - atom_uid: <assign>
        atom_key: WIN/GET-NEW-TOOL/v1/P05/APPLY/042
        legacy_id: atom_042
        title: verify_installation_exit_code

  - phase: P06
    name: Post-Installation Verification
    lane: VALIDATE
    atoms:
      - atom_uid: <assign>
        atom_key: WIN/GET-NEW-TOOL/v1/P06/VALIDATE/043
        legacy_id: atom_043
        title: verify_tool_executable_exists
      - atom_uid: <assign>
        atom_key: WIN/GET-NEW-TOOL/v1/P06/VALIDATE/044
        legacy_id: atom_044
        title: verify_tool_in_system_path
      - atom_uid: <assign>
        atom_key: WIN/GET-NEW-TOOL/v1/P06/VALIDATE/045
        legacy_id: atom_045
        title: run_tool_version_check
      - atom_uid: <assign>
        atom_key: WIN/GET-NEW-TOOL/v1/P06/VALIDATE/046
        legacy_id: atom_046
        title: execute_tool_smoke_test
      - atom_uid: <assign>
        atom_key: WIN/GET-NEW-TOOL/v1/P06/VALIDATE/047
        legacy_id: atom_047
        title: verify_tool_permissions
      - atom_uid: <assign>
        atom_key: WIN/GET-NEW-TOOL/v1/P06/VALIDATE/048
        legacy_id: atom_048
        title: check_tool_runtime_dependencies
      - atom_uid: <assign>
        atom_key: WIN/GET-NEW-TOOL/v1/P06/VALIDATE/049
        legacy_id: atom_049
        title: validate_tool_configuration_files

  - phase: P07
    name: Environment Integration
    lane: ENV
    atoms:
      - atom_uid: <assign>
        atom_key: WIN/GET-NEW-TOOL/v1/P07/ENV/050
        legacy_id: atom_050
        title: add_tool_to_path_if_needed
      - atom_uid: <assign>
        atom_key: WIN/GET-NEW-TOOL/v1/P07/ENV/051
        legacy_id: atom_051
        title: create_symbolic_links_if_needed
      - atom_uid: <assign>
        atom_key: WIN/GET-NEW-TOOL/v1/P07/ENV/052
        legacy_id: atom_052
        title: register_tool_shell_completions
      - atom_uid: <assign>
        atom_key: WIN/GET-NEW-TOOL/v1/P07/ENV/053
        legacy_id: atom_053
        title: update_environment_variable_registry
      - atom_uid: <assign>
        atom_key: WIN/GET-NEW-TOOL/v1/P07/ENV/054
        legacy_id: atom_054
        title: reload_shell_environment
      - atom_uid: <assign>
        atom_key: WIN/GET-NEW-TOOL/v1/P07/ENV/055
        legacy_id: atom_055
        title: verify_tool_accessible_globally

  - phase: P08
    name: Tool Configuration
    lane: CONFIG
    atoms:
      - atom_uid: <assign>
        atom_key: WIN/GET-NEW-TOOL/v1/P08/CONFIG/056
        legacy_id: atom_056
        title: create_tool_config_directory
      - atom_uid: <assign>
        atom_key: WIN/GET-NEW-TOOL/v1/P08/CONFIG/057
        legacy_id: atom_057
        title: generate_default_config_file
      - atom_uid: <assign>
        atom_key: WIN/GET-NEW-TOOL/v1/P08/CONFIG/058
        legacy_id: atom_058
        title: apply_project_specific_settings
      - atom_uid: <assign>
        atom_key: WIN/GET-NEW-TOOL/v1/P08/CONFIG/059
        legacy_id: atom_059
        title: configure_tool_data_directories
      - atom_uid: <assign>
        atom_key: WIN/GET-NEW-TOOL/v1/P08/CONFIG/060
        legacy_id: atom_060
        title: set_tool_permissions_and_ownership
      - atom_uid: <assign>
        atom_key: WIN/GET-NEW-TOOL/v1/P08/CONFIG/061
        legacy_id: atom_061
        title: integrate_with_existing_toolchain

  - phase: P09
    name: Documentation & Registration
    lane: RECORD
    atoms:
      - atom_uid: <assign>
        atom_key: WIN/GET-NEW-TOOL/v1/P09/RECORD/062
        legacy_id: atom_062
        title: record_installed_tool_metadata
      - atom_uid: <assign>
        atom_key: WIN/GET-NEW-TOOL/v1/P09/RECORD/063
        legacy_id: atom_063
        title: update_tool_inventory_manifest
      - atom_uid: <assign>
        atom_key: WIN/GET-NEW-TOOL/v1/P09/RECORD/064
        legacy_id: atom_064
        title: generate_tool_installation_report
      - atom_uid: <assign>
        atom_key: WIN/GET-NEW-TOOL/v1/P09/RECORD/065
        legacy_id: atom_065
        title: document_installation_commands_used
      - atom_uid: <assign>
        atom_key: WIN/GET-NEW-TOOL/v1/P09/RECORD/066
        legacy_id: atom_066
        title: create_tool_usage_quickstart_guide
      - atom_uid: <assign>
        atom_key: WIN/GET-NEW-TOOL/v1/P09/RECORD/067
        legacy_id: atom_067
        title: link_tool_documentation

  - phase: P10
    name: Validation & Testing
    lane: TEST
    atoms:
      - atom_uid: <assign>
        atom_key: WIN/GET-NEW-TOOL/v1/P10/TEST/068
        legacy_id: atom_068
        title: run_tool_comprehensive_health_check
      - atom_uid: <assign>
        atom_key: WIN/GET-NEW-TOOL/v1/P10/TEST/069
        legacy_id: atom_069
        title: test_tool_with_sample_workload
      - atom_uid: <assign>
        atom_key: WIN/GET-NEW-TOOL/v1/P10/TEST/070
        legacy_id: atom_070
        title: verify_tool_performance_baseline
      - atom_uid: <assign>
        atom_key: WIN/GET-NEW-TOOL/v1/P10/TEST/071
        legacy_id: atom_071
        title: test_tool_error_handling
      - atom_uid: <assign>
        atom_key: WIN/GET-NEW-TOOL/v1/P10/TEST/072
        legacy_id: atom_072
        title: validate_tool_logging_functionality
      - atom_uid: <assign>
        atom_key: WIN/GET-NEW-TOOL/v1/P10/TEST/073
        legacy_id: atom_073
        title: check_tool_update_mechanism

  - phase: P11
    name: Integration Testing
    lane: INTEGRATE
    atoms:
      - atom_uid: <assign>
        atom_key: WIN/GET-NEW-TOOL/v1/P11/INTEGRATE/074
        legacy_id: atom_074
        title: test_tool_with_existing_projects
      - atom_uid: <assign>
        atom_key: WIN/GET-NEW-TOOL/v1/P11/INTEGRATE/075
        legacy_id: atom_075
        title: verify_tool_api_compatibility
      - atom_uid: <assign>
        atom_key: WIN/GET-NEW-TOOL/v1/P11/INTEGRATE/076
        legacy_id: atom_076
        title: test_tool_cli_interface_stability
      - atom_uid: <assign>
        atom_key: WIN/GET-NEW-TOOL/v1/P11/INTEGRATE/077
        legacy_id: atom_077
        title: validate_tool_plugin_ecosystem
      - atom_uid: <assign>
        atom_key: WIN/GET-NEW-TOOL/v1/P11/INTEGRATE/078
        legacy_id: atom_078
        title: test_tool_with_ci_cd_pipelines

  - phase: P12
    name: Rollback Preparation
    lane: ROLLBACK
    atoms:
      - atom_uid: <assign>
        atom_key: WIN/GET-NEW-TOOL/v1/P12/ROLLBACK/079
        legacy_id: atom_079
        title: document_rollback_procedure
      - atom_uid: <assign>
        atom_key: WIN/GET-NEW-TOOL/v1/P12/ROLLBACK/080
        legacy_id: atom_080
        title: create_uninstall_script
      - atom_uid: <assign>
        atom_key: WIN/GET-NEW-TOOL/v1/P12/ROLLBACK/081
        legacy_id: atom_081
        title: backup_previous_tool_version
      - atom_uid: <assign>
        atom_key: WIN/GET-NEW-TOOL/v1/P12/ROLLBACK/082
        legacy_id: atom_082
        title: mark_installation_as_reversible

  - phase: P13
    name: Observability & Monitoring
    lane: OBSERVE
    atoms:
      - atom_uid: <assign>
        atom_key: WIN/GET-NEW-TOOL/v1/P13/OBSERVE/083
        legacy_id: atom_083
        title: register_tool_in_monitoring_system
      - atom_uid: <assign>
        atom_key: WIN/GET-NEW-TOOL/v1/P13/OBSERVE/084
        legacy_id: atom_084
        title: configure_tool_telemetry_settings
      - atom_uid: <assign>
        atom_key: WIN/GET-NEW-TOOL/v1/P13/OBSERVE/085
        legacy_id: atom_085
        title: set_up_tool_update_notifications
      - atom_uid: <assign>
        atom_key: WIN/GET-NEW-TOOL/v1/P13/OBSERVE/086
        legacy_id: atom_086
        title: track_tool_usage_metrics

  - phase: P14
    name: Post-Installation Cleanup
    lane: CLEANUP
    atoms:
      - atom_uid: <assign>
        atom_key: WIN/GET-NEW-TOOL/v1/P14/CLEANUP/087
        legacy_id: atom_087
        title: remove_installation_temporary_files
      - atom_uid: <assign>
        atom_key: WIN/GET-NEW-TOOL/v1/P14/CLEANUP/088
        legacy_id: atom_088
        title: clear_package_manager_cache
      - atom_uid: <assign>
        atom_key: WIN/GET-NEW-TOOL/v1/P14/CLEANUP/089
        legacy_id: atom_089
        title: remove_installation_logs_if_successful
      - atom_uid: <assign>
        atom_key: WIN/GET-NEW-TOOL/v1/P14/CLEANUP/090
        legacy_id: atom_090
        title: finalize_installation_status

  - phase: P15
    name: Cross-Cutting — Error Handling & Recovery
    lane: ERR
    atoms:
      - atom_uid: <assign>
        atom_key: WIN/GET-NEW-TOOL/v1/P15/ERR/091
        legacy_id: atom_091
        title: detect_installation_failure_type
      - atom_uid: <assign>
        atom_key: WIN/GET-NEW-TOOL/v1/P15/ERR/092
        legacy_id: atom_092
        title: classify_error_as_transient_or_permanent
      - atom_uid: <assign>
        atom_key: WIN/GET-NEW-TOOL/v1/P15/ERR/093
        legacy_id: atom_093
        title: execute_automatic_rollback_on_failure
      - atom_uid: <assign>
        atom_key: WIN/GET-NEW-TOOL/v1/P15/ERR/094
        legacy_id: atom_094
        title: log_detailed_error_diagnostics
      - atom_uid: <assign>
        atom_key: WIN/GET-NEW-TOOL/v1/P15/ERR/095
        legacy_id: atom_095
        title: suggest_alternative_installation_methods
      - atom_uid: <assign>
        atom_key: WIN/GET-NEW-TOOL/v1/P15/ERR/096
        legacy_id: atom_096
        title: escalate_to_manual_intervention

  - phase: P16
    name: Cross-Cutting — Multi-Tool Orchestration
    lane: ORCH
    atoms:
      - atom_uid: <assign>
        atom_key: WIN/GET-NEW-TOOL/v1/P16/ORCH/097
        legacy_id: atom_097
        title: process_tool_installation_batch
      - atom_uid: <assign>
        atom_key: WIN/GET-NEW-TOOL/v1/P16/ORCH/098
        legacy_id: atom_098
        title: handle_inter_tool_dependencies
      - atom_uid: <assign>
        atom_key: WIN/GET-NEW-TOOL/v1/P16/ORCH/099
        legacy_id: atom_099
        title: parallelize_independent_installations
      - atom_uid: <assign>
        atom_key: WIN/GET-NEW-TOOL/v1/P16/ORCH/100
        legacy_id: atom_100
        title: coordinate_shared_dependency_installs

  - phase: P17
    name: Tool Update & Upgrade Path
    lane: UPDATE
    atoms:
      - atom_uid: <assign>
        atom_key: WIN/GET-NEW-TOOL/v1/P17/UPDATE/101
        legacy_id: atom_101
        title: check_for_tool_updates
      - atom_uid: <assign>
        atom_key: WIN/GET-NEW-TOOL/v1/P17/UPDATE/102
        legacy_id: atom_102
        title: compare_installed_vs_available_versions
      - atom_uid: <assign>
        atom_key: WIN/GET-NEW-TOOL/v1/P17/UPDATE/103
        legacy_id: atom_103
        title: download_updated_tool_package
      - atom_uid: <assign>
        atom_key: WIN/GET-NEW-TOOL/v1/P17/UPDATE/104
        legacy_id: atom_104
        title: execute_in_place_upgrade
      - atom_uid: <assign>
        atom_key: WIN/GET-NEW-TOOL/v1/P17/UPDATE/105
        legacy_id: atom_105
        title: verify_upgrade_success
      - atom_uid: <assign>
        atom_key: WIN/GET-NEW-TOOL/v1/P17/UPDATE/106
        legacy_id: atom_106
        title: rollback_failed_upgrade

  - phase: P18
    name: Definition of Done
    lane: CLOSEOUT
    atoms:
      - atom_uid: <assign>
        atom_key: WIN/GET-NEW-TOOL/v1/P18/CLOSEOUT/107
        legacy_id: atom_107
        title: tool_executable_in_path_and_working
      - atom_uid: <assign>
        atom_key: WIN/GET-NEW-TOOL/v1/P18/CLOSEOUT/108
        legacy_id: atom_108
        title: tool_version_matches_requirement
      - atom_uid: <assign>
        atom_key: WIN/GET-NEW-TOOL/v1/P18/CLOSEOUT/109
        legacy_id: atom_109
        title: tool_dependencies_satisfied
      - atom_uid: <assign>
        atom_key: WIN/GET-NEW-TOOL/v1/P18/CLOSEOUT/110
        legacy_id: atom_110
        title: tool_configuration_valid
      - atom_uid: <assign>
        atom_key: WIN/GET-NEW-TOOL/v1/P18/CLOSEOUT/111
        legacy_id: atom_111
        title: tool_documented_in_manifest
      - atom_uid: <assign>
        atom_key: WIN/GET-NEW-TOOL/v1/P18/CLOSEOUT/112
        legacy_id: atom_112
        title: installation_logs_archived
      - atom_uid: <assign>
        atom_key: WIN/GET-NEW-TOOL/v1/P18/CLOSEOUT/113
        legacy_id: atom_113
        title: tool_integrated_with_environment
      - atom_uid: <assign>
        atom_key: WIN/GET-NEW-TOOL/v1/P18/CLOSEOUT/114
        legacy_id: atom_114
        title: rollback_procedure_documented

