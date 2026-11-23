# Merge Instance

```yaml
instance_id: reddit.f_news_comments.links_assessment
task_level: level3
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
  assessment_scope: Links L.1-L.2
gold:
  expected_verdict: issue_found
  issues:
  - issue_id: reddit.rd20.lf.reply_anchor_inserts_form_without_widget_role
    target:
      selector: a.comment__reply-link[data-form-url]
      description: the visible `Reply` anchor elements under comments in the news recent-comments listing
      coverage_policy: representative_group
    criterion:
      issue_family: link_function
      wcag_target: WCAG 4.1.2 Name, Role, Value
    evidence_rule: The matched `Reply` anchor elements are exposed as links, but activating one inserts or reveals a reply form in
      place. The action does not navigate to link content, page location, or a resource.
  - issue_id: reddit.rd20.lp.comment_reply_without_comment_context
    target:
      selector: a.comment__reply-link[data-form-url]
      description: the repeated `Reply` links in the news recent-comments listing
      coverage_policy: representative_group
    criterion:
      issue_family: link_purpose
      wcag_target: WCAG 2.4.4 Link Purpose (In Context)
    evidence_rule: The matched links are named only `Reply`. Each link's closest list-item context is only `Reply`, with no
      programmatic binding that identifies which comment the reply action belongs to.
  - issue_id: reddit.rd20.lp.comment_permalink_without_comment_context
    target:
      selector: a.comment__permalink[href*='/comment/']
      description: the repeated `Permalink` links in the news recent-comments listing
      coverage_policy: representative_group
    criterion:
      issue_family: link_purpose
      wcag_target: WCAG 2.4.4 Link Purpose (In Context)
    evidence_rule: The matched links are named only `Permalink` and point to different comment permalink URLs. Each link's
      closest list-item context is only `Permalink`, with no programmatic binding that identifies the target comment.
  - issue_id: reddit.rd20.lp.comment_parent_without_comment_context
    target:
      selector: a.comment__parent-link[href*='/comment/']
      description: the repeated `Parent` links in the news recent-comments listing
      coverage_policy: representative_group
    criterion:
      issue_family: link_purpose
      wcag_target: WCAG 2.4.4 Link Purpose (In Context)
    evidence_rule: The matched links are named only `Parent` and point to different parent comment targets. Each link's closest
      list-item context is only `Parent`, with no programmatic binding that identifies which parent comment will be opened.
  - issue_id: reddit.rd20.lp.generic_more_link_without_list_context
    target:
      selector: a.button[rel='next']
      description: the `More` pagination link at the bottom of the news recent-comments listing
      coverage_policy: single
    criterion:
      issue_family: link_purpose
      wcag_target: WCAG 2.4.4 Link Purpose (In Context)
    evidence_rule: The matched link is named only `More`. Its closest list-item and pagination context are also only `More`,
      with no programmatic label or description explaining that it opens more `/f/news/comments` items.
  - issue_id: reddit.rd20.lp.opaque_inline_external_link_text
    target:
      selector: a[href*='texastribune.org']
      description: the inline external link whose visible text is `as American as apple pie.`
      coverage_policy: single
    criterion:
      issue_family: link_purpose
      wcag_target: WCAG 2.4.4 Link Purpose (In Context)
    evidence_rule: The matched link text is `as American as apple pie.`. The text and same paragraph context do not identify
      the destination article or resource.
```

## Source And Live Check

- This L3 source may reuse reviewed L2 merge source files for the same page where applicable.
- The L3 YAML `gold.issues[]` in this file is the authoritative page-level Links L.1-L.2 inventory for this L3 benchmark unit.
- Current entries are retained from reviewed source records, live DOM checks, or reviewed L2 helper context as documented for this page.
- Coverage-gap observations are not included unless they are explicitly listed in `gold.issues[]`.

## Merge Scope

- L3 owner key: `reddit + http://localhost:9999/f/news/comments`.
- This merge instance should generate one L3 task for Links L.1-L.2 on this page.
- `gold.issues[]` contains 6 issues: 1 link_function and 5 link_purpose.
- This L3 source file is authoritative for the L3 page-level inventory; it may include L3-only issues that are not part of Merge L2.
