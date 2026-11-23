# Merge Instance

```yaml
instance_id: reddit.f_news_comments.link_function
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
  issue_family: link_function
  wcag_target: WCAG 4.1.2 Name, Role, Value
  assessment_requirement: L.1 Link Function

gold:
  expected_verdict: issue_found
  issues:
    - issue_id: reddit.rd20.lf.reply_anchor_inserts_form_without_widget_role
      target:
        selector: 'a.comment__reply-link[data-form-url]'
        description: the visible `Reply` anchor elements under comments in the news recent-comments listing
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

- `reddit-link-purpose-record.md` RD20 states that 6.1 Link Function fails on 25 visible `Reply` anchor elements with `data-form-url` because they insert a reply form in place instead of navigating.
- The same RD20 record states `Permalink`, `Parent`, `More`, the inline external link, author/profile links, post titles, top navigation, skip links, sidebar, and footer links are navigation, resource, or pagination links and are not included as link-function failures.
- Fresh live RD20 probe after refreshing Reddit auth found 25 visible `a.comment__reply-link[data-form-url]` anchor elements.
- The matched anchor elements have text `Reply`, hrefs pointing to comment URLs, and `data-form-url` values such as `/comment_form/news/129492/2561477`.

## Merge Scope

- L2 owner key: `reddit + http://localhost:9999/f/news/comments + link_function + WCAG 4.1.2 Name, Role, Value`.
- This merge instance should generate one L2 task for RD20 link function.
- The single `gold.issues[]` entry preserves the RD20 source-record link-function failure group confirmed on the live page.
