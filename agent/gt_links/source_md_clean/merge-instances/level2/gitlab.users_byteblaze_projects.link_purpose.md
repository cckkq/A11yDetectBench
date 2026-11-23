# Merge Instance

```yaml
instance_id: gitlab.users_byteblaze_projects.link_purpose
task_level: level2
issue_present: true

source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: GL06
  review_status: source_and_live_checked

page:
  site: gitlab
  page_name: User Projects
  start_url: http://localhost:8023/users/byteblaze/projects
  auth_state_file: runtime_auth_state_placeholder.json

scope:
  issue_family: link_purpose
  wcag_target: WCAG 2.4.4 Link Purpose (In Context)
  assessment_requirement: L.2 Link Purpose

gold:
  expected_verdict: issue_found
  issues:
    - issue_id: gitlab.gl06.lp.empty_gravatar_avatar_anchor_without_name
      target:
        selector: 'main#content-body .avatar-holder > a[href*=''gravatar.com/avatar'']'
        description: the profile header external Gravatar avatar anchor element on the user projects page
        coverage_policy: single
      criterion:
        issue_family: link_purpose
        wcag_target: WCAG 2.4.4 Link Purpose (In Context)
      evidence_rule: >-
        The matched avatar anchor element has an empty accessible name. Its child image
        has empty `alt`, and no aria label, title, or description provides the
        external Gravatar link purpose.

    - issue_id: gitlab.gl06.lp.profile_rss_subscribe_anchor_without_target_context
      target:
        selector: 'main#content-body a[title=''Subscribe''][href*=''.atom''], main#content-body a[aria-label=''Subscribe''][href*=''.atom'']'
        description: the `Subscribe` RSS feed anchor element on the user projects page
        coverage_policy: single
      criterion:
        issue_family: link_purpose
        wcag_target: WCAG 2.4.4 Link Purpose (In Context)
      evidence_rule: >-
        The matched feed link is named only `Subscribe`. The name does not
        identify that the link subscribes to the Byte Blaze user feed, and the
        feed target is not provided as programmatically determined link context.
```

## Source And Live Check

- `gitlab-link-purpose-record.md` GL06 states that stable 6.2 Link Purpose failures include `Subscribe` and Gravatar/avatar-class failures; project-card numbers and avatars are kept PASS by title or same-list-item context.
- The clean atomic page anchor for GL06 is `gitlab.gl06.lp.empty_gravatar_avatar_anchor_without_name`; the same-page RSS `Subscribe` issue is filled here from source-record and live DOM review.
- Fresh live GL06 probe after refreshing GitLab auth found one visible profile Gravatar anchor element and one visible RSS `Subscribe` Atom-feed anchor element.

## Merge Scope

- L2 owner key: `gitlab + http://localhost:8023/users/byteblaze/projects + link_purpose + WCAG 2.4.4 Link Purpose (In Context)`.
- This merge instance should generate one L2 task for GL06 link purpose.
- The two entries in `gold.issues[]` preserve the GL06 source-record link-purpose failure groups confirmed on the live page.
