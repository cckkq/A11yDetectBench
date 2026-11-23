# PASS Instance

```yaml
instance_id: gitlab.gl11.collapse_sidebar_not_tabbable
template_id: keyboard.keyboard_nonreachable.sidebar_collapse_toggle_not_tabbable
issue_present: false
source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: GL11
  matched_positive: gitlab.gl11.collapse_sidebar_not_tabbable
page:
  site: gitlab
  page_name: Edit Profile
  start_url: http://localhost:8023/-/profile
  auth_state_file: runtime_auth_state_placeholder.json
target:
  selector: aside a[role="button"][title="Toggle sidebar"]
  description: the Collapse sidebar toggle in GitLab user settings
  coverage_policy: single
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

- This PASS L1 instance is counterfactually derived from BASE L1 `gitlab.gl11.collapse_sidebar_not_tabbable`.
- Page, target selector, target description, setup, and criterion intentionally match the BASE L1 source instance.
- The PASS condition is supplied by the Keyboard runtime counterfactual patch; the target remains the same keyboard path.
