# Issue Instance

```yaml
instance_id: shopping.p03.lp.generic_view_all_without_programmatic_context
template_id: links.link_purpose.shopping.generic_view_all_without_programmatic_context
issue_present: true

source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: P03

page:
  site: shopping
  page_name: Downloadable Products
  start_url: http://localhost:7770/downloadable/customer/products/
  auth_state_file: runtime_auth_state_placeholder.json

target:
  selector: '.block-reorder a.action.view'
  description: the View All anchor element in the Recently Ordered block
  coverage_policy: single

criterion:
  issue_family: link_purpose
  wcag_target: WCAG 2.4.4 Link Purpose (In Context)

gold:
  expected_verdict: issue_found
  evidence_rule: >-
    The matched link is named only View All. The section title is visual block
    context, but it is not programmatically associated with the link through
    aria-labelledby, aria-describedby, table headers, or list-item context that
    identifies the destination collection.
```

## Selector Check

- After logging into Shopping, the `target.selector` value resolves to one visible element on P03.
- The matched anchor element has text `View All`, class `action view`, and href `http://localhost:7770/customer/account/#my-orders-table`.
