# Merge Instance

```yaml
instance_id: reddit.user_marvelsgrantman136.link_function
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
  issue_family: link_function
  wcag_target: WCAG 4.1.2 Name, Role, Value
  assessment_requirement: L.1 Link Function

gold:
  expected_verdict: issue_found
  issues:
    - issue_id: reddit.rd10.lf.reply_anchor_inserts_form_without_widget_role
      target:
        selector: 'a.comment__reply-link[data-form-url]'
        description: the single `Reply` anchor element in the user profile comment activity item
        coverage_policy: single
      criterion:
        issue_family: link_function
        wcag_target: WCAG 4.1.2 Name, Role, Value
      evidence_rule: >-
        The matched `Reply` anchor element is exposed as a link, but activating it
        inserts or reveals a reply form in place. The action does not navigate
        to link content, page location, or a resource.
```

## Source And Live Check

- `reddit-link-purpose-record.md` RD10 states that 6.1 Link Function fails on one comment `Reply` link with `data-form-url` because it inserts a reply form in place instead of navigating.
- The same RD10 record states submission/comment `Edit`, `Permalink`, comment-count links, `More`, post titles, author/profile links, body external links, top navigation, main tabs, and footer links are navigation or resource links and are not included as link-function failures.
- Fresh live RD10 probe after refreshing Reddit auth found one visible `a.comment__reply-link[data-form-url]` anchor element.
- The matched anchor element has text `Reply`, href `/f/television/134942/-/comment/2402719`, and `data-form-url=/comment_form/television/134942/2402719`.

## Merge Scope

- L2 owner key: `reddit + http://localhost:9999/user/MarvelsGrantMan136 + link_function + WCAG 4.1.2 Name, Role, Value`.
- This merge instance should generate one L2 task for RD10 link function.
- The single `gold.issues[]` entry preserves the RD10 source-record link-function failure group confirmed on the live page.
