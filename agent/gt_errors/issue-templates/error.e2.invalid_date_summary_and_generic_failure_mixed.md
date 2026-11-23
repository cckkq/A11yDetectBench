# Issue Template

- template_id: `error.e2.invalid_date_summary_and_generic_failure_mixed`
- template_name: `Invalid-date summary path mixed with generic failure and no corrective guidance`
- domain: `error`
- primary_wcag: `3.3.3 Error Suggestion`
- assessment_mapping: `E.2 Error Suggestion`
- pattern_summary: `The same date-input error has mixed handling: one path only echoes Invalid date in a summary, another degrades into a generic failure, and neither path provides an actionable correction suggestion`

## Recognition Rule
- The page has a reproducible invalid-date input path.
- One path only echoes `Invalid date` in a summary or active filters.
- Another path degrades into `Something went wrong` or an equivalent generic failure.
- The page does not provide a stable, actionable correction suggestion.

## Boundary Rule
- Exclude a same-page `Invalid date` case with no generic failure.
- Exclude a page-level exception with no `Invalid date` summary path.
- Exclude cases that clearly provide a format hint, example value, or other corrective direction.

## Canonical Examples
- `shopping_admin.pa48.e2.invalid_date_summary_and_generic_failure_mixed`
