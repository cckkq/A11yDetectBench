# Merge Instance

```yaml
instance_id: shopping.sales_order_history.link_purpose
task_level: level2
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
  issue_family: link_purpose
  wcag_target: WCAG 2.4.4 Link Purpose (In Context)
  assessment_requirement: L.2 Link Purpose

gold:
  expected_verdict: issue_found
  issues:
    - issue_id: shopping.p02.lp.order_view_order_without_row_header_context
      target:
        selector: 'table#my-orders-table a.action.view'
        description: the repeated `View Order` links in the order history table
        coverage_policy: representative_group
      criterion:
        issue_family: link_purpose
        wcag_target: WCAG 2.4.4 Link Purpose (In Context)
      evidence_rule: >-
        The matched links are named only `View Order` and point to different order
        detail URLs. Their action cells are associated only with the `Action` column
        header; the order numbers are ordinary sibling data cells without row-header,
        headers/id, or ARIA association to the links.

    - issue_id: shopping.p02.lp.order_reorder_without_row_header_context
      target:
        selector: 'table#my-orders-table a.action.order'
        description: the repeated `Reorder` links in the order history table
        coverage_policy: representative_group
      criterion:
        issue_family: link_purpose
        wcag_target: WCAG 2.4.4 Link Purpose (In Context)
      evidence_rule: >-
        The matched links are named only `Reorder`. Their action cells are associated
        only with the `Action` column header; the order ids are hidden in `data-post`
        values or ordinary sibling data cells, not in programmatically determined link
        context.

    - issue_id: shopping.p02.lp.recently_ordered_view_all_without_section_context
      target:
        selector: '.block-reorder a.action.view'
        description: the generic `View All` link in the Recently Ordered block
        coverage_policy: single
      criterion:
        issue_family: link_purpose
        wcag_target: WCAG 2.4.4 Link Purpose (In Context)
      evidence_rule: >-
        The matched link is named only `View All`. The visible `Recently Ordered`
        block title is not exposed through the link name, description, ARIA
        association, same sentence, same paragraph, same list item, or same table
        cell.

```

## Source And Live Check

- `shopping-link-purpose-record.md` P02 states that 6.2 Link Purpose fails on ten `View Order` links, ten `Reorder` links, and LP043 `View All` in the Recently Ordered block.
- The same P02 record states pagination links are PASS because their accessible names are `Page 2`, `Page 3`, and `Page 4`.
- The record states P02 had no visible/evaluated `Clear All` candidate in the source run; if compare state makes `Clear All` visible in another session, that belongs to a separate compare-state task, not this P02 source-record merge.
- Fresh live P02 probe after refreshing Shopping auth found ten visible `table#my-orders-table a.action.view` links, ten visible `table#my-orders-table a.action.order` links, and one visible `.block-reorder a.action.view` link.
- The live probe found no visible `#compare-clear-all`, `a#compare-clear-all`, or `.block-compare a.action.clear` target in this session.
- The live probe found no `aria-label`, `aria-labelledby`, `aria-describedby`, `title`, or custom role on the target anchor elements included in `gold.issues[]`.

## Merge Scope

- L2 owner key: `shopping + http://localhost:7770/sales/order/history/ + link_purpose + WCAG 2.4.4 Link Purpose (In Context)`.
- This merge instance should generate one L2 task for P02 link purpose, not one L2 task per atomic issue pattern.
- The three entries in `gold.issues[]` preserve all source-record failure groups for the current P02 source-record state.
