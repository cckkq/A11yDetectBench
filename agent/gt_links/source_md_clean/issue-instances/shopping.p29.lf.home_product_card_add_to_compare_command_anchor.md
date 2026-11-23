# Issue Instance

```yaml
instance_id: shopping.p29.lf.home_product_card_add_to_compare_command_anchor
template_id: links.link_function.shopping.home_product_card_add_to_compare_command_anchor
issue_present: true

source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: P29

page:
  site: shopping
  page_name: Home
  start_url: http://localhost:7770/
  auth_state_file: runtime_auth_state_placeholder.json

target:
  selector: '.products-grid a.action.tocompare'
  description: the Add to Compare anchor elements in home page product cards
  coverage_policy: representative_group

criterion:
  issue_family: link_function
  wcag_target: WCAG 4.1.2 Name, Role, Value

gold:
  expected_verdict: issue_found
  evidence_rule: >-
    The matched anchor elements have href="#" and `data-post` values targeting
    `/catalog/product_compare/add/`. Activation adds the product to the compare
    list and shows page feedback instead of navigating to link content.
```

## Selector Check

- After logging into Shopping, the `target.selector` value resolves to twelve visible elements on P29.
- The matched anchor elements have text `Add to Compare`, class `action tocompare`, `href="#"`, and `data-post` payloads for different product ids.
