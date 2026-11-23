# Issue Instance

```yaml
instance_id: shopping_admin.pa01.lp.tooltip_help_what_is_this_without_target_context
template_id: links.link_purpose.shopping_admin.tooltip_help_what_is_this_without_target_context
issue_present: true

source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: PA01

page:
  site: shopping_admin
  page_name: Dashboard
  start_url: http://localhost:7780/admin/admin/dashboard/
  auth_state_file: runtime_auth_state_placeholder.json

target:
  selector: 'main#anchor-content a.admin__field-tooltip-action.action-help'
  description: the `What is this?` help link in the Dashboard store-view switcher
  coverage_policy: single

criterion:
  issue_family: link_purpose
  wcag_target: WCAG 2.4.4 Link Purpose (In Context)

gold:
  expected_verdict: issue_found
  evidence_rule: >-
    The matched link has computed AX name `What is this?` and no description.
    Its title repeats the same generic text, and the surrounding tooltip
    container does not programmatically identify the scope or control that the
    help link explains.
```

## Selector Check

- `document.querySelectorAll('main#anchor-content a.admin__field-tooltip-action.action-help')` resolves to one element on PA01.
- The matched element has visible text `What is this?`, matching title text, no `aria-label`, and href `https://docs.magento.com/user-guide/configuration/scope.html`.
- The parent tooltip text repeats only `What is this?`; it does not provide a programmatic name for the helped target.
