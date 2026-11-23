# PASS Instance

```yaml
instance_id: shopping_admin.pa10.f25t1.split_button_revealed_menu_no_focus_shift
template_id: focus.revealing_content.split_button_revealed_menu_no_focus_shift
issue_present: false
source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: PA10
  matched_positive: shopping_admin.pa10.f25t1.split_button_revealed_menu_no_focus_shift
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
  expected_verdict: no_issue_found
  evidence_rule: >-
    Counterfactual PASS L1 for the matched BASE target: the runtime patch is expected to keep
    the same keyboard activation path but move focus into the revealed content. A reported
    revealing-content focus issue on this matched target is a false alarm for this task.
```

## Selector Check

- This PASS L1 instance is counterfactually derived from BASE L1 `shopping_admin.pa10.f25t1.split_button_revealed_menu_no_focus_shift`.
- Page, target selector, target description, setup, and criterion intentionally match the BASE L1 source instance.
- The PASS condition is supplied by the Focus runtime counterfactual patch; the target remains the same keyboard path.
