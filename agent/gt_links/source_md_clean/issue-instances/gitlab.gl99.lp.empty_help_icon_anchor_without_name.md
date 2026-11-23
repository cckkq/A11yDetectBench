# Issue Instance

```yaml
instance_id: gitlab.gl99.lp.empty_help_icon_anchor_without_name
template_id: links.link_purpose.gitlab.empty_help_icon_anchor_without_name
issue_present: true

source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: GL99

page:
  site: gitlab
  page_name: New Snippet
  start_url: http://localhost:8023/-/snippets/new
  auth_state_file: runtime_auth_state_placeholder.json

target:
  selector: 'main#content-body a[href*=''/help/user/public_access'']'
  description: the empty help icon link beside the Visibility level field
  coverage_policy: single

criterion:
  issue_family: link_purpose
  wcag_target: WCAG 2.4.4 Link Purpose (In Context)

gold:
  expected_verdict: issue_found
  evidence_rule: >-
    The matched help icon anchor element has an empty accessible name. The nearby
    Visibility level label is visual context, but it is not exposed as the link
    name or accessible description.
```

## Selector Check

- The `target.selector` value resolves to one visible element on GL99.
- The matched element has empty text, no `aria-label`, no `title`, and contains only an aria-hidden help icon.
