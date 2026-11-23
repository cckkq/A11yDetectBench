# Merge Instance

```yaml
instance_id: reddit.f_news_comments.link_purpose
task_level: level2
issue_present: true

source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: RD20
  review_status: source_and_live_checked

page:
  site: reddit
  page_name: News Comments
  start_url: http://localhost:9999/f/news/comments
  auth_state_file: runtime_auth_state_placeholder.json

scope:
  issue_family: link_purpose
  wcag_target: WCAG 2.4.4 Link Purpose (In Context)
  assessment_requirement: L.2 Link Purpose

gold:
  expected_verdict: issue_found
  issues:
    - issue_id: reddit.rd20.lp.comment_reply_without_comment_context
      target:
        selector: 'a.comment__reply-link[data-form-url]'
        description: the repeated `Reply` links in the news recent-comments listing
        coverage_policy: representative_group
      criterion:
        issue_family: link_purpose
        wcag_target: WCAG 2.4.4 Link Purpose (In Context)
      evidence_rule: >-
        The matched links are named only `Reply`. Each link's closest list-item
        context is only `Reply`, with no programmatic binding that identifies
        which comment the reply action belongs to.

    - issue_id: reddit.rd20.lp.comment_permalink_without_comment_context
      target:
        selector: 'a.comment__permalink[href*=''/comment/'']'
        description: the repeated `Permalink` links in the news recent-comments listing
        coverage_policy: representative_group
      criterion:
        issue_family: link_purpose
        wcag_target: WCAG 2.4.4 Link Purpose (In Context)
      evidence_rule: >-
        The matched links are named only `Permalink` and point to different
        comment permalink URLs. Each link's closest list-item context is only
        `Permalink`, with no programmatic binding that identifies the target
        comment.

    - issue_id: reddit.rd20.lp.comment_parent_without_comment_context
      target:
        selector: 'a.comment__parent-link[href*=''/comment/'']'
        description: the repeated `Parent` links in the news recent-comments listing
        coverage_policy: representative_group
      criterion:
        issue_family: link_purpose
        wcag_target: WCAG 2.4.4 Link Purpose (In Context)
      evidence_rule: >-
        The matched links are named only `Parent` and point to different parent
        comment targets. Each link's closest list-item context is only `Parent`,
        with no programmatic binding that identifies which parent comment will
        be opened.

    - issue_id: reddit.rd20.lp.generic_more_link_without_list_context
      target:
        selector: 'a.button[rel=''next'']'
        description: the `More` pagination link at the bottom of the news recent-comments listing
        coverage_policy: single
      criterion:
        issue_family: link_purpose
        wcag_target: WCAG 2.4.4 Link Purpose (In Context)
      evidence_rule: >-
        The matched link is named only `More`. Its closest list-item and
        pagination context are also only `More`, with no programmatic label or
        description explaining that it opens more `/f/news/comments` items.

    - issue_id: reddit.rd20.lp.opaque_inline_external_link_text
      target:
        selector: 'a[href*=''texastribune.org'']'
        description: the inline external link whose visible text is `as American as apple pie.`
        coverage_policy: single
      criterion:
        issue_family: link_purpose
        wcag_target: WCAG 2.4.4 Link Purpose (In Context)
      evidence_rule: >-
        The matched link text is `as American as apple pie.`. The text and same
        paragraph context do not identify the destination article or resource.
```

## Source And Live Check

- `reddit-link-purpose-record.md` RD20 states that 6.2 Link Purpose fails on 25 `Reply` links, 25 `Permalink` links, 15 `Parent` links, LP167 `More`, and LP050 `as American as apple pie.`.
- The same RD20 record states `[deleted]` author/profile links, repeated post titles, author/profile links, forum links, top navigation, skip links, and footer links are purpose-clear.
- Fresh live RD20 probe after refreshing Reddit auth found 25 visible `a.comment__reply-link[data-form-url]` links, 25 visible `a.comment__permalink[href*='/comment/']` links, 15 visible `a.comment__parent-link[href*='/comment/']` links, one visible `a.button[rel='next']` link, and one visible `a[href*='texastribune.org']` link.
- The live probe confirmed the external link text is `as American as apple pie.` and the href points to `https://www.texastribune.org/2022/11/10/indian-child-adoption-scotus/`.

## Merge Scope

- L2 owner key: `reddit + http://localhost:9999/f/news/comments + link_purpose + WCAG 2.4.4 Link Purpose (In Context)`.
- This merge instance should generate one L2 task for RD20 link purpose, not one L2 task per comment-action pattern.
- The five entries in `gold.issues[]` preserve all RD20 source-record link-purpose failure groups confirmed on the live page.
