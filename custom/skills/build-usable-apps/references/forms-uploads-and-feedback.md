# Forms, Uploads, And Feedback

## Form Layout

- Use a shared field wrapper, label rhythm, control height, help text, and error treatment.
- Define responsive grid tracks instead of letting content determine widths.
- Read-only calculated fields look disabled/read-only and remain legible.
- Use native date controls for dates, menus for option sets, and checkboxes/toggles for binary choices.
- Avoid cards nested inside cards; use sections and dividers inside one working surface.

## Validation And Recovery

- Run cheap client validation for immediate feedback and authoritative server validation for trust.
- Return a structured field-error map plus one concise summary.
- Preserve all safe submitted values after a validation failure.
- Do not redirect away and discard the operator's work for a recoverable error.
- Keep the submit control pending until the server returns a durable outcome.
- Confirmation messages state what completed, not merely what was attempted.

## Upload Integrity

1. Validate type, size, dimensions, and content signature.
2. Crop/transform to a bounded application format when appropriate.
3. Upload to a temporary destination.
4. Verify size/hash and decode the stored asset.
5. Commit the profile or record and final asset atomically, or clean up the temporary asset.
6. Render the saved URL before reporting success.

Interrupted multipart input must fail without partially mutating the business record. Support slow networks with visible progress and retry guidance.

## Visual Verification

Check at minimum a phone and desktop viewport, plus long names, translated/large text, browser zoom, loading, errors, open menus, and validation states. Screenshots and interaction evidence matter; DOM existence alone does not prove usability.

