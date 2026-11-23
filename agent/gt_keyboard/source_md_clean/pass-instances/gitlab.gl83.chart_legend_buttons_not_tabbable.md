# PASS Instance

```yaml
instance_id: gitlab.gl83.chart_legend_buttons_not_tabbable
template_id: >-
  keyboard.keyboard_nonreachable.visualization_embedded_interactives_not_keyboard_reachable
issue_present: false
source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: GL83
  matched_positive: gitlab.gl83.chart_legend_buttons_not_tabbable
page:
  site: gitlab
  page_name: Pipeline Charts
  start_url: http://localhost:8023/byteblaze/dotfiles/-/pipelines/charts
  auth_state_file: runtime_auth_state_placeholder.json
target:
  selector: .gl-legend-inline .gl-legend-inline-series[role="button"]
  description: the all and success chart legend buttons in GitLab Pipeline Charts
  coverage_policy: representative_group
criterion:
  issue_family: keyboard_nonreachable
  wcag_target: WCAG 2.1.1 Keyboard
gold:
  expected_verdict: no_issue_found
  evidence_rule: >-
    Counterfactual PASS L1 for the matched BASE target: the runtime patch is expected to remove
    the reviewed keyboard failure while keeping the same page, setup, target selector, and
    criterion. A reported keyboard issue on this matched clean target is a false alarm for
    this task.
```

## Selector Check

- This PASS L1 instance is counterfactually derived from BASE L1 `gitlab.gl83.chart_legend_buttons_not_tabbable`.
- Page, target selector, target description, setup, and criterion intentionally match the BASE L1 source instance.
- The PASS condition is supplied by the Keyboard runtime counterfactual patch; the target remains the same keyboard path.
