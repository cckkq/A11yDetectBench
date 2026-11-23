# Merge Instance

```yaml
instance_id: shopping_admin.admin_sales_order_status.link_function
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
  issue_family: link_function
  wcag_target: WCAG 4.1.2 Name, Role, Value
  assessment_requirement: L.1 Link Function

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
      evidence_rule: >-
        The matched anchor elements have `href='#'` and `onclick='return false;'` without
        button/disclosure roles or `aria-expanded` state. Activation expands a left
        navigation submenu in place while the current Order Status page remains loaded.

    - issue_id: shopping_admin.pa61.lf.order_status_unassign_data_post_anchor
      target:
        selector: 'a[href=''#''][data-post*=''unassign'']'
        description: the `Unassign` command anchor elements in the order status grid
        coverage_policy: representative_group
      criterion:
        issue_family: link_function
        wcag_target: WCAG 4.1.2 Name, Role, Value
      evidence_rule: >-
        The matched anchor elements are exposed as links with `href='#'`, but their
        `data-post` payload submits order-status unassign commands. They do not
        navigate to link content and do not expose a button or command role.

```

## Source And Live Check

- `shopping-admin-link-purpose-record.md` PA61 states that 6.1 Link Function fails on L01-L08 left top-level menu anchor elements and L09-L18 ten `Unassign` anchor elements.
- Fresh live PA61 probe after refreshing Shopping Admin auth found eight visible `#nav a[href='#'][onclick*='return false']` anchor elements and ten visible `a[href='#'][data-post*='unassign']` anchor elements.
- The live probe found no `aria-label`, `aria-labelledby`, `aria-describedby`, `title`, `role`, or `aria-expanded` on these target anchor elements.
- PA61 also has 6.2 link-purpose failures on `Unassign`, but this merge instance records only the 6.1 link-function evidence.

## Merge Scope

- L2 owner key: `shopping_admin + http://localhost:7780/admin/sales/order_status/ + link_function + WCAG 4.1.2 Name, Role, Value`.
- This merge instance should generate one L2 task for PA61 link function, not one L2 task per command/disclosure pattern.
- The two entries in `gold.issues[]` preserve all PA61 source-record link-function failure groups.
