# Merge Instance

```yaml
instance_id: gitlab.snippets_new.link_purpose
task_level: level2
issue_present: true

source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: GL99
  review_status: source_and_live_checked

page:
  site: gitlab
  page_name: New Snippet
  start_url: http://localhost:8023/-/snippets/new
  auth_state_file: runtime_auth_state_placeholder.json

scope:
  issue_family: link_purpose
  wcag_target: WCAG 2.4.4 Link Purpose (In Context)
  assessment_requirement: L.2 Link Purpose

gold:
  expected_verdict: issue_found
  issues:
    - issue_id: gitlab.gl99.lp.empty_help_icon_anchor_without_name
      target:
        selector: 'main#content-body a[href*=''/help/user/public_access'']'
        description: the empty help icon link beside the Visibility level field
        coverage_policy: single
      criterion:
        issue_family: link_purpose
        wcag_target: WCAG 2.4.4 Link Purpose (In Context)
      evidence_rule: >-
        The matched help icon anchor element has an empty accessible name. The nearby
        Visibility level label is visual context, but it is not exposed as the
        link name or accessible description.
```

## Source And Live Check

- `gitlab-link-purpose-record.md` GL99 states that the stable 6.2 Link Purpose failure is LP009, the empty Visibility level help icon; the topbar `Issues` and form `Cancel` links are PASS.
- Fresh live GL99 probe after refreshing GitLab auth found one visible anchor element matching `main#content-body a[href*='/help/user/public_access']`.
- The matched anchor element has empty text/name fields and href `/help/user/public_access`.

## Merge Scope

- L2 owner key: `gitlab + http://localhost:8023/-/snippets/new + link_purpose + WCAG 2.4.4 Link Purpose (In Context)`.
- This merge instance should generate one L2 task for GL99 link purpose.
- The single `gold.issues[]` entry preserves the GL99 source-record link-purpose failure group already anchored by a clean atomic issue instance.
