# Issue Instance

```yaml
instance_id: shopping_admin.pa10.f25t1.split_button_revealed_menu_no_focus_shift
template_id: focus.revealing_content.split_button_revealed_menu_no_focus_shift
issue_present: true
source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: PA10
page:
  site: shopping_admin
  page_name: Products
  start_url: http://localhost:7780/admin/catalog/product/
  auth_state_file: runtime_auth_state_placeholder.json
target:
  selector: .page-actions button.action-toggle.primary.add
  description: the Add Product split-button trigger and revealed product-type menu
  coverage_policy: single
criterion:
  issue_family: revealing_content
  wcag_target: WCAG 2.4.3 Focus Order
gold:
  expected_verdict: issue_found
  evidence_rule: Keyboard activation reveals the menu, but focus does not move into the revealed menu content.
```

## Selector Check

- Playwright on PA10 resolved `.page-actions button.action-toggle.primary.add` to the visible Add Product split-button trigger.
- The matched button had title `Add Product`, aria-label `Add product of type`, and text `Select`.
