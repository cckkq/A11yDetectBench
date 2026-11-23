# Issue Template

- template_id: `error.e2.invalid_date_without_expected_format`
- template_name: `Invalid date message without the expected format`
- domain: `error`
- primary_wcag: `3.3.3 Error Suggestion`
- assessment_mapping: `E.2 Error Suggestion`
- pattern_summary: `A date-filter value is automatically rejected, but the page only echoes Invalid date or an equivalent message and provides no expected format, example value, or other corrective direction`

## Recognition Rule
- A date-input error is detected automatically.
- The page gives an in-page `Invalid date` message or equivalent date-error text.
- The page provides no expected date format, example value, placeholder, or other correction direction.
- The issue remains in a same-page summary path rather than becoming a page-level failure.

## Boundary Rule
- Exclude cases that mix the `Invalid date` summary path with a generic failure.
- Exclude cases where invalid dates directly degrade into an exception page or broken page.
- Exclude cases that clearly provide a date-format explanation or example value.

## Canonical Examples
- `shopping_admin.pa04.e2.invalid_date_without_expected_format`
- `shopping_admin.pa06.e2.invalid_date_without_expected_format`
