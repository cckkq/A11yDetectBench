# PASS Instance

```yaml
instance_id: shopping.p29.f21t10.header_menu_expanded_item_no_visible_focus
template_id: focus.visible_focus.header_menu_expanded_item_no_visible_focus
issue_present: false
source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: P29
  matched_positive: shopping.p29.f21t10.header_menu_expanded_item_no_visible_focus
page:
  site: shopping
  page_name: Homepage
  start_url: http://localhost:7770/
  auth_state_file: runtime_auth_state_placeholder.json
target:
  selector: nav.navigation a[role="menuitem"][href$="/beauty-personal-care/skin-care.html"]
  description: the Skin Care submenu item in the Shopping header mega-menu
  coverage_policy: single
setup: >-
  Prepare the header mega-menu expanded state with Beauty & Personal Care open and the Skin
  Care submenu item exposed for assessment.
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

- This PASS L1 instance is counterfactually derived from BASE L1 `shopping.p29.f21t10.header_menu_expanded_item_no_visible_focus`.
- Page, target selector, target description, setup, and criterion intentionally match the BASE L1 source instance.
- The PASS condition is supplied by the Focus runtime counterfactual patch; the target remains the same keyboard path.
