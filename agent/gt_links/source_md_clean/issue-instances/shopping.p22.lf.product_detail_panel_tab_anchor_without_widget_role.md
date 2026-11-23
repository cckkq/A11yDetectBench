# Issue Instance

```yaml
instance_id: shopping.p22.lf.product_detail_panel_tab_anchor_without_widget_role
template_id: links.link_function.shopping.product_detail_panel_tab_anchor_without_widget_role
issue_present: true

source:
  record_file: redacted_source_record_for_double_anonymous_review
  page_id: P22

page:
  site: shopping
  page_name: Product Detail
  start_url: http://localhost:7770/auuxva-sport-soccer-ball-storage-bins-basket-football-theme-collapsible-storage-cube-rectangle-storage-box-with-handles-for-shelf-closet-nursery-bedroom-home-office-1-pack.html
  auth_state_file: runtime_auth_state_placeholder.json

target:
  selector: '.product.data.items a.data.switch'
  description: the Details and Reviews product information tab anchor elements
  coverage_policy: representative_group

criterion:
  issue_family: link_function
  wcag_target: WCAG 4.1.2 Name, Role, Value

gold:
  expected_verdict: issue_found
  evidence_rule: >-
    The matched anchor elements are exposed as links with hrefs to page fragments, but
    activation switches the visible product information panel in place. The
    interactive tab state is represented on the parent title elements, while
    the focusable anchor elements themselves are ordinary links.
```

## Selector Check

- After opening P22, the `target.selector` value resolves to two visible elements.
- The matched anchor elements are `Details` and `Reviews`, with ids `tab-label-description-title` and `tab-label-reviews-title`.
