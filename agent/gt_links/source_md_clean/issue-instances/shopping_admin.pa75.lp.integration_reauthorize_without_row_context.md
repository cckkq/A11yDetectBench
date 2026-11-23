# Issue Instance

```yaml
instance_id: shopping_admin.pa75.lp.integration_reauthorize_without_row_context
template_id: links.link_purpose.shopping_admin.integration_reauthorize_without_row_context
issue_present: true

source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: PA75

page:
  site: shopping_admin
  page_name: Integrations
  start_url: http://localhost:7780/admin/admin/integration/
  auth_state_file: runtime_auth_state_placeholder.json

target:
  selector: '#integrationGrid_table td.col-activate a'
  description: the `Reauthorize` link in the Integrations grid Activate column
  coverage_policy: single

criterion:
  issue_family: link_purpose
  wcag_target: WCAG 2.4.4 Link Purpose (In Context)

gold:
  expected_verdict: issue_found
  evidence_rule: >-
    The matched link has computed AX name `Reauthorize` and no description. Its
    title repeats the same action text, and the Activate cell/header do not
    programmatically identify the integration row, whose name is in a sibling
    cell without row-header, headers/id, or ARIA association.
```

## Selector Check

- `document.querySelectorAll('#integrationGrid_table td.col-activate a')` resolves to one element on PA75.
- The matched element has visible text `Reauthorize`, title `Reauthorize`, no `aria-label`, and `href=javascript:void(0);`.
- The row contains `Magento Analytics user`, but that text is ordinary sibling-cell text rather than programmatic link context.
