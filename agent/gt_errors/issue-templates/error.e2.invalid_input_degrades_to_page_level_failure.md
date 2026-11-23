# Issue Template

- template_id: `error.e2.invalid_input_degrades_to_page_level_failure`
- template_name: `Invalid input degrades into page-level failure without corrective guidance`
- domain: `error`
- primary_wcag: `3.3.3 Error Suggestion`
- assessment_mapping: `E.2 Error Suggestion`
- pattern_summary: `After an invalid value is entered, the page provides no actionable correction suggestion and instead degrades into a generic exception page, broken page, or equivalent page-level failure`

## Recognition Rule
- The page has a reproducible invalid-input path.
- After detecting the problem, the system provides no actionable correction suggestion.
- The worse real path reaches an exception page, broken page, or equivalent page-level failure.
- A better same-page required-field branch cannot be used to cover this worse path.

## Boundary Rule
- Exclude cases with only a generic message that remain on the same page.
- Exclude cases that mix an `Invalid date` summary path with a generic failure.
- Exclude cases that consistently provide an actionable correction suggestion.

## Canonical Examples
- `shopping_admin.pa41.e2.invalid_input_degrades_to_page_level_failure`
- `shopping_admin.pa52.e2.invalid_input_degrades_to_page_level_failure`
