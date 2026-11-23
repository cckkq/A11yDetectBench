# Issue Template

- template_id: `error.e1.generic_message_not_field_specific`
- template_name: `Error detected, but the message is generic and does not identify the field`
- domain: `error`
- primary_wcag: `3.3.1 Error Identification`
- assessment_mapping: `E.1 Error Identification`
- pattern_summary: `The system detects an input problem, but the returned error message remains generic and does not identify the specific field or error type`

## Recognition Rule
- The page detects an input error.
- The user sees a textual error message.
- The message remains generic, such as `This value is not valid.`
- The message does not clearly identify the affected item or the type of error.

## Boundary Rule
- Exclude cases with no error text.
- Exclude cases where invalid input directly degrades into an exception page or broken page.
- Exclude cases where the error text clearly identifies both the field and the error type.

## Canonical Examples
- `reddit.rd11.e1.generic_message_not_field_specific`
- `reddit.ex02.e1.generic_message_not_field_specific`
