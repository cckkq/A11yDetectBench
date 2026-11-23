# Issue Template

- template_id: `error.e1.invalid_input_degrades_to_page_level_failure`
- template_name: `Invalid input degrades into page-level failure`
- domain: `error`
- primary_wcag: `3.3.1 Error Identification`
- assessment_mapping: `E.1 Error Identification`
- pattern_summary: `After an invalid value is entered, the page provides no valid field-level error identification and instead degrades into a generic exception page, broken page, or equivalent page-level failure`

## Recognition Rule
- The page has a reproducible invalid-input path.
- After detecting the problem, the system provides no valid field-level error identification.
- The worse real path reaches an exception page, broken page, or equivalent page-level failure.
- A better same-page required-field branch cannot be used to cover this worse path.

## Boundary Rule
- Exclude cases with only a generic message that remain on the same page.
- Exclude mixed cases that only echo `Invalid date` in an active-filter summary.
- Exclude cases that consistently provide field-level error identification.

## Canonical Examples
- `shopping_admin.pa41.e1.invalid_input_degrades_to_page_level_failure`
- `shopping_admin.pa53.e1.invalid_input_degrades_to_page_level_failure`
