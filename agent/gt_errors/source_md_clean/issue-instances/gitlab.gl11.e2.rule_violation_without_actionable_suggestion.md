# Issue Instance

```yaml
instance_id: gitlab.gl11.e2.rule_violation_without_actionable_suggestion
template_id: error.e2.rule_violation_without_actionable_suggestion
issue_present: true

source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: GL11

page:
  site: gitlab
  page_name: Profile settings
  start_url: http://localhost:8023/-/profile
  auth_state_file: runtime_auth_state_placeholder.json

target:
  selector: 'input#user_website_url[name="user[website_url]"]'
  description: the Website URL input in the GitLab profile form
  coverage_policy: single

probe: Enter `not-a-url` in the target field and submit the profile form.

criterion:
  issue_family: error_suggestion
  wcag_target: WCAG 3.3.3 Error Suggestion

gold:
  expected_verdict: issue_found
  evidence_rule: >-
    The page detects the Website URL value as invalid but does not provide an
    accepted URL format, an example URL, or another actionable correction
    direction. Other better validation paths on the same page do not rescue this
    Website URL path.
```

## Selector Check

- `document.querySelectorAll('input#user_website_url[name="user[website_url]"]')` resolves to one visible input on GL11.
- The matched input has `id="user_website_url"`, `name="user[website_url]"`, label text `Website url`, and is the field used by the invalid URL submission path.
- A fresh Playwright probe with refreshed GitLab auth entered `not-a-url` in this input and submitted the profile form. The page then displayed one visible alert message: `Website url is not a valid URL`.
- The alert message is evidence for this issue, but it is not the target selector. The target selector is the stable Website URL input path.
