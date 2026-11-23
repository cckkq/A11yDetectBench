# PASS Instance

```yaml
instance_id: shopping.p10.lf.product_detail_add_to_wishlist_navigates_to_wishlist
template_id: links.link_function.pass.shopping.product_detail_add_to_wishlist_navigates_to_wishlist
issue_present: false

source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: P10
  matched_positive: shopping.p10.lf.product_detail_panel_tab_anchor_without_widget_role

page:
  site: shopping
  page_name: Product Detail
  start_url: http://localhost:7770/pre-baked-gingerbread-house-kit-value-pack-17-oz-pack-of-2-total-34-oz.html
  auth_state_file: runtime_auth_state_placeholder.json

target:
  selector: '.product-social-links a.action.towishlist'
  description: the Add to Wish List anchor element in the product detail action links
  coverage_policy: single

criterion:
  issue_family: link_function
  wcag_target: WCAG 4.1.2 Name, Role, Value

gold:
  expected_verdict: no_issue_found
  evidence_rule: >-
    The matched anchor element has visible text `Add to Wish List`, class
    `action towishlist`, and a `data-post` action targeting
    `/wishlist/index/add/`. Activation enters the wishlist login/add flow, so
    the Link Function issue is not present for this target.
```

## Selector Check

- A construction-time selector check confirmed one visible matching anchor element on P10.
