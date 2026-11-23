# Issue Instance

```yaml
instance_id: gitlab.gl12.collapse_sidebar_not_tabbable
template_id: keyboard.keyboard_nonreachable.sidebar_collapse_toggle_not_tabbable
issue_present: true
source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: GL12
page:
  site: gitlab
  page_name: Account Settings
  start_url: http://localhost:8023/-/profile/account
  auth_state_file: runtime_auth_state_placeholder.json
target:
  selector: aside a[role="button"][title="Toggle sidebar"]
  description: the Collapse sidebar toggle in GitLab account settings
  coverage_policy: single
criterion:
  issue_family: keyboard_nonreachable
  wcag_target: WCAG 2.1.1 Keyboard
gold:
  expected_verdict: issue_found
  evidence_rule: The target (the Collapse sidebar toggle in GitLab account settings) is visible
    and pointer-operable or part of an active widget, but expected keyboard navigation cannot
    reach or complete operation of that same target. Reporting a different keyboard issue
    on the page does not satisfy this rule.
```

## Selector Check

- Playwright selector audit: Playwright resolved aside a[role="button"][title="Toggle sidebar"] to one visible sidebar toggle link-button.
- The selector is the BASE L1 target selector; unresolved or conflicting legacy targets were not included in this source set.
