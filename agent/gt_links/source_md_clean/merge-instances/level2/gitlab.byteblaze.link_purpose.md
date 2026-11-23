# Merge Instance

```yaml
instance_id: gitlab.byteblaze.link_purpose
task_level: level2
issue_present: true

source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: GL02
  review_status: source_and_live_checked

page:
  site: gitlab
  page_name: User Profile
  start_url: http://localhost:8023/byteblaze
  auth_state_file: runtime_auth_state_placeholder.json

scope:
  issue_family: link_purpose
  wcag_target: WCAG 2.4.4 Link Purpose (In Context)
  assessment_requirement: L.2 Link Purpose

gold:
  expected_verdict: issue_found
  issues:
    - issue_id: gitlab.gl02.lp.profile_rss_subscribe_anchor_without_target_context
      target:
        selector: 'main#content-body a[title=''Subscribe''][href*=''.atom'']'
        description: the `Subscribe` RSS feed anchor element on the user profile page
        coverage_policy: single
      criterion:
        issue_family: link_purpose
        wcag_target: WCAG 2.4.4 Link Purpose (In Context)
      evidence_rule: >-
        The matched link has computed name `Subscribe` and no description. The
        name does not identify that the link subscribes to the Byte Blaze user feed.

    - issue_id: gitlab.gl02.lp.empty_gravatar_avatar_anchor_without_name
      target:
        selector: 'main#content-body a[href*=''gravatar.com/avatar'']:has(img[alt=''''])'
        description: the external Gravatar profile avatar link with an empty image alt
        coverage_policy: single
      criterion:
        issue_family: link_purpose
        wcag_target: WCAG 2.4.4 Link Purpose (In Context)
      evidence_rule: >-
        The matched profile avatar link has no text, no accessible name, and an
        image with empty `alt`. Its purpose cannot be determined from the link name
        or a programmatically associated context.

    - issue_id: gitlab.gl02.lp.dashboard_projects_view_all_without_section_context
      target:
        selector: 'main#content-body a.js-view-all[href=''/users/byteblaze/projects'']'
        description: the `View all` anchor element in the projects overview section
        coverage_policy: single
      criterion:
        issue_family: link_purpose
        wcag_target: WCAG 2.4.4 Link Purpose (In Context)
      evidence_rule: >-
        The matched link has computed name `View all` and no description. Its link
        name does not identify the projects destination, and the visual `Personal
        projects` heading is not supplied as programmatically determined link context.

```

## Source And Live Check

- `gitlab-link-purpose-record.md` GL02 states that stable 6.2 Link Purpose failures include `Subscribe`, a Gravatar empty-name link, and a generic `View all` link.
- Fresh live GL02 probe after refreshing GitLab auth found one visible `main#content-body a[title='Subscribe'][href*='.atom']` link, one visible external `gravatar.com/avatar` link with `img[alt='']`, and one visible `main#content-body a.js-view-all[href='/users/byteblaze/projects']` link.
- The same live probe found another empty-alt project-card avatar link, but source-record GL02 treats project-card avatar context separately and does not list it as this page's stable failure group.
- The live probe found no `aria-label`, `aria-labelledby`, `aria-describedby`, or custom role on the target anchor elements included in `gold.issues[]`.
- GL02 also has 6.1 topbar dropdown failures, but this merge instance records only 6.2 link-purpose evidence.

## Merge Scope

- L2 owner key: `gitlab + http://localhost:8023/byteblaze + link_purpose + WCAG 2.4.4 Link Purpose (In Context)`.
- This merge instance should generate one L2 task for GL02 link purpose, not one L2 task per profile-page pattern.
- The three entries in `gold.issues[]` preserve the GL02 source-record stable link-purpose failure groups confirmed on the live page.
