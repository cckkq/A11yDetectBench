# Merge Instance

```yaml
instance_id: reddit.f_relationship_advice_25599.link_purpose
task_level: level2
issue_present: true

source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: RD18
  review_status: source_and_live_checked

page:
  site: reddit
  page_name: Relationship Advice Comment Thread
  start_url: http://localhost:9999/f/relationship_advice/25599/update-my-f23-boyfriend-m33-just-left-me-in-europe-told-me
  auth_state_file: runtime_auth_state_placeholder.json

scope:
  issue_family: link_purpose
  wcag_target: WCAG 2.4.4 Link Purpose (In Context)
  assessment_requirement: L.2 Link Purpose

gold:
  expected_verdict: issue_found
  issues:
    - issue_id: reddit.rd18.lp.comment_count_link_without_post_context
      target:
        selector: 'a.text-sm[href=''/f/relationship_advice/25599/update-my-f23-boyfriend-m33-just-left-me-in-europe-told-me'']:has(> strong)'
        description: the `8 comments` link for the current relationship_advice submission
        coverage_policy: single
      criterion:
        issue_family: link_purpose
        wcag_target: WCAG 2.4.4 Link Purpose (In Context)
      evidence_rule: >-
        The matched link is named only `8 comments`. Its closest list-item context is
        only `8 comments`, with no ARIA or other programmatic binding to the current
        submission title.

    - issue_id: reddit.rd18.lp.comment_reply_without_comment_context
      target:
        selector: 'a.comment__reply-link[data-form-url]'
        description: the repeated `Reply` links in this relationship_advice comment thread
        coverage_policy: representative_group
      criterion:
        issue_family: link_purpose
        wcag_target: WCAG 2.4.4 Link Purpose (In Context)
      evidence_rule: >-
        The matched links are named only `Reply`. Each link's closest list-item
        context is only `Reply`, with no programmatic binding that identifies which
        comment the reply action belongs to.

    - issue_id: reddit.rd18.lp.comment_permalink_without_comment_context
      target:
        selector: 'a.comment__permalink[href*=''/comment/'']'
        description: the repeated `Permalink` links in this relationship_advice comment thread
        coverage_policy: representative_group
      criterion:
        issue_family: link_purpose
        wcag_target: WCAG 2.4.4 Link Purpose (In Context)
      evidence_rule: >-
        The matched links are named only `Permalink` and point to different comment
        permalink URLs. Each link's closest list-item context is only `Permalink`,
        with no programmatic binding that identifies the target comment.

    - issue_id: reddit.rd18.lp.comment_parent_without_comment_context
      target:
        selector: 'a.comment__parent-link[href*=''/comment/'']'
        description: the repeated `Parent` links in this relationship_advice comment thread
        coverage_policy: representative_group
      criterion:
        issue_family: link_purpose
        wcag_target: WCAG 2.4.4 Link Purpose (In Context)
      evidence_rule: >-
        The matched links are named only `Parent` and point to different parent
        comment targets. Each link's closest list-item context is only `Parent`,
        with no programmatic binding that identifies which parent comment will be
        opened.

```

## Source And Live Check

- `reddit-link-purpose-record.md` RD18 states that 6.2 Link Purpose fails on LP012 `8 comments`, eight `Reply` links, eight `Permalink` links, and three `Parent` links.
- The same RD18 record states `Nested` and `Linear` are current discussion view tabs and should not be included.
- The record states submission title, author/profile, forum, `Subscribe via RSS`, `Bans`, `Moderation log`, top navigation, skip, and footer links are purpose-clear.
- Fresh live RD18 probe after refreshing Reddit auth found one visible `8 comments` self-link, eight visible `a.comment__reply-link[data-form-url]` links, eight visible `a.comment__permalink[href*='/comment/']` links, and three visible `a.comment__parent-link[href*='/comment/']` links.
- The live probe found no `aria-label`, `aria-labelledby`, `aria-describedby`, `title`, or custom role on these target anchor elements.

## Merge Scope

- L2 owner key: `reddit + http://localhost:9999/f/relationship_advice/25599/update-my-f23-boyfriend-m33-just-left-me-in-europe-told-me + link_purpose + WCAG 2.4.4 Link Purpose (In Context)`.
- This merge instance should generate one L2 task for RD18 link purpose, not one L2 task per comment-action pattern.
- The four entries in `gold.issues[]` preserve all RD18 source-record link-purpose failure groups.
