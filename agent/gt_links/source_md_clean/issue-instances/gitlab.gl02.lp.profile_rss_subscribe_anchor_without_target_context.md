# Issue Instance

```yaml
instance_id: gitlab.gl02.lp.profile_rss_subscribe_anchor_without_target_context
template_id: links.link_purpose.gitlab.rss_subscribe_anchor_without_target_context
issue_present: true

source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: GL02

page:
  site: gitlab
  page_name: User Profile
  start_url: http://localhost:8023/byteblaze
  auth_state_file: runtime_auth_state_placeholder.json

target:
  selector: "main#content-body a[title='Subscribe'][href*='.atom']"
  description: the `Subscribe` RSS feed anchor element on the user profile page
  coverage_policy: single

criterion:
  issue_family: link_purpose
  wcag_target: WCAG 2.4.4 Link Purpose (In Context)

gold:
  expected_verdict: issue_found
  evidence_rule: >-
    The matched link has computed name `Subscribe` and no description. The name
    does not identify that the link subscribes to the Byte Blaze user feed.
```

## Selector Check

- `document.querySelectorAll("main#content-body a[title='Subscribe'][href*='.atom']")` resolves to one element on GL02.
- The matched element is visible, has title-derived name `Subscribe`, href `/byteblaze.atom?...`, no `aria-label`, and no accessible description.
- The visible icon is an RSS glyph; the target feed is not part of the accessible name.
