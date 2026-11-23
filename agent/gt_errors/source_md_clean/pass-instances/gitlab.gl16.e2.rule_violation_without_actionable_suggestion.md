# PASS Instance

```yaml
instance_id: gitlab.gl16.e2.rule_violation_without_actionable_suggestion
template_id: error.e2.rule_violation_without_actionable_suggestion
issue_present: false
source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: GL16
  matched_positive: gitlab.gl16.e2.rule_violation_without_actionable_suggestion
page:
  site: gitlab
  page_name: Emails
  start_url: http://localhost:8023/-/profile/emails
  auth_state_file: runtime_auth_state_placeholder.json
target:
  selector: input#email_email[name="email[email]"]
  description: the add-email input in the GitLab Emails settings form
  coverage_policy: single
probe: Enter `abc` in the target field and submit the add-email form.
criterion:
  issue_family: error_suggestion
  wcag_target: WCAG 3.3.3 Error Suggestion
gold:
  expected_verdict: no_issue_found
  evidence_rule: >-
    Counterfactual PASS L1 for the matched BASE target/probe: the runtime patch is expected
    to remediate the same target path so any automatically detected input error provides an
    actionable correction suggestion. A reported E.2 issue on this matched target is a false
    alarm for this task.
```

## Selector Check

- This PASS L1 instance is counterfactually derived from BASE L1 `gitlab.gl16.e2.rule_violation_without_actionable_suggestion`.
- Target selector, target description, start URL, auth state, criterion, and probe intentionally match the BASE L1 source instance.
- The PASS condition is supplied by the runtime counterfactual patch; the target remains the same stable interaction or input path.
