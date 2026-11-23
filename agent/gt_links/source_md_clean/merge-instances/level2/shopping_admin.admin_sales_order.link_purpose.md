# Merge Instance

```yaml
instance_id: shopping_admin.admin_sales_order.link_purpose
task_level: level2
issue_present: true

source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: PA04
  review_status: source_and_live_checked

page:
  site: shopping_admin
  page_name: Orders
  start_url: http://localhost:7780/admin/sales/order/
  auth_state_file: runtime_auth_state_placeholder.json

scope:
  issue_family: link_purpose
  wcag_target: WCAG 2.4.4 Link Purpose (In Context)
  assessment_requirement: L.2 Link Purpose

gold:
  expected_verdict: issue_found
  issues:
    - issue_id: shopping_admin.pa04.lp.order_grid_view_without_row_context
      target:
        selector: 'a.action-menu-item'
        description: the `View` links in the Orders grid Action column
        coverage_policy: representative_group
      criterion:
        issue_family: link_purpose
        wcag_target: WCAG 2.4.4 Link Purpose (In Context)
      evidence_rule: >-
        The matched links have computed AX name `View` and no description. Their action cells and associated column header only identify `Action`; order numbers and customer names are in sibling cells without row-header, headers/id, or ARIA association.
```

## Source And Live Check

- `shopping-admin-link-purpose-record.md` PA04 says the stable 6.2 failure group is LP015-LP214, 200 order grid `View` links.
- Fresh live PA04 probe after waiting for Magento grid binding found 200 visible `a.action-menu-item` links with text `View`.

## Merge Scope

- L2 owner key: `shopping_admin + http://localhost:7780/admin/sales/order/ + link_purpose + WCAG 2.4.4 Link Purpose (In Context)`.
- This merge instance should generate one L2 task for PA04 link purpose.
