# Issue Instance

```yaml
instance_id: shopping_admin.pa03.lf.left_nav_disclosure_anchor_without_widget_role
template_id: links.link_function.shopping_admin.left_nav_disclosure_anchor_without_widget_role
issue_present: true

source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: PA03

page:
  site: shopping_admin
  page_name: System Account
  start_url: http://localhost:7780/admin/admin/system_account/index/
  auth_state_file: runtime_auth_state_placeholder.json

target:
  selector: '#nav a[href="#"][onclick*="return false"]'
  description: the top-level admin left navigation anchor elements
  coverage_policy: representative_group

criterion:
  issue_family: link_function
  wcag_target: WCAG 4.1.2 Name, Role, Value

gold:
  expected_verdict: issue_found
  evidence_rule: >-
    The matched anchor elements have `href="#"` and `onclick="return false;"` without
    button/disclosure roles or aria-expanded state. Activation expands a left
    navigation submenu in place while the current admin page remains loaded.
```

## Selector Check

- After logging into Shopping Admin, the `target.selector` value resolves to eight visible elements on PA03.
- The matched anchor elements are `SALES`, `CATALOG`, `CUSTOMERS`, `MARKETING`, `CONTENT`, `REPORTS`, `STORES`, and `SYSTEM`.
