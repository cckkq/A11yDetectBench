# Issue Template

- template_id: `error.e1.invalid_date_summary_and_generic_failure_mixed`
- template_name: `Invalid-date summary path mixed with generic failure`
- domain: `error`
- primary_wcag: `3.3.1 Error Identification`
- assessment_mapping: `E.1 Error Identification`
- pattern_summary: `After invalid date input, one path only echoes the bad value as an Invalid date summary while another degrades into a generic failure; the page does not provide stable, valid field-level error identification`

## Recognition Rule
- The page has a reproducible invalid-date input path.
- One path only echoes the bad value in an active-filter summary, such as `Invalid date`.
- Another path degrades into a generic failure, such as `Something went wrong`.
- The page does not provide stable, valid field-level error identification.

## Boundary Rule
- Exclude cases that consistently reach an exception page after invalid input.
- Exclude cases with only a generic message and no mixed paths.
- Exclude cases that consistently provide field-level error identification.

## Canonical Examples
- `shopping_admin.pa48.e1.invalid_date_summary_and_generic_failure_mixed`
