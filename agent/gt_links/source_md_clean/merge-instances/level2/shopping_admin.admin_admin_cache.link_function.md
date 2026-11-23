# Merge Instance

```yaml
instance_id: shopping_admin.admin_admin_cache.link_function
task_level: level2
issue_present: true

source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: PA76
  review_status: source_and_live_checked

page:
  site: shopping_admin
  page_name: Cache Management
  start_url: http://localhost:7780/admin/admin/cache/
  auth_state_file: runtime_auth_state_placeholder.json

scope:
  issue_family: link_function
  wcag_target: WCAG 4.1.2 Name, Role, Value
  assessment_requirement: L.1 Link Function

gold:
  expected_verdict: issue_found
  issues:
    - issue_id: shopping_admin.pa76.lf.left_nav_disclosure_anchor_without_widget_role
      target:
        selector: '#nav a[href=''#''][onclick*=''return false'']'
        description: the top-level admin left navigation anchor elements on the Cache Management page
        coverage_policy: representative_group
      criterion:
        issue_family: link_function
        wcag_target: WCAG 4.1.2 Name, Role, Value
      evidence_rule: >-
        The matched anchor elements have href `#` and onclick `return false` without button/disclosure roles or aria-expanded state. Activation expands a left navigation submenu in place while the Cache Management page remains loaded.
```

## Source And Live Check

- `shopping-admin-link-purpose-record.md` PA76 says 6.1 Link Function fails on the eight top-level left-navigation disclosure-as-link anchor elements.
- Fresh live PA76 probe found eight visible `#nav a[href='#'][onclick*='return false']` anchor elements: `SALES`, `CATALOG`, `CUSTOMERS`, `MARKETING`, `CONTENT`, `REPORTS`, `STORES`, and `SYSTEM`.

## Merge Scope

- L2 owner key: `shopping_admin + http://localhost:7780/admin/admin/cache/ + link_function + WCAG 4.1.2 Name, Role, Value`.
- This merge instance should generate one L2 task for PA76 link function.
