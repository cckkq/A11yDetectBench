# Merge Instance

```yaml
instance_id: reddit.comments.link_purpose
task_level: level2
issue_present: true

source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: RD06
  review_status: source_and_live_checked

page:
  site: reddit
  page_name: Recent Comments
  start_url: http://localhost:9999/comments
  auth_state_file: runtime_auth_state_placeholder.json

scope:
  issue_family: link_purpose
  wcag_target: WCAG 2.4.4 Link Purpose (In Context)
  assessment_requirement: L.2 Link Purpose

gold:
  expected_verdict: issue_found
  issues:
    - issue_id: reddit.rd06.lp.comment_reply_without_comment_context
      target:
        selector: 'a.comment__reply-link[data-form-url]'
        description: the repeated `Reply` links in Recent comments action rows
        coverage_policy: representative_group
      criterion:
        issue_family: link_purpose
        wcag_target: WCAG 2.4.4 Link Purpose (In Context)
      evidence_rule: >-
        The matched links are named only `Reply` and point to different comment
        reply targets. Each link's closest list-item context is only `Reply`, with
        no `aria-label`, `title`, `aria-labelledby`, or `aria-describedby` binding
        that identifies which comment the reply action belongs to.

    - issue_id: reddit.rd06.lp.comment_permalink_without_comment_context
      target:
        selector: 'a.comment__permalink'
        description: the repeated `Permalink` links in Recent comments action rows
        coverage_policy: representative_group
      criterion:
        issue_family: link_purpose
        wcag_target: WCAG 2.4.4 Link Purpose (In Context)
      evidence_rule: >-
        The matched links are named only `Permalink` and point to different comment
        permalink URLs. Each link's closest list-item context is only `Permalink`,
        with no programmatic binding that identifies the target comment.

    - issue_id: reddit.rd06.lp.comment_parent_without_comment_context
      target:
        selector: 'a.comment__parent-link'
        description: the repeated `Parent` links in Recent comments action rows
        coverage_policy: representative_group
      criterion:
        issue_family: link_purpose
        wcag_target: WCAG 2.4.4 Link Purpose (In Context)
      evidence_rule: >-
        The matched links are named only `Parent` and point to different parent
        comment targets. Each link's closest list-item context is only `Parent`,
        with no programmatic binding that identifies which parent comment will be
        opened.

    - issue_id: reddit.rd06.lp.generic_more_link_without_list_context
      target:
        selector: 'nav.pagination a[rel=next]'
        description: the generic `More` pagination link at the bottom of Recent comments
        coverage_policy: single
      criterion:
        issue_family: link_purpose
        wcag_target: WCAG 2.4.4 Link Purpose (In Context)
      evidence_rule: >-
        The matched link is named only `More`. Its closest list-item and pagination
        context are also only `More`, with no programmatic label or description
        explaining that it opens more Recent comments.

```

## Source And Live Check

- `reddit-link-purpose-record.md` RD06 states that 6.2 Link Purpose fails on 25 `Reply` links, 25 `Permalink` links, 12 `Parent` links, and LP160 `More`.
- The same RD06 record states `[deleted]` author/profile links are not included because their link name corresponds to the displayed author identifier.
- The record states other usernames, post titles, `Reply to ... in ... by ...`, skip, top navigation, and footer links are purpose-clear.
- Fresh live RD06 probe after refreshing Reddit auth found 25 visible `a.comment__reply-link[data-form-url]` links, 25 visible `a.comment__permalink` links, 12 visible `a.comment__parent-link` links, and one visible `nav.pagination a[rel=next]` link.
- The live probe found no `aria-label`, `aria-labelledby`, `aria-describedby`, `title`, or custom role on the target anchor elements included in `gold.issues[]`.
- RD06 `Reply` is also a 6.1 link-function failure in the source record, but this L2 merge instance only records the 6.2 link-purpose failure evidence.

## Merge Scope

- L2 owner key: `reddit + http://localhost:9999/comments + link_purpose + WCAG 2.4.4 Link Purpose (In Context)`.
- This merge instance should generate one L2 task for RD06 link purpose, not one L2 task per comment-action pattern.
- The four entries in `gold.issues[]` preserve all RD06 source-record link-purpose failure groups.
