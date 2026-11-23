# Issue Instance

```yaml
instance_id: shopping.p19.lf.compare_page_print_command_anchor
template_id: links.link_function.shopping.compare_page_print_command_anchor
issue_present: true

source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: P19

page:
  site: shopping
  page_name: Compare Products
  start_url: http://localhost:7770/catalog/product_compare/index/uenc/aHR0cDovL2xvY2FsaG9zdDo3NzcwL2N1c3RvbWVyL3NlY3Rpb24vbG9hZC8_c2VjdGlvbnM9Y29tcGFyZS1wcm9kdWN0cyUyQ21lc3NhZ2VzJmZvcmNlX25ld19zZWN0aW9uX3RpbWVzdGFtcD1mYWxzZSZfPTE3NzMwNjQwNTAxODY~/
  auth_state_file: runtime_auth_state_placeholder.json

target:
  selector: 'a.action.print'
  description: the Print This Page anchor element above the compare products table
  coverage_policy: single

criterion:
  issue_family: link_function
  wcag_target: WCAG 4.1.2 Name, Role, Value

gold:
  expected_verdict: issue_found
  evidence_rule: >-
    The matched anchor element has `href="#"` and visible text `Print This Page`.
    Activation invokes `window.print()` while the URL remains unchanged, so the
    control performs a print command rather than navigating to link content.
```

## Selector Check

- With products present in the compare list, the `target.selector` value resolves to one visible element on P19.
- The matched anchor element has text `Print This Page`, class `action print hidden-print`, and `href="#"`.
