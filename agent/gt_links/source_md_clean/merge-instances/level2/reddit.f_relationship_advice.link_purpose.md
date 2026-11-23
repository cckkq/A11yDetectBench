# Merge Instance

```yaml
instance_id: reddit.f_relationship_advice.link_purpose
task_level: level2
issue_present: true

source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: RD17
  review_status: source_and_live_checked

page:
  site: reddit
  page_name: Relationship Advice Forum
  start_url: http://localhost:9999/f/relationship_advice
  auth_state_file: runtime_auth_state_placeholder.json

scope:
  issue_family: link_purpose
  wcag_target: WCAG 2.4.4 Link Purpose (In Context)
  assessment_requirement: L.2 Link Purpose

gold:
  expected_verdict: issue_found
  issues:
    - issue_id: reddit.rd17.lp.comment_count_link_without_post_context
      target:
        selector: 'article.submission a.text-sm[href^=''/f/'']:has(> strong)'
        description: the twenty-five per-submission comment-count links in the relationship_advice listing
        coverage_policy: representative_group
      criterion:
        issue_family: link_purpose
        wcag_target: WCAG 2.4.4 Link Purpose (In Context)
      evidence_rule: >-
        The matched links have names such as `N comments`. Each link navigates
        to a different submission/comment page, but the link name does not
        identify which post it belongs to, and the post title is not provided as
        programmatically determined link context.

    - issue_id: reddit.rd17.lp.generic_more_link_without_list_context
      target:
        selector: 'a.button[rel=''next'']'
        description: the `More` pagination anchor element at the bottom of the relationship_advice listing
        coverage_policy: single
      criterion:
        issue_family: link_purpose
        wcag_target: WCAG 2.4.4 Link Purpose (In Context)
      evidence_rule: >-
        The matched link name is only `More`. It does not programmatically
        identify that it continues or loads more items from the relationship_advice listing.
```

## Source And Live Check

- `reddit-link-purpose-record.md` RD17 states that the stable 6.2 Link Purpose failures are 25 per-submission comment-count links plus one `More` pagination link.
- The same source-record entry keeps `[deleted]` author/profile links, submission titles, authors/profile links, forum tabs, `Subscribe via RSS`, `Bans`, `Moderation log`, top navigation, skip links, and footer links as PASS.
- Fresh live RD17 probe after refreshing Reddit auth found 25 visible `article.submission a.text-sm[href^='/f/']:has(> strong)` links and one visible `a.button[rel='next']` link.
- The matched comment-count links have names such as `8 comments`, `142 comments`, and `88 comments`; the matched pagination link has text `More`.

## Merge Scope

- L2 owner key: `reddit + http://localhost:9999/f/relationship_advice + link_purpose + WCAG 2.4.4 Link Purpose (In Context)`.
- This merge instance should generate one L2 task for RD17 link purpose.
- The two entries in `gold.issues[]` preserve all RD17 source-record link-purpose failure groups already anchored by clean atomic issue instances.
