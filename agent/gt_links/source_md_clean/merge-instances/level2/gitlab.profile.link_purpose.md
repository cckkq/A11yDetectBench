# Merge Instance

```yaml
instance_id: gitlab.profile.link_purpose
task_level: level2
issue_present: true

source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: GL11
  review_status: source_and_live_checked

page:
  site: gitlab
  page_name: Profile
  start_url: http://localhost:8023/-/profile
  auth_state_file: runtime_auth_state_placeholder.json

scope:
  issue_family: link_purpose
  wcag_target: WCAG 2.4.4 Link Purpose (In Context)
  assessment_requirement: L.2 Link Purpose

gold:
  expected_verdict: issue_found
  issues:
    - issue_id: gitlab.gl11.lp.empty_help_icon_anchor_without_name
      target:
        selector: 'main#content-body a[href*=''make-your-user-profile-page-private'']'
        description: the empty help icon link beside the Private profile setting
        coverage_policy: single
      criterion:
        issue_family: link_purpose
        wcag_target: WCAG 2.4.4 Link Purpose (In Context)
      evidence_rule: >-
        The matched help icon anchor element has an empty accessible name. The nearby
        Private profile label is visual context, but it is not exposed as the
        link name or accessible description.
```

## Source And Live Check

- `gitlab-link-purpose-record.md` GL11 states that the stable 6.2 Link Purpose failure is LP027, the empty profile-private help icon; `Learn more.` and `Cancel` are PASS.
- Fresh live GL11 probe after refreshing GitLab auth found one visible anchor element matching `main#content-body a[href*='make-your-user-profile-page-private']`.
- The matched anchor element has empty text/name fields and href `/help/user/profile/index.md#make-your-user-profile-page-private`.

## Merge Scope

- L2 owner key: `gitlab + http://localhost:8023/-/profile + link_purpose + WCAG 2.4.4 Link Purpose (In Context)`.
- This merge instance should generate one L2 task for GL11 link purpose.
- The single `gold.issues[]` entry preserves the GL11 source-record link-purpose failure group already anchored by a clean atomic issue instance.
