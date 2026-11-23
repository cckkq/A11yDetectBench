# Merge Instance

```yaml
instance_id: shopping.downloadable_customer_products.links_assessment
task_level: level3
issue_present: true
source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: P03
  review_status: source_and_live_checked
page:
  site: shopping
  page_name: Downloadable Products
  start_url: http://localhost:7770/downloadable/customer/products/
  auth_state_file: runtime_auth_state_placeholder.json
scope:
  assessment_scope: Links L.1-L.2
gold:
  expected_verdict: issue_found
  issues:
  - issue_id: shopping.p03.lp.generic_view_all_without_programmatic_context
    target:
      selector: .block-reorder a.action.view
      description: the `View All` anchor element in the Recently Ordered block
      coverage_policy: single
    criterion:
      issue_family: link_purpose
      wcag_target: WCAG 2.4.4 Link Purpose (In Context)
    evidence_rule: The matched link is named only `View All`. The visible `Recently Ordered` block title is not exposed through
      the link name, description, ARIA association, same sentence, same paragraph, same list item, or same table cell.
```

## Source And Live Check

- This L3 source may reuse reviewed L2 merge source files for the same page where applicable.
- The L3 YAML `gold.issues[]` in this file is the authoritative page-level Links L.1-L.2 inventory for this L3 benchmark unit.
- Current entries are retained from reviewed source records, live DOM checks, or reviewed L2 helper context as documented for this page.
- Coverage-gap observations are not included unless they are explicitly listed in `gold.issues[]`.

## Merge Scope

- L3 owner key: `shopping + http://localhost:7770/downloadable/customer/products/`.
- This merge instance should generate one L3 task for Links L.1-L.2 on this page.
- `gold.issues[]` contains 1 issue: 1 link_purpose.
- This L3 source file is authoritative for the L3 page-level inventory; it may include L3-only issues that are not part of Merge L2.
