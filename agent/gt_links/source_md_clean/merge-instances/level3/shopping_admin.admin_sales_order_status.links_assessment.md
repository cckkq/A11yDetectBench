# Merge Instance

```yaml
instance_id: shopping_admin.admin_sales_order_status.links_assessment
task_level: level3
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
  assessment_scope: Links L.1-L.2
gold:
  expected_verdict: issue_found
  issues:
  - issue_id: shopping_admin.pa61.lf.left_nav_disclosure_anchor_without_widget_role
    target:
      selector: '#nav a[href=''#''][onclick*=''return false'']'
      description: the top-level admin left navigation anchor elements on the Order Status page
      coverage_policy: representative_group
    criterion:
      issue_family: link_function
      wcag_target: WCAG 4.1.2 Name, Role, Value
    evidence_rule: The matched anchor elements have `href='#'` and `onclick='return false;'` without button/disclosure roles or `aria-expanded`
      state. Activation expands a left navigation submenu in place while the current Order Status page remains loaded.
  - issue_id: shopping_admin.pa61.lf.order_status_unassign_data_post_anchor
    target:
      selector: a[href='#'][data-post*='unassign']
      description: the `Unassign` command anchor elements in the order status grid
      coverage_policy: representative_group
    criterion:
      issue_family: link_function
      wcag_target: WCAG 4.1.2 Name, Role, Value
    evidence_rule: The matched anchor elements are exposed as links with `href='#'`, but their `data-post` payload submits order-status
      unassign commands. They do not navigate to link content and do not expose a button or command role.
  - issue_id: shopping_admin.pa61.lp.order_status_unassign_without_row_context
    target:
      selector: '#sales_order_status_grid_table a[href=''#''][data-post*=''unassign'']'
      description: the ten `Unassign` action links in the order status grid
      coverage_policy: representative_group
    criterion:
      issue_family: link_purpose
      wcag_target: WCAG 2.4.4 Link Purpose (In Context)
    evidence_rule: The matched links all have the accessible name `Unassign` and no programmatically associated status/state
      context. The action cell text is only `Unassign`, the `Action` header is not bound with `headers` or `scope`, and the
      status/state values in sibling cells or `data-post` are not part of the link name or a valid programmatic context.
```

## Source And Live Check

- This L3 source may reuse reviewed L2 merge source files for the same page where applicable.
- The L3 YAML `gold.issues[]` in this file is the authoritative page-level Links L.1-L.2 inventory for this L3 benchmark unit.
- Current entries are retained from reviewed source records, live DOM checks, or reviewed L2 helper context as documented for this page.
- Coverage-gap observations are not included unless they are explicitly listed in `gold.issues[]`.

## Merge Scope

- L3 owner key: `shopping_admin + http://localhost:7780/admin/sales/order_status/`.
- This merge instance should generate one L3 task for Links L.1-L.2 on this page.
- `gold.issues[]` contains 3 issues: 2 link_function and 1 link_purpose.
- This L3 source file is authoritative for the L3 page-level inventory; it may include L3-only issues that are not part of Merge L2.
