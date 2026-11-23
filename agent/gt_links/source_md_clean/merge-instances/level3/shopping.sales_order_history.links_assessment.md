# Merge Instance

```yaml
instance_id: shopping.sales_order_history.links_assessment
task_level: level3
issue_present: true
source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: P02
  review_status: source_and_live_checked
page:
  site: shopping
  page_name: Order History
  start_url: http://localhost:7770/sales/order/history/
  auth_state_file: runtime_auth_state_placeholder.json
scope:
  assessment_scope: Links L.1-L.2
gold:
  expected_verdict: issue_found
  issues:
  - issue_id: shopping.p02.lp.order_view_order_without_row_header_context
    target:
      selector: table#my-orders-table a.action.view
      description: the repeated `View Order` links in the order history table
      coverage_policy: representative_group
    criterion:
      issue_family: link_purpose
      wcag_target: WCAG 2.4.4 Link Purpose (In Context)
    evidence_rule: The matched links are named only `View Order` and point to different order detail URLs. Their action cells
      are associated only with the `Action` column header; the order numbers are ordinary sibling data cells without row-header,
      headers/id, or ARIA association to the links.
  - issue_id: shopping.p02.lp.order_reorder_without_row_header_context
    target:
      selector: table#my-orders-table a.action.order
      description: the repeated `Reorder` links in the order history table
      coverage_policy: representative_group
    criterion:
      issue_family: link_purpose
      wcag_target: WCAG 2.4.4 Link Purpose (In Context)
    evidence_rule: The matched links are named only `Reorder`. Their action cells are associated only with the `Action` column
      header; the order ids are hidden in `data-post` values or ordinary sibling data cells, not in programmatically determined
      link context.
  - issue_id: shopping.p02.lp.recently_ordered_view_all_without_section_context
    target:
      selector: .block-reorder a.action.view
      description: the generic `View All` link in the Recently Ordered block
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

- L3 owner key: `shopping + http://localhost:7770/sales/order/history/`.
- This merge instance should generate one L3 task for Links L.1-L.2 on this page.
- `gold.issues[]` contains 3 issues: 3 link_purpose.
- This L3 source file is authoritative for the L3 page-level inventory; it may include L3-only issues that are not part of Merge L2.
