# Merge Instance

```yaml
instance_id: reddit.user_marvelsgrantman136.links_assessment
task_level: level3
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
  assessment_scope: Links L.1-L.2
gold:
  expected_verdict: issue_found
  issues:
  - issue_id: reddit.rd10.lf.reply_anchor_inserts_form_without_widget_role
    target:
      selector: a.comment__reply-link[data-form-url]
      description: the single `Reply` anchor element in the user profile comment activity item
      coverage_policy: single
    criterion:
      issue_family: link_function
      wcag_target: WCAG 4.1.2 Name, Role, Value
    evidence_rule: The matched `Reply` anchor element is exposed as a link, but activating it inserts or reveals a reply form in place.
      The action does not navigate to link content, page location, or a resource.
  - issue_id: reddit.rd10.lp.edit_links_without_submission_or_comment_context
    target:
      selector: article a[href$='/edit'][href^='/']
      description: the repeated submission and comment `Edit` links in the user profile activity list
      coverage_policy: representative_group
    criterion:
      issue_family: link_purpose
      wcag_target: WCAG 2.4.4 Link Purpose (In Context)
    evidence_rule: The matched links are named only `Edit` and point to different submission or comment edit URLs. Each link's
      closest list-item context is only `Edit`, with no programmatic binding to the relevant post or comment.
  - issue_id: reddit.rd10.lp.comment_count_link_without_post_context
    target:
      selector: article.submission a.text-sm[href^='/f/']:has(> strong)
      description: the `No comments` and `N comments` links in the user profile post listing
      coverage_policy: representative_group
    criterion:
      issue_family: link_purpose
      wcag_target: WCAG 2.4.4 Link Purpose (In Context)
    evidence_rule: The matched links have names such as `No comments` or `N comments`. Each link navigates to a different
      submission/comment page, but the link name does not identify which post it belongs to, and the post title is not provided
      as programmatically determined link context.
  - issue_id: reddit.rd10.lp.comment_reply_without_comment_context
    target:
      selector: a.comment__reply-link[data-form-url]
      description: the single `Reply` link in the user profile comment activity item
      coverage_policy: single
    criterion:
      issue_family: link_purpose
      wcag_target: WCAG 2.4.4 Link Purpose (In Context)
    evidence_rule: The matched link is named only `Reply`. Its closest list-item context is only `Reply`, with no programmatic
      binding that identifies which comment the reply action belongs to.
  - issue_id: reddit.rd10.lp.comment_permalink_without_comment_context
    target:
      selector: a.comment__permalink[href*='/comment/']
      description: the single `Permalink` link in the user profile comment activity item
      coverage_policy: single
    criterion:
      issue_family: link_purpose
      wcag_target: WCAG 2.4.4 Link Purpose (In Context)
    evidence_rule: The matched link is named only `Permalink` and points to a comment permalink URL. Its closest list-item
      context is only `Permalink`, with no programmatic binding that identifies the target comment.
  - issue_id: reddit.rd10.lp.generic_more_link_without_list_context
    target:
      selector: a.button[rel='next']
      description: the `More` pagination link at the bottom of the user profile activity list
      coverage_policy: single
    criterion:
      issue_family: link_purpose
      wcag_target: WCAG 2.4.4 Link Purpose (In Context)
    evidence_rule: The matched link is named only `More`. Its closest list-item and pagination context are also only `More`,
      with no programmatic label or description explaining that it opens more user profile activity.
```

## Source And Live Check

- This L3 source may reuse reviewed L2 merge source files for the same page where applicable.
- The L3 YAML `gold.issues[]` in this file is the authoritative page-level Links L.1-L.2 inventory for this L3 benchmark unit.
- Current entries are retained from reviewed source records, live DOM checks, or reviewed L2 helper context as documented for this page.
- Coverage-gap observations are not included unless they are explicitly listed in `gold.issues[]`.

## Merge Scope

- L3 owner key: `reddit + http://localhost:9999/user/MarvelsGrantMan136`.
- This merge instance should generate one L3 task for Links L.1-L.2 on this page.
- `gold.issues[]` contains 6 issues: 1 link_function and 5 link_purpose.
- This L3 source file is authoritative for the L3 page-level inventory; it may include L3-only issues that are not part of Merge L2.
