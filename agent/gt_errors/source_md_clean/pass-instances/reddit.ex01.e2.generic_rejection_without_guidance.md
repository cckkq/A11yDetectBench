# PASS Instance

```yaml
instance_id: reddit.ex01.e2.generic_rejection_without_guidance
template_id: error.e2.generic_rejection_without_guidance
issue_present: false
source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: EX01
  matched_positive: reddit.ex01.e2.generic_rejection_without_guidance
page:
  site: reddit
  page_name: Login
  start_url: http://localhost:9999/login
  auth_state_file: null
target:
  selector: input#login-username[name="_username"], input#login-password[name="_password"]
  description: the username and password inputs in the Reddit login form
  coverage_policy: representative_group
probe: Enter invalid credentials in the target fields and submit the login form.
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

- This PASS L1 instance is counterfactually derived from BASE L1 `reddit.ex01.e2.generic_rejection_without_guidance`.
- Target selector, target description, start URL, auth state, criterion, and probe intentionally match the BASE L1 source instance.
- The PASS condition is supplied by the runtime counterfactual patch; the target remains the same stable interaction or input path.
