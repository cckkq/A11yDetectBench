# Issue Instance

```yaml
instance_id: gitlab.gl06.lp.empty_gravatar_avatar_anchor_without_name
template_id: links.link_purpose.gitlab.empty_gravatar_avatar_anchor_without_name
issue_present: true

source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: GL06

page:
  site: gitlab
  page_name: User Projects
  start_url: http://localhost:8023/users/byteblaze/projects
  auth_state_file: runtime_auth_state_placeholder.json

target:
  selector: 'main#content-body .avatar-holder > a[href*=''gravatar.com/avatar'']'
  description: the profile header external Gravatar avatar anchor element on the user projects page
  coverage_policy: single

criterion:
  issue_family: link_purpose
  wcag_target: WCAG 2.4.4 Link Purpose (In Context)

gold:
  expected_verdict: issue_found
  evidence_rule: >-
    The matched avatar anchor element has an empty accessible name. Its child image has
    empty alt, and no aria label, title, or description provides the external
    Gravatar link purpose.
```

## Selector Check

- The `target.selector` value resolves to one visible element on GL06.
- The matched element has empty text, no `aria-label`, no `title`, empty child image `alt`, and href `https://www.gravatar.com/avatar/...`.
