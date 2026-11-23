# Issue Instance

```yaml
instance_id: gitlab.gl50.lp.dashboard_activity_rss_subscribe_anchor_without_target_context
template_id: links.link_purpose.gitlab.rss_subscribe_anchor_without_target_context
issue_present: true

source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: GL50

page:
  site: gitlab
  page_name: Dashboard Activity
  start_url: http://localhost:8023/dashboard/activity
  auth_state_file: runtime_auth_state_placeholder.json

target:
  selector: 'main#content-body a[title=''Subscribe''][href*=''.atom''], main#content-body a[aria-label=''Subscribe''][href*=''.atom'']'
  description: the Subscribe RSS feed anchor element on the dashboard activity page
  coverage_policy: single

criterion:
  issue_family: link_purpose
  wcag_target: WCAG 2.4.4 Link Purpose (In Context)

gold:
  expected_verdict: issue_found
  evidence_rule: >-
    The matched link has computed name Subscribe and no description. The name
    does not identify that the link subscribes to the dashboard activity feed.
```

## Selector Check

- The `target.selector` value resolves to one visible element on GL50.
- The matched element has `aria-label` and `title` both equal to `Subscribe`, and href `/dashboard/projects.atom?...`.
