# Page-Evidence Diagnostic

The page-evidence diagnostic is a diagnostic condition for Focus and Keyboard L2 issue-list tasks. It gives the agent automatically probed page and interaction facts without giving evaluator rules, expected verdicts, reviewed issue lists, or human review rationales.

## Scanner Code

The scanner package is `agent/evidence_baseline/`.

| Component | Role |
| --- | --- |
| `keyboard_collector.py` | Keyboard reachability scanner. It records real Tab traversal, inventories visible interactive candidates, and optionally probes composite widgets with arrow keys. |
| `focus_collector.py` | Focus-visible scanner. It records focus movement, style snapshots, before/after screenshots when enabled, and focus-crop visual deltas. |
| `run_candidates.py` | CLI/orchestrator that loads one task, prepares auth and page state, runs the right scanner, writes candidate manifests, and optionally evaluates candidate-grounding against a rule for offline audit. |
| `candidates.py` | Candidate selection rules for Keyboard and Focus scanner outputs. |
| `offline_eval.py` | Candidate-manifest precision/recall audit against evaluator-rule targets. |
| `focus_vlm.py` | Optional Focus crop VLM review helpers. Optional VLM review uses a locally configured OpenAI-compatible client. Use `--no-focus-vlm` for the scanner-only condition. |
| `overlay.py` | Non-interactive A11Y marker overlay helpers used for evidence-assisted observation. |

The two scanner functions are:

- `collect_keyboard_reachability_candidates(...)`
- `collect_focus_visible_candidates(...)`

## Candidate Generation

This example collects focus evidence on the Shopping Admin PA15 page. Use the same task in both commands.

```powershell
python -m agent.evidence_baseline.run_candidates `
  --task agent/gt_focus/generated_clean_pilot/generated_merge/tasks/shopping_admin.pa15.visible_focus.verify.level2.v1.yaml `
  --output-dir runs/pa15-focus-evidence `
  --no-focus-vlm
```

The output directory contains:

- `candidate-manifest.full.json`: full scanner trace and candidate data.
- `candidate-manifest.suspects.json`: compact candidate list used by the evidence-assisted runner condition.
- `candidate-eval.json`: optional offline candidate-grounding audit when an evaluator rule is available.

For Focus, omitting `--no-focus-vlm` and passing `--focus-vlm-model <model>` enables optional crop review through a local OpenAI-compatible client. The non-VLM fallback still records focus traces, computed-style changes, and pixel deltas.

## Downstream Injection

Focus and Keyboard runners accept the compact scanner manifest through `--evidence-pack-manifest`:

```powershell
python -m agent.gt_focus.run_task `
  --task agent/gt_focus/generated_clean_pilot/generated_merge/tasks/shopping_admin.pa15.visible_focus.verify.level2.v1.yaml `
  --evidence-pack-manifest runs/pa15-focus-evidence/candidate-manifest.suspects.json `
  --model gpt-5.2-20251211 `
  --reasoning-effort xhigh `
  --temperature 0 `
  --max-steps 25 `
  --headless `
  --capture-structured-failures `
  --salvage-multi-json `
  --disable-highlight-elements
```

Use `agent.gt_keyboard.run_task` for Keyboard tasks with the same evidence-pack argument. The helper `agent/evidence_assisted_observation.py` loads `candidate-manifest.suspects.json`, appends a compact prompt suffix, and adds non-interactive `A11Y-F*` or `A11Y-K*` markers to browser observations.

## Diagnostic Scope

The June 19, 2026 experiment compared the agent with and without scanner evidence on the same L2 issue-list tasks. Each task asks the agent to check one page for one type of barrier. For example, PA15 is one Focus task whose reference answer includes both the date-picker buttons and the Apply Rules button.

The final table uses the tasks linked below. There are 13 Focus tasks and 15 Keyboard tasks. Each condition ran each task three times, giving 39 Focus attempts and 45 Keyboard attempts per condition.

| Site | Focus visibility | Keyboard reachability |
| --- | --- | --- |
| GitLab | [GL01](../agent/gt_focus/generated_clean_pilot/generated_merge/tasks/gitlab.gl01.visible_focus.verify.level2.v1.yaml), [GL02](../agent/gt_focus/generated_clean_pilot/generated_merge/tasks/gitlab.gl02.visible_focus.verify.level2.v1.yaml), [GL96](../agent/gt_focus/generated_clean_pilot/generated_merge/tasks/gitlab.gl96.visible_focus.verify.level2.v1.yaml) | [GL11](../agent/gt_keyboard/generated_clean_pilot/generated_merge/tasks/gitlab.gl11.keyboard_nonreachable.verify.level2.v1.yaml), [GL12](../agent/gt_keyboard/generated_clean_pilot/generated_merge/tasks/gitlab.gl12.keyboard_nonreachable.verify.level2.v1.yaml), [GL15](../agent/gt_keyboard/generated_clean_pilot/generated_merge/tasks/gitlab.gl15.keyboard_nonreachable.verify.level2.v1.yaml), [GL27](../agent/gt_keyboard/generated_clean_pilot/generated_merge/tasks/gitlab.gl27.keyboard_nonreachable.verify.level2.v1.yaml), [GL28](../agent/gt_keyboard/generated_clean_pilot/generated_merge/tasks/gitlab.gl28.keyboard_nonreachable.verify.level2.v1.yaml), [GL82](../agent/gt_keyboard/generated_clean_pilot/generated_merge/tasks/gitlab.gl82.keyboard_nonreachable.verify.level2.v1.yaml), [GL83](../agent/gt_keyboard/generated_clean_pilot/generated_merge/tasks/gitlab.gl83.keyboard_nonreachable.verify.level2.v1.yaml) |
| Shopping | [P16](../agent/gt_focus/generated_clean_pilot/generated_merge/tasks/shopping.p16.visible_focus.verify.level2.v1.yaml), [P29](../agent/gt_focus/generated_clean_pilot/generated_merge/tasks/shopping.p29.visible_focus.verify.level2.v1.yaml) | [P16](../agent/gt_keyboard/generated_clean_pilot/generated_merge/tasks/shopping.p16.keyboard_nonreachable.verify.level2.v1.yaml) |
| Shopping Admin | [PA02](../agent/gt_focus/generated_clean_pilot/generated_merge/tasks/shopping_admin.pa02.visible_focus.verify.level2.v1.yaml), [PA04](../agent/gt_focus/generated_clean_pilot/generated_merge/tasks/shopping_admin.pa04.visible_focus.verify.level2.v1.yaml), [PA08](../agent/gt_focus/generated_clean_pilot/generated_merge/tasks/shopping_admin.pa08.visible_focus.verify.level2.v1.yaml), [PA15](../agent/gt_focus/generated_clean_pilot/generated_merge/tasks/shopping_admin.pa15.visible_focus.verify.level2.v1.yaml), [PA27](../agent/gt_focus/generated_clean_pilot/generated_merge/tasks/shopping_admin.pa27.visible_focus.verify.level2.v1.yaml), [PA58](../agent/gt_focus/generated_clean_pilot/generated_merge/tasks/shopping_admin.pa58.visible_focus.verify.level2.v1.yaml), [PA62](../agent/gt_focus/generated_clean_pilot/generated_merge/tasks/shopping_admin.pa62.visible_focus.verify.level2.v1.yaml), [PA75](../agent/gt_focus/generated_clean_pilot/generated_merge/tasks/shopping_admin.pa75.visible_focus.verify.level2.v1.yaml) | [PA04](../agent/gt_keyboard/generated_clean_pilot/generated_merge/tasks/shopping_admin.pa04.keyboard_nonreachable.verify.level2.v1.yaml), [PA05](../agent/gt_keyboard/generated_clean_pilot/generated_merge/tasks/shopping_admin.pa05.keyboard_nonreachable.verify.level2.v1.yaml), [PA08](../agent/gt_keyboard/generated_clean_pilot/generated_merge/tasks/shopping_admin.pa08.keyboard_nonreachable.verify.level2.v1.yaml), [PA11](../agent/gt_keyboard/generated_clean_pilot/generated_merge/tasks/shopping_admin.pa11.keyboard_nonreachable.verify.level2.v1.yaml), [PA50](../agent/gt_keyboard/generated_clean_pilot/generated_merge/tasks/shopping_admin.pa50.keyboard_nonreachable.verify.level2.v1.yaml), [PA68](../agent/gt_keyboard/generated_clean_pilot/generated_merge/tasks/shopping_admin.pa68.keyboard_nonreachable.verify.level2.v1.yaml), [PA69](../agent/gt_keyboard/generated_clean_pilot/generated_merge/tasks/shopping_admin.pa69.keyboard_nonreachable.verify.level2.v1.yaml) |

The recorded settings were GPT-5.2, temperature 0, reasoning effort `xhigh`, a 25-step limit, headless browsing, schema enhancement, structured failure capture and multi-JSON salvage.
