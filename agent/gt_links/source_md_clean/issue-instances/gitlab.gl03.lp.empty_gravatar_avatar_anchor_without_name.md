# Issue Instance

```yaml
instance_id: gitlab.gl03.lp.empty_gravatar_avatar_anchor_without_name
template_id: links.link_purpose.gitlab.empty_gravatar_avatar_anchor_without_name
issue_present: true

source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: GL03

page:
  site: gitlab
  page_name: User Activity
  start_url: http://localhost:8023/users/byteblaze/activity
  auth_state_file: runtime_auth_state_placeholder.json

target:
  selector: "main#content-body .avatar-holder > a[href*='gravatar.com/avatar']"
  description: the profile header external Gravatar avatar anchor element on the user activity page
  coverage_policy: single

criterion:
  issue_family: link_purpose
  wcag_target: WCAG 2.4.4 Link Purpose (In Context)

gold:
  expected_verdict: issue_found
  evidence_rule: >-
    The matched avatar anchor element has an empty accessible name. Its child image has
    empty `alt`, and no aria label, title, or description provides the external
    Gravatar link purpose.
```

## Selector Check

- `document.querySelectorAll("main#content-body .avatar-holder > a[href*='gravatar.com/avatar']")` resolves to one element on GL03.
- The matched element is visible, has empty text, no `aria-label`, no `title`, and href `https://www.gravatar.com/avatar/...`.
- The old probe reports AX role `link`, empty AX name, and no accessible description.
