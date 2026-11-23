# Merge Instance

```yaml
instance_id: shopping.p16.keyboard_assessment
task_level: level3
issue_present: true
source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: P16
  review_status: current_clean_inventory
page:
  site: shopping
  page_name: Toothbrushes Accessories Category
  start_url: http://localhost:7770/beauty-personal-care/oral-care/toothbrushes-accessories.html
scope:
  assessment_scope: Keyboard assessment scope 1.1, 1.2, 1.3, 1.4, and 1.6
gold:
  expected_verdict: issue_found
  issues:
  - issue_id: shopping.p16.product_image_link_not_tabbable
    target:
      selector: .products-grid a.product.photo.product-item-photo
      description: the product image links in the toothbrushes accessories product grid
      coverage_policy: representative_group
    criterion:
      issue_family: keyboard_nonreachable
      wcag_target: WCAG 2.1.1 Keyboard
    evidence_rule: >-
      The target (the product image links in the toothbrushes accessories product grid) is
      visible and pointer-operable or part of an active widget, but expected keyboard navigation
      cannot reach or complete operation of that same target. Reporting a different keyboard
      issue on the page does not satisfy this rule.
  - issue_id: shopping.p16.select_limiter
    target:
      selector: select#limiter
      description: the Show per page selector on the toothbrushes accessories category page
      coverage_policy: single
    criterion:
      issue_family: on_input
      wcag_target: WCAG 3.2.2 On Input
    evidence_rule: >-
      The target control (the Show per page selector on the toothbrushes accessories category
      page) changes page context, navigation state, result ordering, or equivalent page state
      immediately after the control value or selection changes, without a separate submit
      or apply action and without prior warning. Merely opening a menu is not sufficient.
  - issue_id: shopping.p16.select_sorter
    target:
      selector: select#sorter
      description: the Sort By selector on the toothbrushes accessories category page
      coverage_policy: single
    criterion:
      issue_family: on_input
      wcag_target: WCAG 3.2.2 On Input
    evidence_rule: >-
      The target control (the Sort By selector on the toothbrushes accessories category page)
      changes page context, navigation state, result ordering, or equivalent page state immediately
      after the control value or selection changes, without a separate submit or apply action
      and without prior warning. Merely opening a menu is not sufficient.
```

## Source And Live Check

- This L3 merge source is restricted to a BASE-induced page owner key.
- Completeness is scoped to reviewed Keyboard inventory on that page, not a new full-site audit.
- Current L3 scope is limited to the listed Keyboard assessment items.

## Merge Scope

- Owner key: shopping + P16 + Keyboard assessment scope 1.1, 1.2, 1.3, 1.4, and 1.6.
- gold.issues[] contains 3 reviewed issue entries.
