# Merge Instance

```yaml
instance_id: gitlab.dashboard_activity.link_purpose
task_level: level2
issue_present: true

source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: GL50
  review_status: source_and_live_checked

page:
  site: gitlab
  page_name: Dashboard Activity
  start_url: http://localhost:8023/dashboard/activity
  auth_state_file: runtime_auth_state_placeholder.json

scope:
  issue_family: link_purpose
  wcag_target: WCAG 2.4.4 Link Purpose (In Context)
  assessment_requirement: L.2 Link Purpose

gold:
  expected_verdict: issue_found
  issues:
    - issue_id: gitlab.gl50.lp.dashboard_activity_rss_subscribe_anchor_without_target_context
      target:
        selector: 'main#content-body a[title=''Subscribe''][href*=''.atom''], main#content-body a[aria-label=''Subscribe''][href*=''.atom'']'
        description: the `Subscribe` RSS feed anchor element on the dashboard activity page
        coverage_policy: single
      criterion:
        issue_family: link_purpose
        wcag_target: WCAG 2.4.4 Link Purpose (In Context)
      evidence_rule: >-
        The matched link has computed name `Subscribe` and no description beyond
        the same generic name. The name does not identify that the link
        subscribes to the dashboard activity feed.
```

## Source And Live Check

- `gitlab-link-purpose-record.md` GL50 states that the stable 6.2 Link Purpose failure is the RSS `Subscribe` link; page uniqueness or URL inference is not accepted as link-purpose context.
- Fresh live GL50 probe after refreshing GitLab auth found one visible RSS `Subscribe` Atom-feed anchor element and no profile Gravatar anchor element in the main content.
- The matched `Subscribe` anchor element has title `Subscribe`, `aria-label=Subscribe`, and href `/dashboard/projects.atom?...`.

## Merge Scope

- L2 owner key: `gitlab + http://localhost:8023/dashboard/activity + link_purpose + WCAG 2.4.4 Link Purpose (In Context)`.
- This merge instance should generate one L2 task for GL50 link purpose.
- The single `gold.issues[]` entry preserves the GL50 source-record link-purpose failure group already anchored by a clean atomic issue instance.
