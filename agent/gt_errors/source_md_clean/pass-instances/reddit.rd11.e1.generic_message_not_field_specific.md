# PASS Instance

```yaml
instance_id: reddit.rd11.e1.generic_message_not_field_specific
template_id: error.e1.generic_message_not_field_specific
issue_present: false
source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: RD11
  matched_positive: reddit.rd11.e1.generic_message_not_field_specific
page:
  site: reddit
  page_name: Account
  start_url: http://localhost:9999/user/MarvelsGrantMan136/account
  auth_state_file: runtime_auth_state_placeholder.json
target:
  selector: >-
    input#user_password_first[name="user[password][first]"], input#user_password_second[name="user[password][second]"]
  description: the New password and repeat password inputs in the Reddit account form
  coverage_policy: representative_group
probe: Enter different valid-length values in the target fields and save changes. Do not submit matching password values or otherwise save a valid account update.
criterion:
  issue_family: error_identification
  wcag_target: WCAG 3.3.1 Error Identification
gold:
  expected_verdict: no_issue_found
  evidence_rule: >-
    Counterfactual PASS L1 for the matched BASE target/probe: the runtime patch is expected
    to remediate the same target path so the page no longer lacks user-facing identification
    for the automatically detected input error. A reported E.1 issue on this matched target
    is a false alarm for this task.
```

## Selector Check

- This PASS L1 instance is counterfactually derived from BASE L1 `reddit.rd11.e1.generic_message_not_field_specific`.
- Target selector, target description, start URL, auth state, criterion, and probe intentionally match the BASE L1 source instance.
- The PASS condition is supplied by the runtime counterfactual patch; the target remains the same stable interaction or input path.
