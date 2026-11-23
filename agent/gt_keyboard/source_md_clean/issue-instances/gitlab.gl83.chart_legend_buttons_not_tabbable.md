# Issue Instance

```yaml
instance_id: gitlab.gl83.chart_legend_buttons_not_tabbable
template_id: keyboard.keyboard_nonreachable.visualization_embedded_interactives_not_keyboard_reachable
issue_present: true
source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: GL83
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
  expected_verdict: issue_found
  evidence_rule: The target (the all and success chart legend buttons in GitLab Pipeline Charts)
    is visible and pointer-operable or part of an active widget, but expected keyboard navigation
    cannot reach or complete operation of that same target. Reporting a different keyboard
    issue on the page does not satisfy this rule.
```

## Selector Check

- Playwright selector audit: Playwright resolved .gl-legend-inline .gl-legend-inline-series[role="button"] to visible all and success legend controls with tabindex -1.
- The selector is the BASE L1 target selector; unresolved or conflicting legacy targets were not included in this source set.
