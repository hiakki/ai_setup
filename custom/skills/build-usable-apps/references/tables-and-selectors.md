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

## Interactive Hierarchies

For an existing tree or organizational chart, define selection, expansion, focus
and viewport position separately. Expanding one branch must not collapse another
unless the requested interaction is explicitly an accordion. Committing a search
result should use the same selection transition as manual node selection. Keep
query text, result highlight and committed selection distinct; clearing a query
must not silently clear the selected node unless that is the agreed behavior.

- Keep node dimensions and text bounds stable at supported zoom levels. Recompute
  branch layout without overlapping nodes or stretching empty child controls.
- Make hidden descendants reachable through expansion or bounded loading; a
  count without an action is not a usable navigation path.
- Keep the selected node and its ancestor path understandable at depth. Collapse
  long breadcrumbs accessibly while retaining navigation to hidden ancestors.
- Test scroll/pan and zoom with touch, trackpad and keyboard controls as applicable.
  Avoid trapping page scrolling or unintentionally blocking browser zoom. Keep
  on-screen alternatives for gestures and distinguish reset-view from data changes.
- Exercise deep and uneven trees, several open branches, search-to-node navigation,
  clearing search after selection, selection without search, loading/errors and
  compact/full views if both exist.

Do not add a graph viewer or a second view just to follow this guidance. Declare
which input methods were exercised; mouse automation does not prove pinch support.

## Bulk Actions

- Require explicit selection.
- State the count and exact action.
- Exclude ineligible rows before confirmation and explain why.
- Make partial channel or row failures visible.
- Preserve the current query and page after completion.
- Audit actor, targets, intent, outcomes, and safe failure context.
