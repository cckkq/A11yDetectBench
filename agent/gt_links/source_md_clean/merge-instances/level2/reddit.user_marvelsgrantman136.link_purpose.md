# Merge Instance

```yaml
instance_id: reddit.user_marvelsgrantman136.link_purpose
task_level: level2
issue_present: true

source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: RD10
  review_status: source_and_live_checked

page:
  site: reddit
  page_name: User Profile
  start_url: http://localhost:9999/user/MarvelsGrantMan136
  auth_state_file: runtime_auth_state_placeholder.json

scope:
  issue_family: link_purpose
  wcag_target: WCAG 2.4.4 Link Purpose (In Context)
  assessment_requirement: L.2 Link Purpose

gold:
  expected_verdict: issue_found
  issues:
    - issue_id: reddit.rd10.lp.edit_links_without_submission_or_comment_context
      target:
        selector: 'article a[href$=''/edit''][href^=''/'']'
        description: the repeated submission and comment `Edit` links in the user profile activity list
        coverage_policy: representative_group
      criterion:
        issue_family: link_purpose
        wcag_target: WCAG 2.4.4 Link Purpose (In Context)
      evidence_rule: >-
        The matched links are named only `Edit` and point to different
        submission or comment edit URLs. Each link's closest list-item context
        is only `Edit`, with no programmatic binding to the relevant post or
        comment.

    - issue_id: reddit.rd10.lp.comment_count_link_without_post_context
      target:
        selector: 'article.submission a.text-sm[href^=''/f/'']:has(> strong)'
        description: the `No comments` and `N comments` links in the user profile post listing
        coverage_policy: representative_group
      criterion:
        issue_family: link_purpose
        wcag_target: WCAG 2.4.4 Link Purpose (In Context)
      evidence_rule: >-
        The matched links have names such as `No comments` or `N comments`.
        Each link navigates to a different submission/comment page, but the link
        name does not identify which post it belongs to, and the post title is
        not provided as programmatically determined link context.

    - issue_id: reddit.rd10.lp.comment_reply_without_comment_context
      target:
        selector: 'a.comment__reply-link[data-form-url]'
        description: the single `Reply` link in the user profile comment activity item
        coverage_policy: single
      criterion:
        issue_family: link_purpose
        wcag_target: WCAG 2.4.4 Link Purpose (In Context)
      evidence_rule: >-
        The matched link is named only `Reply`. Its closest list-item context is
        only `Reply`, with no programmatic binding that identifies which comment
        the reply action belongs to.

    - issue_id: reddit.rd10.lp.comment_permalink_without_comment_context
      target:
        selector: 'a.comment__permalink[href*=''/comment/'']'
        description: the single `Permalink` link in the user profile comment activity item
        coverage_policy: single
      criterion:
        issue_family: link_purpose
        wcag_target: WCAG 2.4.4 Link Purpose (In Context)
      evidence_rule: >-
        The matched link is named only `Permalink` and points to a comment
        permalink URL. Its closest list-item context is only `Permalink`, with
        no programmatic binding that identifies the target comment.

    - issue_id: reddit.rd10.lp.generic_more_link_without_list_context
      target:
        selector: 'a.button[rel=''next'']'
        description: the `More` pagination link at the bottom of the user profile activity list
        coverage_policy: single
      criterion:
        issue_family: link_purpose
        wcag_target: WCAG 2.4.4 Link Purpose (In Context)
      evidence_rule: >-
        The matched link is named only `More`. Its closest list-item and
        pagination context are also only `More`, with no programmatic label or
        description explaining that it opens more user profile activity.
```

## Source And Live Check

- `reddit-link-purpose-record.md` RD10 states that 6.2 Link Purpose fails on 25 `Edit` links, 24 per-submission comment-count/status links, one `Reply`, one `Permalink`, and one `More` link.
- The same RD10 record states user/profile links, forum links, source-domain search links, post titles, `Overview`/`Submissions`/`Comments` tabs, skip links, top navigation, and footer links are purpose-clear.
- Fresh live RD10 probe after refreshing Reddit auth found 25 visible `article a[href$='/edit'][href^='/']` links. The broader `a[href*='/edit'][href^='/']` selector also matched `Edit biography`, which is not part of the source-record failure group, so it is intentionally excluded.
- The same live probe found 24 visible `article.submission a.text-sm[href^='/f/']:has(> strong)` links, one visible `a.comment__reply-link[data-form-url]`, one visible `a.comment__permalink[href*='/comment/']`, and one visible `a.button[rel='next']` link.

## Merge Scope

- L2 owner key: `reddit + http://localhost:9999/user/MarvelsGrantMan136 + link_purpose + WCAG 2.4.4 Link Purpose (In Context)`.
- This merge instance should generate one L2 task for RD10 link purpose, not one L2 task per activity-link pattern.
- The five entries in `gold.issues[]` preserve all RD10 source-record link-purpose failure groups confirmed on the live page.
