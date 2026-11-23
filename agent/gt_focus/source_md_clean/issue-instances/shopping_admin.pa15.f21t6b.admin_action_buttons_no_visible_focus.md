# Issue Instance

```yaml
instance_id: shopping_admin.pa15.f21t6b.admin_action_buttons_no_visible_focus
template_id: focus.visible_focus.admin_action_buttons_no_visible_focus
issue_present: true
source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: PA15
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
  expected_verdict: issue_found
  evidence_rule: The Apply Rules toolbar button receives keyboard focus, but no user-perceivable focus indicator is visible while it is keyboard-focused.
```

## Selector Check

- Playwright on PA15 resolved `button#apply_rules` to one visible `Apply Rules` toolbar button.
- The selector is restricted to the top toolbar action button and not the datepicker buttons on the same page.
