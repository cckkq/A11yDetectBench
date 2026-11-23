# PASS Instance

```yaml
instance_id: gitlab.gl50.lp.activity_push_events_filter_has_specific_purpose
template_id: links.link_purpose.pass.gitlab.activity_push_events_filter_has_specific_purpose
issue_present: false

source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: GL50
  matched_positive: gitlab.gl50.lp.dashboard_activity_rss_subscribe_anchor_without_target_context

page:
  site: gitlab
  page_name: Dashboard Activity
  start_url: http://localhost:8023/dashboard/activity
  auth_state_file: runtime_auth_state_placeholder.json

target:
  selector: 'main#content-body a#push_event_filter'
  description: the Push events filter anchor element on the dashboard activity page
  coverage_policy: single

criterion:
  issue_family: link_purpose
  wcag_target: WCAG 2.4.4 Link Purpose (In Context)

gold:
  expected_verdict: no_issue_found
  evidence_rule: >-
    The matched anchor element has visible text `Push events` and title
    `Filter by push events`. The name identifies that the link filters the
    activity feed to push events, so the Link Purpose issue is not present for
    this target.
```

## Selector Check

- A construction-time selector check confirmed one visible matching Push events filter link on GL50.
- The matched link is in the same activity filter row as the dashboard activity feed controls.
