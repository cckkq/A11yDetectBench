# PASS Instance

```yaml
instance_id: shopping_admin.pa01.lp.dashboard_chart_disabled_here_link_has_sentence_context
template_id: links.link_purpose.pass.shopping_admin.dashboard_chart_disabled_here_link_has_sentence_context
issue_present: false

source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: PA01
  matched_positive: shopping_admin.pa01.lp.tooltip_help_what_is_this_without_target_context

page:
  site: shopping_admin
  page_name: Dashboard
  start_url: http://localhost:7780/admin/admin/dashboard/
  auth_state_file: runtime_auth_state_placeholder.json

target:
  selector: 'main#anchor-content .dashboard-diagram-disabled a'
  description: the `here` link in the disabled dashboard chart message
  coverage_policy: single

criterion:
  issue_family: link_purpose
  wcag_target: WCAG 2.4.4 Link Purpose (In Context)

gold:
  expected_verdict: no_issue_found
  evidence_rule: >-
    The matched anchor element is in the sentence `Chart is disabled. To enable the
    chart, click here.` and its href points to the dashboard chart
    configuration section. The same sentence identifies the link purpose, so
    the Link Purpose issue is not present for this target.
```

## Selector Check

- The selector targets the visible `here` link in the Dashboard chart-disabled message on PA01.
- This target is different from the `What is this?` help-link positive target.
