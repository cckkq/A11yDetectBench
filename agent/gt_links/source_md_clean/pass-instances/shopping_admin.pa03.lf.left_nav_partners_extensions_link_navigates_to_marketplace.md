# PASS Instance

```yaml
instance_id: shopping_admin.pa03.lf.left_nav_partners_extensions_link_navigates_to_marketplace
template_id: links.link_function.pass.shopping_admin.left_nav_partners_extensions_link_navigates_to_marketplace
issue_present: false

source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: PA03
  matched_positive: shopping_admin.pa03.lf.left_nav_disclosure_anchor_without_widget_role

page:
  site: shopping_admin
  page_name: System Account
  start_url: http://localhost:7780/admin/admin/system_account/index/
  auth_state_file: runtime_auth_state_placeholder.json

target:
  selector: '#nav > li.item-partners > a[href*="/marketplace/index/"]'
  description: the Find Partners & Extensions top-level link in the admin left navigation
  coverage_policy: single

criterion:
  issue_family: link_function
  wcag_target: WCAG 4.1.2 Name, Role, Value

gold:
  expected_verdict: no_issue_found
  evidence_rule: >-
    The matched anchor element has visible text `Find Partners & Extensions`, a real
    href containing `/marketplace/index/`, and no `onclick="return false"`
    submenu-disclosure handler. Activation navigates to the marketplace page
    rather than expanding a submenu in place, so the Link Function issue is not
    present for this target.
```

## Selector Check

- The selector targets one visible top-level left navigation anchor element on PA03.
- This target is in the same left navigation widget as the positive disclosure anchor elements, but it is a leaf navigation link rather than a `href="#"` disclosure control.
