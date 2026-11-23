# PASS Instance

```yaml
instance_id: gitlab.gl11.lp.commit_email_learn_more_link_has_context
template_id: links.link_purpose.pass.gitlab.commit_email_learn_more_link_has_context
issue_present: false

source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: GL11
  matched_positive: gitlab.gl11.lp.empty_help_icon_anchor_without_name

page:
  site: gitlab
  page_name: Profile
  start_url: http://localhost:8023/-/profile
  auth_state_file: runtime_auth_state_placeholder.json

target:
  selector: 'form a[href*=''change-the-email-displayed-on-your-commits'']'
  description: the Learn more link in the Commit email form group
  coverage_policy: single

criterion:
  issue_family: link_purpose
  wcag_target: WCAG 2.4.4 Link Purpose (In Context)

gold:
  expected_verdict: no_issue_found
  evidence_rule: >-
    The matched anchor element has visible text `Learn more.` and appears in the Commit
    email form group after text explaining that the selected email is used for
    web based operations such as edits and merges. Its href targets the profile
    help section about changing the email displayed on commits, so the link
    purpose is determinable from its text and form-group context.
```

## Selector Check

- A construction-time selector check confirmed one visible matching Commit email Learn more link on GL11.
- The matched link text is `Learn more.` and the form-group context begins with `Commit email`.
