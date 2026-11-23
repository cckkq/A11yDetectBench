# Artifact Manifest


## Executable Asset Counts

| Family | Task family | Task bundles |
| --- | --- | ---: |
| Links | selected_issue | 153 |
| Links | no_issue | 51 |
| Links | issue_list | 78 |
| Keyboard | selected_issue | 84 |
| Keyboard | no_issue | 28 |
| Keyboard | issue_list | 50 |
| Errors/status | selected_issue | 78 |
| Errors/status | no_issue | 26 |
| Errors/status | issue_list | 46 |
| Focus | selected_issue | 48 |
| Focus | no_issue | 16 |
| Focus | issue_list | 28 |

Total task YAML files: 686  
Total prompt TXT files: 686  
Total evaluate-rule YAML files: 686  
Sanitized construction-source markdown files under `source_md_clean`: 494  
Errors/status issue templates under `agent/gt_errors/issue-templates`: 14

## Batch manifests

Each family’s `experiments/` directory contains an index for selected issues, clean L1 controls and L2/L3 issue lists. The [protocol](docs/EXPERIMENT_CONFIG.md#batch-manifests) identifies the ten recovered or submitted manifests and the two issue-list indexes prepared for this release. Focus, Keyboard and Errors/status each include the original per-instance settings in `runtime_patches/pass_l1_counterfactual.yaml`.

## Runner and Construction Code Included

- Family runners: `run_task.py`, `run_experiment_parallel.py`, `evaluate_run.py`, `experiment_manifest.py`, and `parallel_runner.py` for each family.
- Shared runner utilities: `agent/gt/evaluation_runner.py`, `agent/gt/evaluation_gate.py`, `agent/gt/parallel_runner.py`, `agent/gt/path_utils.py`, `agent/gt/probe_auth.py`, and the public sign-in adapter `agent/gt/save_storage_state.py`. The public model adapter is `agent/llm_setup.py`. These two adapters use environment variables in place of the original institutional setup.
- Construction scripts: family `generate_clean_assets.py`, `generate_pass_assets.py` where present, `generate_merge_assets.py`, plus Links `links_gt_manifest.py` and its sanitized clean manifest.
- Page-evidence diagnostic scanners: `agent/evidence_baseline/run_candidates.py`, `focus_collector.py`, `keyboard_collector.py`, `candidates.py`, `offline_eval.py`, `focus_vlm.py`, and `overlay.py`.
- Third-party runtime patch metadata: `third_party/browser-use-0.12.6-structured-output.patch` for the browser-use 0.12.6 structured-output robustness patch.
- Supplementary diagnostic note: `docs/SUPPLEMENTARY_BROWSER_ACCESS_DIAGNOSTIC.md` records the Keyboard-only Codex+CLI browser-access diagnostic table.
- Representative evaluation cases: `docs/CONSTRUCTION_PIPELINE.md` contains four sanitized end-to-end case chains covering a selected-issue hit, a repaired no-issue control, a target-localization failure, and a missing-interaction-evidence failure.
- Original evaluator and evidence utility tests are in `tests/`. Keyboard includes its optional visual evaluator helper.
- The archived [Focus adjudication rule and group counts](docs/focus-table3-reference.json) preserve the distinction between automatic scores and the manual adjustments used for Table III.

The project archives the original annotation sheets and full run traces separately.
