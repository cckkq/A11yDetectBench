# PASS Instance

```yaml
instance_id: gitlab.gl01.custom_selector_context_change
template_id: keyboard.on_input.custom_selector_change_triggers_context_change
issue_present: false
source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: GL01
  matched_positive: gitlab.gl01.custom_selector_context_change
page:
  site: gitlab
  page_name: Dashboard
  start_url: http://localhost:8023/
  auth_state_file: runtime_auth_state_placeholder.json
target:
  selector: button#sort-projects-dropdown
  description: the project sort dropdown on the GitLab Dashboard
  coverage_policy: single
criterion:
  issue_family: on_input
  wcag_target: WCAG 3.2.2 On Input
gold:
  expected_verdict: no_issue_found
  evidence_rule: >-
    Counterfactual PASS L1 for the matched BASE target: the runtime patch is expected to remove
    the reviewed keyboard failure while keeping the same page, setup, target selector, and
    criterion. A reported keyboard issue on this matched clean target is a false alarm for
    this task.
```

## Selector Check

- This PASS L1 instance is counterfactually derived from BASE L1 `gitlab.gl01.custom_selector_context_change`.
- Page, target selector, target description, setup, and criterion intentionally match the BASE L1 source instance.
- The PASS condition is supplied by the Keyboard runtime counterfactual patch; the target remains the same keyboard path.
