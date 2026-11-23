# PASS Instance

```yaml
instance_id: shopping_admin.pa15.f21t6b.admin_action_buttons_no_visible_focus
template_id: focus.visible_focus.admin_action_buttons_no_visible_focus
issue_present: false
source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: PA15
  matched_positive: shopping_admin.pa15.f21t6b.admin_action_buttons_no_visible_focus
page:
  site: shopping_admin
  page_name: Catalog Price Rules
  start_url: http://localhost:7780/admin/catalog_rule/promo_catalog/
  auth_state_file: runtime_auth_state_placeholder.json
target:
  selector: button#apply_rules
  description: the Apply Rules button in the top toolbar of the Catalog Price Rules page
  coverage_policy: single
criterion:
  issue_family: visible_focus
  wcag_target: WCAG 2.4.7 Focus Visible
gold:
  expected_verdict: no_issue_found
  evidence_rule: >-
    Counterfactual PASS L1 for the matched BASE target: the runtime patch is expected to add
    a user-perceivable focus indicator for the same keyboard-focused or keyboard-current target.
    A reported visible-focus issue on this matched target is a false alarm for this task.
```

## Selector Check

- This PASS L1 instance is counterfactually derived from BASE L1 `shopping_admin.pa15.f21t6b.admin_action_buttons_no_visible_focus`.
- Page, target selector, target description, setup, and criterion intentionally match the BASE L1 source instance.
- The PASS condition is supplied by the Focus runtime counterfactual patch; the target remains the same keyboard path.
