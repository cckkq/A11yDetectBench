# Experiment Config

This file records the submitted snapshot protocol, not every development-time runner default.

## Formal Defaults

| Field | Value |
| --- | --- |
| Model | `gpt-5.2-20251211` |
| Reasoning effort | `xhigh` |
| Temperature | `0` |
| Repeats | `3` per manifest entry |
| Max steps | `25` per task |
| Parallel workers | `3` |
| Schema enhancement | on |
| Headless browser | true |
| Browser interaction highlights | off |
| Structured failure capture | on |
| Multi-JSON salvage | on |
| Auth | fresh storage state plus probe for each auth-required task |
| Global auth state file | none |
| Required per-run artifacts | `usage.json`, `final-response.json`, `evaluation.json` |

The browser-agent framework was browser-use `0.12.6` with the structured-output robustness patch recorded in `third_party/browser-use-0.12.6-structured-output.patch`.

## Batch manifests

- Links selected-issue: `agent/gt_links/experiments/links_base_l1_l2_l3_v1.yaml`
- Links no-issue L1: `agent/gt_links/experiments/links_pass_l1_v1.yaml`
- Links issue-list: `agent/gt_links/experiments/links_merge_l2_l3_v1.yaml`
- Keyboard selected-issue: `agent/gt_keyboard/experiments/keyboard_base_l1_l2_l3_v1.yaml`
- Keyboard no-issue L1: `agent/gt_keyboard/experiments/keyboard_pass_l1_v1.yaml`
- Keyboard issue-list: `agent/gt_keyboard/experiments/keyboard_merge_l2_l3_v1.yaml`
- Errors/status selected-issue: `agent/gt_errors/experiments/formal_error_experiment_v1.yaml`
- Focus selected-issue: `agent/gt_focus/experiments/formal_focus_experiment_v1.yaml`
- Errors/status no-issue L1: `agent/gt_errors/experiments/error_pass_l1_v1.yaml`
- Focus no-issue L1: `agent/gt_focus/experiments/focus_pass_l1_v1.yaml`
- Errors/status and Focus issue-list: `errors_issue_list_release.yaml` and `focus_issue_list_release.yaml` in their respective experiment directories. These two release indexes enumerate the submitted task files and use the protocol defaults above.

The twelve manifests together cover all 686 task files once before repeats. Two earlier Focus evidence manifests are preserved in [historical-manifests](historical-manifests/). They referred to an earlier task directory and are kept as protocol records.

## Command Pattern

Use the relevant family module and manifest. For example:

```powershell
python -m agent.gt_links.run_experiment_parallel `
  --manifest agent/gt_links/experiments/links_base_l1_l2_l3_v1.yaml `
  --parallel 3 `
  --refresh-session-every 1 `
  --headless `
  --model gpt-5.2-20251211 `
  --reasoning-effort xhigh `
  --capture-structured-failures `
  --salvage-multi-json
```

Do not pass `--disable-schema-enhancement`. For Keyboard and Focus, leave browser highlights disabled by omitting `--enable-browser-highlights`.

## Page-Evidence Diagnostic

The page-evidence diagnostic uses the same model, temperature, reasoning effort, max-step, headless, schema, and structured-output settings above. It additionally passes a scanner-produced `candidate-manifest.suspects.json` through `--evidence-pack-manifest` to `agent.gt_focus.run_task` or `agent.gt_keyboard.run_task`.

Scanner and injection details are documented in `docs/PAGE_EVIDENCE.md`.


## Comparing scores with the paper

The [reference scores for Tables II–IV](reference-scores.json) come from the archived table audits. For selected issues and clean controls the file gives the numerator and denominator for each condition. For issue lists it gives element-level recall and precision, the unrounded values, and the policy for failed attempts. Those attempts count toward the denominator in Table IV. The [worked examples](CONSTRUCTION_PIPELINE.md) show how an individual report becomes a hit, a miss or an extra finding.

## Focus no-issue scores in Table III

The evaluator produces a mechanical verdict for each attempt. For the Focus L1 no-issue controls, Table III also includes a manual check. Reviewers credited a report only when it matched the reference element and issue type, had no extra issue, and explicitly identified the injected focus repair in its response or history. Other false alarms kept their original score. The [archived decision rule and counts](focus-table3-reference.json) show the raw and adjusted results for all three models. Keep both numbers when comparing with the paper.
