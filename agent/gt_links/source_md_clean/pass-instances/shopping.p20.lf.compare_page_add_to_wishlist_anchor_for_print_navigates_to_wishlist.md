# PASS Instance

```yaml
instance_id: shopping.p20.lf.compare_page_add_to_wishlist_anchor_for_print_navigates_to_wishlist
template_id: links.link_function.pass.shopping.compare_page_add_to_wishlist_anchor_navigates_to_wishlist
issue_present: false

source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: P20
  matched_positive: shopping.p20.lf.compare_page_print_command_anchor

page:
  site: shopping
  page_name: Compare Products
  start_url: http://localhost:7770/catalog/product_compare/index/uenc/aHR0cDovL2xvY2FsaG9zdDo3NzcwL2N1c3RvbWVyL3NlY3Rpb24vbG9hZC8_c2VjdGlvbnM9Y29tcGFyZS1wcm9kdWN0cyUyQ21lc3NhZ2VzJmZvcmNlX25ld19zZWN0aW9uX3RpbWVzdGFtcD1mYWxzZSZfPTE3NzMwNjQwODY2MDA~/
  auth_state_file: runtime_auth_state_placeholder.json

target:
  selector: '.table-comparison a.action.towishlist'
  description: the Add to Wish List links in the compare products table
  coverage_policy: representative_group

criterion:
  issue_family: link_function
  wcag_target: WCAG 4.1.2 Name, Role, Value

gold:
  expected_verdict: no_issue_found
  evidence_rule: >-
    The matched links have visible text `Add to Wish List`, class
    `action towishlist`, and data-post actions targeting `/wishlist/index/add/`.
    Activation enters the wishlist login/add flow rather than running an
    unlabeled in-place print command, so the Link Function issue is not present
    for this target.
```

## Selector Check

- With products in the compare list, the selector resolves to visible Add to Wish List links on P20.
- This target is different from the `Print This Page` positive target.
