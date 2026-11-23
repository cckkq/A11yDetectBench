# Merge Instance

```yaml
instance_id: shopping_admin.admin_sales_order_status.link_purpose
task_level: level2
issue_present: true

source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: PA61
  review_status: source_and_live_checked

page:
  site: shopping_admin
  page_name: Order Status
  start_url: http://localhost:7780/admin/sales/order_status/
  auth_state_file: runtime_auth_state_placeholder.json

scope:
  issue_family: link_purpose
  wcag_target: WCAG 2.4.4 Link Purpose (In Context)
  assessment_requirement: L.2 Link Purpose

gold:
  expected_verdict: issue_found
  issues:
    - issue_id: shopping_admin.pa61.lp.order_status_unassign_without_row_context
      target:
        selector: '#sales_order_status_grid_table a[href=''#''][data-post*=''unassign'']'
        description: the ten `Unassign` action links in the order status grid
        coverage_policy: representative_group
      criterion:
        issue_family: link_purpose
        wcag_target: WCAG 2.4.4 Link Purpose (In Context)
      evidence_rule: >-
        The matched links all have the accessible name `Unassign` and no
        programmatically associated status/state context. The action cell text
        is only `Unassign`, the `Action` header is not bound with `headers` or
        `scope`, and the status/state values in sibling cells or `data-post` are
        not part of the link name or a valid programmatic context.
```

## Source And Live Check

- `shopping-admin-link-purpose-record.md` PA61 states that the stable 6.2 Link Purpose failures are ten order-status table `Unassign` links, LP015-LP024.
- The same source-record entry flips `admin` and footer `Magento` to PASS and does not include the left navigation disclosure anchor elements in 6.2.
- Fresh live PA61 probe after refreshing Shopping Admin auth found ten visible `#sales_order_status_grid_table a[href='#'][data-post*='unassign']` links.
- The matched anchor elements all have text `Unassign`, `href='#'`, no `aria-label`, no `aria-labelledby`, no `aria-describedby`, no `title`, no `role`, and a `data-post` payload for a different status/state pair.
- PA61 also has 6.1 link-function failures on left navigation disclosures and these `Unassign` command links, but this merge instance records only the 6.2 link-purpose evidence.

## Merge Scope

- L2 owner key: `shopping_admin + http://localhost:7780/admin/sales/order_status/ + link_purpose + WCAG 2.4.4 Link Purpose (In Context)`.
- This merge instance should generate one L2 task for PA61 link purpose.
- The single `gold.issues[]` entry represents the source-record stable group of ten order-status `Unassign` link-purpose failures.
