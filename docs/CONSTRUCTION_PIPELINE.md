# Construction Pipeline

The submitted benchmark snapshot is built from sanitized template and instance sources into executable task, prompt, and evaluator-rule bundles.

## Asset Layers

1. `source_md_clean`: human-readable sanitized issue templates, representative instances, pass instances, and issue-list merge instances.
2. Generation scripts: family-specific scripts convert the source layer into YAML task files, prompt previews, and evaluator-rule files.
3. `generated_clean_pilot`: historical directory name for the submitted generated snapshot. The files under this directory are the benchmark assets counted in the paper snapshot.
4. `experiments`: formal manifests select the task sets and repeat counts used by the experiments.

## Family Pipelines

| Family | Source inputs | Generation scripts | Formal outputs |
| --- | --- | --- | --- |
| Links | 30 templates, 51 issue instances, 51 formal L1 pass instances, 42 L2 merge instances, 36 L3 merge instances | `generate_clean_assets.py`, `generate_merge_assets.py`, `links_gt_manifest.py`; the included L1 pass assets are the 51-task formal subset selected by `links_pass_l1_v1.yaml` | 282 task bundles |
| Keyboard | 12 templates, 28 issue instances, 28 pass instances, 27 L2 merge instances, 23 L3 merge instances | `generate_clean_assets.py`, `generate_pass_assets.py`, `generate_merge_assets.py` | 162 task bundles |
| Errors/status | 14 templates, 26 issue instances, 26 pass instances, 25 L2 merge instances, 21 L3 merge instances | `generate_clean_assets.py`, `generate_pass_assets.py`, `generate_merge_assets.py` | 150 task bundles |
| Focus | 8 templates, 16 issue instances, 16 pass instances, 14 L2 merge instances, 14 L3 merge instances | `generate_clean_assets.py`, `generate_pass_assets.py`, `generate_merge_assets.py` | 92 task bundles |

## Deliberate Exclusions

The artifact excludes raw review records, local notes, old Links generation scripts, pilot compiler folders, draft pass/page-assessment assets outside the formal manifests, review-agent workspaces, temporary scripts, retry manifests, and run outputs. Those files either contain local/private context or are not part of the submitted 686-task benchmark snapshot.

## Representative End-to-End Evaluation Cases

The following sanitized cases make the mapping from task definition to structured report and evaluator result directly checkable. They are representative examples; raw browser traces, authentication state, machine paths, and credentials remain excluded.

### GL28 selected-issue L1: positive structured match

Asset chain:

- Source instance: `agent/gt_keyboard/source_md_clean/issue-instances/gitlab.gl28.filtered_search_token_not_tabbable.md`
- Task: `agent/gt_keyboard/generated_clean_pilot/generated/tasks/gitlab.gl28.filtered_search_token_not_tabbable.verify.v1.yaml`
- Prompt: `agent/gt_keyboard/generated_clean_pilot/generated/prompts/gitlab.gl28.filtered_search_token_not_tabbable.verify.v1.task.prompt.txt`
- Rule: `agent/gt_keyboard/generated_clean_pilot/generated/evaluate-rules/gitlab.gl28.filtered_search_token_not_tabbable.verify.shared.v1.yaml`

The sanitized agent report was `verdict=issue_found`, selector `.filtered-search-token.search-token-assignee`, and issue type `keyboard_nonreachable`. The evaluator resolved the reported selector to the gold DOM target and returned `verdict_match=true`, `selector_match=true`, `issue_type_match=true`, `overall_pass=true`, with no extra findings and no evaluator error.

```json
{"verdict":"issue_found","selector":".filtered-search-token.search-token-assignee","target":"Assignee equals Byte Blaze filtered-search token","issue_type":"keyboard_nonreachable","observed_behavior":"Keyboard navigation skips the assignee token and its remove control.","evidence":"Tab reaches surrounding controls and the filtered-search input, but activeElement never enters the token or its remove button."}
```

Evaluator summary: `expected_verdict=issue_found`, `observed_verdict=issue_found`, `matched_count=1`, `extra_issues=[]`, `overall_pass=true`, `evaluator_error=false`.

### GL28 PASS L1: matched no-issue control

Asset chain:

- Source instance: `agent/gt_keyboard/source_md_clean/pass-instances/gitlab.gl28.filtered_search_token_not_tabbable.md`
- Task: `agent/gt_keyboard/generated_clean_pilot/generated_pass/tasks/gitlab.gl28.filtered_search_token_not_tabbable.verify.v1.yaml`
- Prompt: `agent/gt_keyboard/generated_clean_pilot/generated_pass/prompts/gitlab.gl28.filtered_search_token_not_tabbable.verify.v1.task.prompt.txt`
- Rule: `agent/gt_keyboard/generated_clean_pilot/generated_pass/evaluate-rules/gitlab.gl28.filtered_search_token_not_tabbable.verify.shared.v1.yaml`

This is a counterfactual repair of the same page, target selector, and criterion. The runtime repair specification is `gitlab_filtered_search_token_keyboard_repair`; its postcondition is that the matched token and its keyboard controls are reachable and operable while the page, selector, and WCAG criterion remain unchanged. The sanitized report returned `verdict=no_issue_found` with an empty issue list. The evaluator returned `expected_verdict=no_issue_found`, `observed_verdict=no_issue_found`, `issue_count=0`, `overall_pass=true`, and `evaluator_error=false`. The repair condition therefore changes only the reviewed target state; it does not create a new target or change the criterion.

```json
{"verdict":"no_issue_found","selector":".filtered-search-token.search-token-assignee","target":"Assignee equals Byte Blaze filtered-search token on the merged merge requests dashboard","issue_type":"keyboard_nonreachable","observed_behavior":"The repaired token is reachable and operable with keyboard navigation.","evidence":"Tab reaches the token; Enter opens it for editing and Shift+Tab reaches its controls."}
```

Evaluator summary: `expected_verdict=no_issue_found`, `observed_verdict=no_issue_found`, `issue_count=0`, `overall_pass=true`, `evaluator_error=false`.

### PA75 Focus L3: target-localization failure

Asset chain:

- Source merge instance: `agent/gt_focus/source_md_clean/merge-instances/level3/shopping_admin.pa75.focus_assessment.md`
- Task: `agent/gt_focus/generated_clean_pilot/generated_merge/tasks/shopping_admin.pa75.focus_assessment.verify.level3.v1.yaml`
- Prompt: `agent/gt_focus/generated_clean_pilot/generated_merge/prompts/shopping_admin.pa75.focus_assessment.verify.level3.v1.task.prompt.txt`
- Rule: `agent/gt_focus/generated_clean_pilot/generated_merge/evaluate-rules/shopping_admin.pa75.focus_assessment.verify.level3.v1.yaml`

The gold target is the row-level Edit/Delete button group. The sanitized report instead named a left-navigation link and a System Messages button. Both reports used the correct `visible_focus` family, but neither resolved to the gold target. The evaluator returned `expected_count=1`, `reported_count=2`, `matched_count=0`, `recall=0`, `precision=0`, `extra_issues=[0,1]`, `overall_pass=false`, and `evaluator_error=false`.

```json
{"verdict":"issue_found","issues":[{"selector":"li#menu-magento-marketplace-partners > a","target":"Find Partners & Extensions left-navigation link","issue_type":"visible_focus","observed_behavior":"No visible focus indicator.","evidence":"Focused state had outlineStyle=none and boxShadow=none."},{"selector":"button.message-system-action-dropdown","target":"System Messages: 2 button","issue_type":"visible_focus","observed_behavior":"Focus indicator disappears after activation.","evidence":"The button remained active but its focus ring became none after Enter."}]}
```

Evaluator summary: `expected_elements=2`, `reported_elements=2`, `matched_elements=0`, `recall=0`, `precision=0`, `extra_issues=[0,1]`, `overall_pass=false`, `evaluator_error=false`.

### GL01 Focus L1: missing interaction evidence

Asset chain:

- Source instance: `agent/gt_focus/source_md_clean/issue-instances/gitlab.gl01.f21t4.explore_tab_controls_no_visible_focus.md`
- Task: `agent/gt_focus/generated_clean_pilot/generated/tasks/gitlab.gl01.f21t4.explore_tab_controls_no_visible_focus.verify.v1.yaml`
- Prompt: `agent/gt_focus/generated_clean_pilot/generated/prompts/gitlab.gl01.f21t4.explore_tab_controls_no_visible_focus.verify.v1.task.prompt.txt`
- Rule: `agent/gt_focus/generated_clean_pilot/generated/evaluate-rules/gitlab.gl01.f21t4.explore_tab_controls_no_visible_focus.verify.shared.v1.yaml`

The report returned `no_issue_found` after repeatedly failing to confirm focus on the requested “Yours” tab. The rule expected `issue_found`; selector resolution itself succeeded, but the verdict did not match, so the evaluator returned `overall_pass=false` without a gold-resolution error. This case illustrates why reaching or confirming the reviewed interaction state is part of the reporting task.

```json
{"verdict":"no_issue_found","selector":"","target":"GitLab Dashboard Projects top tab: Yours","issue_type":"visible_focus","observed_behavior":"Tab and Shift+Tab moved among header controls, but focus was never confirmed on the Yours tab.","evidence":"Repeated activeElement checks never matched a.shortcuts-activity.nav-link[href=\"/dashboard/projects\"]."}
```

Evaluator summary: `expected_verdict=issue_found`, `observed_verdict=no_issue_found`, `selector_errors=[]`, `overall_pass=false`, `evaluator_error=false`.

These examples use the same evaluator fields as the formal runs. Natural-language `target`, `observed_behavior`, and `evidence` are retained for audit but do not act as an independent semantic score. The automatic decision uses the normalized verdict, selector-to-DOM target resolution, and normalized issue family; issue-list recall and precision additionally count unmatched findings as extras.
