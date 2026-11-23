# Issue Instance

```yaml
instance_id: gitlab.gl11.lp.empty_help_icon_anchor_without_name
template_id: links.link_purpose.gitlab.empty_help_icon_anchor_without_name
issue_present: true

source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: GL11

page:
  site: gitlab
  page_name: Profile
  start_url: http://localhost:8023/-/profile
  auth_state_file: runtime_auth_state_placeholder.json

target:
  selector: 'main#content-body a[href*=''make-your-user-profile-page-private'']'
  description: the empty help icon link beside the Private profile setting
  coverage_policy: single

criterion:
  issue_family: link_purpose
  wcag_target: WCAG 2.4.4 Link Purpose (In Context)

gold:
  expected_verdict: issue_found
  evidence_rule: >-
    The matched help icon anchor element has an empty accessible name. The nearby
    Private profile label is visual context, but it is not exposed as the link
    name or accessible description.
```

## Selector Check

- The `target.selector` value resolves to one visible element on GL11.
- The matched element has empty text, no `aria-label`, no `title`, and href `/help/user/profile/index.md#make-your-user-profile-page-private`.
