# Merge Instance

```yaml
instance_id: reddit.f_askreddit_10224.link_purpose
task_level: level2
issue_present: true

source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: RD15
  review_status: source_and_live_checked

page:
  site: reddit
  page_name: AskReddit Comment Thread
  start_url: http://localhost:9999/f/AskReddit/10224/why-bleaching-your-butthole-isn-t-called-changing-your-ring
  auth_state_file: runtime_auth_state_placeholder.json

scope:
  issue_family: link_purpose
  wcag_target: WCAG 2.4.4 Link Purpose (In Context)
  assessment_requirement: L.2 Link Purpose

gold:
  expected_verdict: issue_found
  issues:
    - issue_id: reddit.rd15.lp.comment_count_link_without_post_context
      target:
        selector: 'a.text-sm[href=''/f/AskReddit/10224/why-bleaching-your-butthole-isn-t-called-changing-your-ring'']:has(> strong)'
        description: the `16 comments` link for the current AskReddit submission
        coverage_policy: single
      criterion:
        issue_family: link_purpose
        wcag_target: WCAG 2.4.4 Link Purpose (In Context)
      evidence_rule: >-
        The matched link is named only `16 comments`. Its closest list-item
        context is only `16 comments`, with no ARIA or other programmatic
        binding to the current submission title.

    - issue_id: reddit.rd15.lp.comment_reply_without_comment_context
      target:
        selector: 'a.comment__reply-link[data-form-url]'
        description: the repeated `Reply` links in this AskReddit comment thread
        coverage_policy: representative_group
      criterion:
        issue_family: link_purpose
        wcag_target: WCAG 2.4.4 Link Purpose (In Context)
      evidence_rule: >-
        The matched links are named only `Reply`. Each link's closest list-item
        context is only `Reply`, with no programmatic binding that identifies
        which comment the reply action belongs to.

    - issue_id: reddit.rd15.lp.comment_permalink_without_comment_context
      target:
        selector: 'a.comment__permalink[href*=''/comment/'']'
        description: the repeated `Permalink` links in this AskReddit comment thread
        coverage_policy: representative_group
      criterion:
        issue_family: link_purpose
        wcag_target: WCAG 2.4.4 Link Purpose (In Context)
      evidence_rule: >-
        The matched links are named only `Permalink` and point to different
        comment permalink URLs. Each link's closest list-item context is only
        `Permalink`, with no programmatic binding that identifies the target
        comment.

    - issue_id: reddit.rd15.lp.comment_parent_without_comment_context
      target:
        selector: 'a.comment__parent-link[href*=''/comment/'']'
        description: the repeated `Parent` links in this AskReddit comment thread
        coverage_policy: representative_group
      criterion:
        issue_family: link_purpose
        wcag_target: WCAG 2.4.4 Link Purpose (In Context)
      evidence_rule: >-
        The matched links are named only `Parent` and point to different parent
        comment targets. Each link's closest list-item context is only `Parent`,
        with no programmatic binding that identifies which parent comment will
        be opened.
```

## Source And Live Check

- `reddit-link-purpose-record.md` RD15 states that 6.2 Link Purpose fails on LP012 `16 comments`, sixteen `Reply` links, sixteen `Permalink` links, and two `Parent` links.
- The same RD15 record states `[deleted]` author/profile links, the submission title, author/profile links, forum link, `Nested`/`Linear` view links, `Subscribe via RSS`, `Bans`, `Moderation log`, top navigation, skip links, and footer links are purpose-clear.
- Fresh live RD15 probe after refreshing Reddit auth found one visible `16 comments` self-link, sixteen visible `a.comment__reply-link[data-form-url]` links, sixteen visible `a.comment__permalink[href*='/comment/']` links, and two visible `a.comment__parent-link[href*='/comment/']` links.
- The live probe found no `aria-label`, `aria-labelledby`, `aria-describedby`, `title`, or custom role on these target anchor elements.

## Merge Scope

- L2 owner key: `reddit + http://localhost:9999/f/AskReddit/10224/why-bleaching-your-butthole-isn-t-called-changing-your-ring + link_purpose + WCAG 2.4.4 Link Purpose (In Context)`.
- This merge instance should generate one L2 task for RD15 link purpose, not one L2 task per comment-action pattern.
- The four entries in `gold.issues[]` preserve all RD15 source-record link-purpose failure groups confirmed on the live page.
