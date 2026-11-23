# Merge Instance

```yaml
instance_id: reddit.f_relationship_advice.links_assessment
task_level: level3
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
  assessment_scope: Links L.1-L.2
gold:
  expected_verdict: issue_found
  issues:
  - issue_id: reddit.rd17.lp.comment_count_link_without_post_context
    target:
      selector: article.submission a.text-sm[href^='/f/']:has(> strong)
      description: the twenty-five per-submission comment-count links in the relationship_advice listing
      coverage_policy: representative_group
    criterion:
      issue_family: link_purpose
      wcag_target: WCAG 2.4.4 Link Purpose (In Context)
    evidence_rule: The matched links have names such as `N comments`. Each link navigates to a different submission/comment
      page, but the link name does not identify which post it belongs to, and the post title is not provided as programmatically
      determined link context.
  - issue_id: reddit.rd17.lp.generic_more_link_without_list_context
    target:
      selector: a.button[rel='next']
      description: the `More` pagination anchor element at the bottom of the relationship_advice listing
      coverage_policy: single
    criterion:
      issue_family: link_purpose
      wcag_target: WCAG 2.4.4 Link Purpose (In Context)
    evidence_rule: The matched link name is only `More`. It does not programmatically identify that it continues or loads
      more items from the relationship_advice listing.
```

## Source And Live Check

- This L3 source may reuse reviewed L2 merge source files for the same page where applicable.
- The L3 YAML `gold.issues[]` in this file is the authoritative page-level Links L.1-L.2 inventory for this L3 benchmark unit.
- Current entries are retained from reviewed source records, live DOM checks, or reviewed L2 helper context as documented for this page.
- Coverage-gap observations are not included unless they are explicitly listed in `gold.issues[]`.

## Merge Scope

- L3 owner key: `reddit + http://localhost:9999/f/relationship_advice`.
- This merge instance should generate one L3 task for Links L.1-L.2 on this page.
- `gold.issues[]` contains 2 issues: 2 link_purpose.
- This L3 source file is authoritative for the L3 page-level inventory; it may include L3-only issues that are not part of Merge L2.
