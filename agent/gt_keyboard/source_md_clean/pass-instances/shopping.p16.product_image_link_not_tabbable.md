# PASS Instance

```yaml
instance_id: shopping.p16.product_image_link_not_tabbable
template_id: keyboard.keyboard_nonreachable.clickable_image_link_not_tabbable
issue_present: false
source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: P16
  matched_positive: shopping.p16.product_image_link_not_tabbable
page:
  site: shopping
  page_name: Toothbrushes Accessories Category
  start_url: http://localhost:7770/beauty-personal-care/oral-care/toothbrushes-accessories.html
target:
  selector: .products-grid a.product.photo.product-item-photo
  description: the product image links in the toothbrushes accessories product grid
  coverage_policy: representative_group
criterion:
  issue_family: keyboard_nonreachable
  wcag_target: WCAG 2.1.1 Keyboard
gold:
  expected_verdict: no_issue_found
  evidence_rule: >-
    Counterfactual PASS L1 for the matched BASE target: the runtime patch is expected to remove
    the reviewed keyboard failure while keeping the same page, setup, target selector, and
    criterion. A reported keyboard issue on this matched clean target is a false alarm for
    this task.
```

## Selector Check

- This PASS L1 instance is counterfactually derived from BASE L1 `shopping.p16.product_image_link_not_tabbable`.
- Page, target selector, target description, setup, and criterion intentionally match the BASE L1 source instance.
- The PASS condition is supplied by the Keyboard runtime counterfactual patch; the target remains the same keyboard path.
