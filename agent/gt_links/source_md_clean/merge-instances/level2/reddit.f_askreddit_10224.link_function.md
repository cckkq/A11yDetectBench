# Merge Instance

```yaml
instance_id: reddit.f_askreddit_10224.link_function
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
  issue_family: link_function
  wcag_target: WCAG 4.1.2 Name, Role, Value
  assessment_requirement: L.1 Link Function

gold:
  expected_verdict: issue_found
  issues:
    - issue_id: reddit.rd15.lf.reply_anchor_inserts_form_without_widget_role
      target:
        selector: 'a.comment__reply-link[data-form-url]'
        description: the visible `Reply` anchor elements under comments in the AskReddit thread
        coverage_policy: representative_group
      criterion:
        issue_family: link_function
        wcag_target: WCAG 4.1.2 Name, Role, Value
      evidence_rule: >-
        The matched `Reply` anchor elements are exposed as links, but activating one
        inserts or reveals a reply form in place. The action does not navigate
        to link content, page location, or a resource.
```

## Source And Live Check

- `reddit-link-purpose-record.md` RD15 states that 6.1 Link Function fails on sixteen visible `Reply` anchor elements with `data-form-url` because they insert a reply form in place instead of navigating.
- The same RD15 record states `16 comments`, `Permalink`, `Parent`, author/profile links, `Nested`/`Linear`, top navigation, skip, sidebar, and footer links are navigation or view links and are not included as link-function failures.
- Fresh live RD15 probe after refreshing Reddit auth found sixteen visible `a.comment__reply-link[data-form-url]` anchor elements.
- The matched anchor elements have text `Reply`, hrefs pointing to comment URLs, and `data-form-url` values such as `/comment_form/AskReddit/10224/411494`.

## Merge Scope

- L2 owner key: `reddit + http://localhost:9999/f/AskReddit/10224/why-bleaching-your-butthole-isn-t-called-changing-your-ring + link_function + WCAG 4.1.2 Name, Role, Value`.
- This merge instance should generate one L2 task for RD15 link function.
- The single `gold.issues[]` entry preserves the RD15 source-record link-function failure group already anchored by a clean atomic issue instance.
