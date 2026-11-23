# PASS Instance

```yaml
instance_id: shopping.p29.lf.home_product_card_add_to_wishlist_navigates_to_wishlist
template_id: links.link_function.pass.shopping.home_product_card_add_to_wishlist_navigates_to_wishlist
issue_present: false

source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: P29
  matched_positive: shopping.p29.lf.home_product_card_add_to_compare_command_anchor

page:
  site: shopping
  page_name: Home
  start_url: http://localhost:7770/
  auth_state_file: runtime_auth_state_placeholder.json

target:
  selector: '.products-grid a.action.towishlist'
  description: the Add to Wish List anchor elements in home page product cards
  coverage_policy: representative_group

criterion:
  issue_family: link_function
  wcag_target: WCAG 4.1.2 Name, Role, Value

gold:
  expected_verdict: no_issue_found
  evidence_rule: >-
    The matched anchor elements have visible text `Add to Wish List`, class
    `action towishlist`, and `data-post` actions targeting
    `/wishlist/index/add/`. Activation enters the wishlist login/add flow, so
    the Link Function issue is not present for this target.
```

## Selector Check

- `document.querySelectorAll('.products-grid a.action.towishlist')` resolves to twelve visible anchor elements.
