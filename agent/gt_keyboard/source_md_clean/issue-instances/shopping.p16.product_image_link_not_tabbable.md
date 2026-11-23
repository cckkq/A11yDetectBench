# Issue Instance

```yaml
instance_id: shopping.p16.product_image_link_not_tabbable
template_id: keyboard.keyboard_nonreachable.clickable_image_link_not_tabbable
issue_present: true
source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: P16
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
  expected_verdict: issue_found
  evidence_rule: The target (the product image links in the toothbrushes accessories product
    grid) is visible and pointer-operable or part of an active widget, but expected keyboard
    navigation cannot reach or complete operation of that same target. Reporting a different
    keyboard issue on the page does not satisfy this rule.
```

## Selector Check

- Playwright selector audit: Playwright resolved .products-grid a.product.photo.product-item-photo to twelve visible image anchors with tabindex -1.
- The selector is the BASE L1 target selector; unresolved or conflicting legacy targets were not included in this source set.
