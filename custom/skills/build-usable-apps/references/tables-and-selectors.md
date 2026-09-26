# Tables And Selectors

## Data Tables

For each unbounded table, decide explicitly:

- searchable fields;
- sortable data columns;
- filters and their defaults;
- stable secondary sort for ties;
- bounded page size;
- first, previous, nearby pages, next, and last navigation;
- row selection across or within pages;
- permitted bulk actions;
- export scope;
- mobile representation.

Action columns are not sortable. Preserve list state after actions so an operator does not lose the record they were handling.

## Relationship Selectors

Use a remote combobox for users, hosts, sponsors, owners, products, and other large relationships.

- Search by the identifiers operators actually possess.
- Debounce requests and cancel stale responses.
- Return bounded deterministic results.
- Display enough identity to disambiguate duplicates.
- Keep the menu inside the viewport and above sticky footers.
- Support keyboard navigation, Escape, outside click, clear, loading, no-results, and errors.
- Show the selected value independently of the search input.
- Validate the relationship again on the server, including capacity and cycle rules.

Do not solve one selector locally while leaving copies broken. Find the shared primitive or every equivalent use before claiming a global fix.

## Bulk Actions

- Require explicit selection.
- State the count and exact action.
- Exclude ineligible rows before confirmation and explain why.
- Make partial channel or row failures visible.
- Preserve the current query and page after completion.
- Audit actor, targets, intent, outcomes, and safe failure context.

