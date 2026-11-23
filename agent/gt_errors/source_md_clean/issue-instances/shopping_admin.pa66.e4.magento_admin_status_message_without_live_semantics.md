# Issue Instance

```yaml
instance_id: shopping_admin.pa66.e4.magento_admin_status_message_without_live_semantics
template_id: error.e4.magento_admin_status_message_without_live_semantics
issue_present: true

source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: PA66

page:
  site: shopping_admin
  page_name: Currency Rates
  start_url: http://localhost:7780/admin/admin/system_currency/
  auth_state_file: runtime_auth_state_placeholder.json

target:
  selector: 'button[title="Import"][data-ui-id="adminhtml-system-currency-0-import-button"]'
  description: the Import button in the Magento Admin Currency Rates page
  coverage_policy: representative_group

probe: Choose the target Import button on the Currency Rates page and observe the warning messages.

criterion:
  issue_family: status_messages
  wcag_target: WCAG 4.1.3 Status Messages

gold:
  expected_verdict: issue_found
  evidence_rule: >-
    Choosing the target Import button produces active same-page status feedback
    at `#messages .message.message-warning.warning` for the currency-rate import
    action, but those message nodes and their relevant ancestors do not expose
    role, aria-live, or equivalent status-message semantics.
```

## Selector Check

- `document.querySelectorAll('select#rate_services')` resolves to the visible currency-rate service selector on PA66.
- `document.querySelectorAll('button[title="Import"][data-ui-id="adminhtml-system-currency-0-import-button"]')` resolves to the visible Import button on PA66.
- The `#messages .message.message-warning.warning` messages are created by the same-page Import warning path after the Import action.
- The visible warning messages are evidence for this issue, but they are not the target selector. The source record reports that the Import warning message nodes use Magento Admin warning-message classes without role or aria-live semantics.
