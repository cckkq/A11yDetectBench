# PASS Instance

```yaml
instance_id: gitlab.gl70.e4.status_text_change_without_live_semantics
template_id: error.e4.status_text_change_without_live_semantics
issue_present: false
source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: GL70
  matched_positive: gitlab.gl70.e4.status_text_change_without_live_semantics
page:
  site: gitlab
  page_name: CI/CD Editor
  start_url: http://localhost:8023/byteblaze/dotfiles/-/ci/editor?branch_name=main
  auth_state_file: runtime_auth_state_placeholder.json
target:
  selector: .monaco-editor textarea.inputarea[role="textbox"]
  description: the YAML editor textbox in the GitLab CI/CD pipeline editor
  coverage_policy: single
probe: >-
  Choose Configure pipeline to open the editor, change the YAML in the target editor from
  valid to invalid, and observe the pipeline validation message.
criterion:
  issue_family: status_messages
  wcag_target: WCAG 4.1.3 Status Messages
gold:
  expected_verdict: no_issue_found
  evidence_rule: >-
    Counterfactual PASS L1 for the matched BASE target/probe: the runtime patch is expected
    to remediate the same target interaction so the triggered same-page status, error, or
    progress message is programmatically exposed through role, aria-live, or equivalent status-message
    semantics. A reported E.4 issue on this matched target is a false alarm for this task.
```

## Selector Check

- This PASS L1 instance is counterfactually derived from BASE L1 `gitlab.gl70.e4.status_text_change_without_live_semantics`.
- Target selector, target description, start URL, auth state, criterion, and probe intentionally match the BASE L1 source instance.
- The PASS condition is supplied by the runtime counterfactual patch; the target remains the same stable interaction or input path.
