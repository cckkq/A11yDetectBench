# Issue Instance

```yaml
instance_id: shopping.p20.lf.compare_page_remove_product_command_anchor
template_id: links.link_function.shopping.compare_page_remove_product_command_anchor
issue_present: true

source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: P20

page:
  site: shopping
  page_name: Compare Products
  start_url: http://localhost:7770/catalog/product_compare/index/uenc/aHR0cDovL2xvY2FsaG9zdDo3NzcwL2N1c3RvbWVyL3NlY3Rpb24vbG9hZC8_c2VjdGlvbnM9Y29tcGFyZS1wcm9kdWN0cyUyQ21lc3NhZ2VzJmZvcmNlX25ld19zZWN0aW9uX3RpbWVzdGFtcD1mYWxzZSZfPTE3NzMwNjQwODY2MDA~/
  auth_state_file: runtime_auth_state_placeholder.json

target:
  selector: '.table-comparison a.action.delete'
  description: the visible Remove Product anchor elements in the compare products table
  coverage_policy: representative_group

criterion:
  issue_family: link_function
  wcag_target: WCAG 4.1.2 Name, Role, Value

gold:
  expected_verdict: issue_found
  evidence_rule: >-
    The matched anchor elements have `href="#"`, title `Remove Product`, and
    `data-post` payloads targeting `/catalog/product_compare/remove/` with
    confirmation. Activation starts a remove-product command instead of
    navigating to link content.
```

## Selector Check

- With products present in the compare list, the `target.selector` value resolves to four visible elements on P20.
- The selector is scoped to `.table-comparison` so hidden mini-cart remove templates are not included.
