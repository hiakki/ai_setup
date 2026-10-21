# Frontend design from day one

Use this for new frontend work and substantive visual improvements. The goal is
a coherent interface that helps its users complete real tasks. Reference sites,
component catalogs and generated design suggestions are inputs, not evidence that
the resulting application works.

## Start with a direction the product can sustain

For an existing app, inspect its rendered screens, design tokens, shared controls
and current design decisions first. Preserve useful conventions; change a visual
system deliberately rather than inserting an unrelated template. For a new app,
identify the audience, main task, content density and primary device before styling.

Choose two or three relevant references when they would resolve a design choice.
Use the [provider catalog](frontend-reference-catalog.md) by need, not as a mandatory
shopping list. Record the source URL, what to adopt/adapt/reject and why. If a source
is unavailable, say so and use accessible sources or the existing app. Never claim
to have inspected a page or video that was only named in search results.

Extract principles such as hierarchy, navigation, rhythm and interaction feedback;
do not clone another site's branding, copy, artwork or entire composition. A design
gallery is not a license to reuse the designs shown there.

When a reference is supplied for one relationship (for example video behind a
search form), isolate that dimension explicitly. Preserve the approved palette,
type, copy and controls unless their change is requested. A common outer container
with adjacent panels is not a background-media composition. Verify the literal
relationship in rendered bounds and screenshots before judging general polish.
Technical tests can pass while the interpretation fails the owner's brief; retain
that rejected evidence and correct the design contract rather than treating a
successful deployment as design acceptance.

Keep a short design contract in the app's existing design documentation (or
`DESIGN.md` when it has none): audience/task, selected references and rationale,
semantic colors, type scale, spacing, density, navigation, responsive behavior,
focus/interaction states and motion intent. Write down a few specific exclusions
when they prevent drift. This is product documentation, not a local skill copy.

## Prove one representative screen before multiplying pages

Build a screen that exercises the real shell, typography, shared controls and
content density. Use realistic synthetic copy, long labels and plausible data.
Inspect it in the browser at narrow and wide widths; fix the visual system before
propagating it to other screens. Do not seek additional approval unless the task's
scope or owner rules require it.

| Surface | Prioritize | Avoid |
| --- | --- | --- |
| Marketing / business landing page | Clear offer, readable hierarchy, credible proof, navigation and an obvious next action | Decorative sections that obscure the offer; fabricated testimonials or metrics |
| Business app / dashboard | Dense but readable data, filters, stable row actions, status/recovery and keyboard use | Copying a landing-page layout into an operational workflow |
| Video editor / creative tool | Timeline precision, playhead/selection visibility, transport controls, shortcuts, undo, asset loading and export status | Decorative motion that moves controls, delays editing or competes with preview playback |

## Adapt components and motion to the system

Prefer the app's existing shared components. For a component from a provider such
as 21st.dev, inspect its source, license, dependencies, semantics, responsive behavior
and keyboard/focus handling before adoption. Map its colors, spacing and type onto
the app's tokens; replace demonstration data and connect real states. Add only the
dependencies needed by the chosen interaction.

Use CSS for simple state transitions. Consider Motion for React when layout,
gesture or coordinated animation actually needs it and the app's stack supports
it. Consult version-appropriate official documentation before implementation.
Animation should explain a state change or preserve orientation; avoid scroll
hijacking, gratuitous entrance delays and animation on every element. Honor reduced
motion and keep all actions usable when animation is reduced or disabled. Follow
[Motion's accessibility guidance](https://motion.dev/docs/react-accessibility).

Existing installed skills can help selectively: `frontend-ui-engineering` for
implementation, `impeccable` or `design-taste-frontend` for visual refinement,
`emil-design-eng`/`animate` for interaction craft, and `web-design-guidelines` or
`browser-testing-with-devtools` for review. Read only the applicable skill and
reconcile it with the product's design system; do not stack competing aesthetics.
If a skill is absent, use this portable workflow and report the missing capability.

### Select additional specialists by the missing capability

The reviewed global additions and pins are recorded in
`docs/FRONTEND_DEVELOPMENT.md` in the central library. Use `frontend-design` for
subject-specific art direction; `ui-ux-pro-max` for targeted local reference
searches; `gsap-core`/`gsap-react` when GSAP is actually warranted; and
`expo-design-system`/`expo-native-ui` for matching native stacks. Brand Guardian
reviews identity/voice consistency; Visual Storyteller reviews visual narrative.
These complement the existing UI Designer and independent finish-gate reviewer.
Do not load every skill or delegate every task by default.

For an original logo, identity refresh or favicon delivery, select `logo-design`
when installed. It complements `brandkit`'s raster presentations: keep the SVG
master, concept comparisons and delivery assets with the app. Inspect the audit's
findings (exit zero alone is not a pass) and view the small-size/one-colour sheet.
Provider reference logos are inspiration, not reusable trademark assets. Preserve
approved branding; a design task is not automatic permission to rebrand.

Provider guidance is subordinate to the user's brief and project rules:

Anti Slop is an optional focused quality pass after choosing the design direction.
Read the installed `antislop` core and only relevant modules: `antislop-ui`,
`antislop-copywriting`, `antislop-human`, `antislop-layoutmobile`. It checks generic
composition, unsupported claims, accessibility and responsive behavior; it does
not replace the product's design contract or browser verification. The central
integration skips the upstream project-install wizard and defaults to applying
checks during authorized work, respecting saved/session modes and review-only
scope. See `docs/ANTISLOP.md`; do not copy provider rules into the app.

- Search results, agent success metrics and performance claims are suggestions,
  not measured outcomes. Do not invent testimonials or conversion gains. Preserve
  approved assets, themes and business copy unless their change is authorized.
- UI UX Pro Max's blanket objection to instant state changes does not override
  reduced motion, rapid keyboard input or immediate feedback. Inspect the actual
  returned category and relevance before applying or persisting its suggestions.
- GSAP's vendor preference does not justify adding it to a CSS/Motion project.
  `contextSafe` scopes animation recording; it does not prevent callbacks after
  unmount. Remove listeners, cancel timers and guard/abort asynchronous work.
  Verify unmount during pending work when those callbacks are implemented.
- Expo examples require a version check. Do not replace storage, icons, bundler
  configuration or build commands just because a recipe says so. Its optional
  WebGPU/native-prebuild recipe is separate scope; never bypass the owning CI/CD
  entrypoint. Do not submit feedback, add hosted MCPs or install plugin hooks as a
  side effect of reading a skill.
- Brand/storytelling roles cannot authorize a rebrand, trademark/legal claims,
  media generation or publication. Their example metrics and blanket completion
  statements must be replaced by actual evidence; assumed memory paths are not
  instructions to create another local knowledge system.

Installing a skill is only a capability check. Prove the chosen specialists on a
bounded representative screen, inspect the result independently, and keep the
user's comparison/approval gate before broad redesign work.

## Finish against observable acceptance criteria

- Reconcile each route's audience with the latest approved brief. A formerly useful
  audience tab or cross-sell can become incorrect after an explicit correction;
  verify direct links and legacy query parameters too. When comparing prepaid
  terms, show monthly equivalent, whole-term payment and the savings baseline
  together; a lower monthly equivalent must not imply monthly billing.
- For original video requirements, preserve media provenance and verify advancing
  playback time, pause/resume, looping and reduced-motion behavior in a capable
  browser. DOM presence, a poster or a resolved play promise alone is insufficient.
  Exercise source failure and ensure transport labels reflect the actual state.
  Keep media-blocked layout captures separate from successful playback evidence;
  disclose browser differences in before/after comparisons.
- When the brief asks for richer or genuinely different concepts, name the object
  users manipulate and the resulting state change for each direction. Palette,
  border and hover changes alone do not establish a new interaction. Demonstrate
  the signature transition in a recording or intermediate/settled frame pair;
  keep it usable by keyboard, touch and reduced motion. Capture comparison stills
  after entry animations settle, and label intermediate frames explicitly. Inspect
  image positioning and animated glyph bounds visually: successful image decoding
  and no page overflow do not prove correct crops or unclipped text. Editable design
  files and coded motion demos provide different evidence; verify both before
  claiming prototype fidelity.
- Compare the decision structure, not only the effects. An animated selector or
  summary should strengthen or replace an existing choice surface, rather than
  repeat it above unchanged cards. Check how much scrolling/swiping is needed to
  compare options. Shared behavior need not flatten distinct visual compositions.
  Count repeated primary actions and amounts across adjacent sections, not only
  inside each component. Keep one primary action per audience view; a disclosure
  should add conditions rather than repeat the chosen price. Use selectable plans
  only when selection changes a meaningful next step or detail; static comparison
  is clearer when every choice leads to the same unavailable purchase. Separate
  audiences when their payment models differ, while preserving deep links, Back,
  keyboard focus and existing bookmarks to previously visible content.
- Preserve workflow parity when comparing concepts: account for existing
  navigation destinations before calling a reduced interface simpler. In daily
  task screens, keep search, next work and operational actions ahead of decorative
  storytelling. Exclude demo chrome and mismatched loading/data from conclusions.
- For animated values, verify the initial accessible value as well as updates.
  Keep separators out of rolling digit cells; test shorter/longer numbers and
  interrupted changes. Check every affected control against reduced motion,
  any explicit effects switch and the agreed keyboard-feedback policy.
- For an existing UI, capture the before state before editing or replacing the
  installed build. Finish with a user-openable before/after comparison, not only
  a test-count summary. Match viewport, font scale, route, scroll position and
  data/interaction state where possible; record build/source and capture provenance.
  Keep original captures unchanged and label crops, historical states, fixture
  renders and unmatched data. Never reconstruct a missing baseline and call it an
  original screenshot, or infer UX/performance gains from changed data. Store
  private screenshots and comparison galleries in a project-local ignored area,
  verify exclusion from build packaging, and link the review artifact in the
  handoff. Missing baseline coverage is a stated limitation, not a visual PASS.
- When an approved brand change spans Web and native apps, trace each design
  owner, immutable package pin and installed consumer version. Shared ownership
  does not propagate a release automatically. Update the shared semantic tokens,
  adopt the reviewed package in every requested consumer, and verify each installed
  app. Keep platform-specific layouts and meaningful status colors; check for
  stale decorative literals separately. Package tests alone cannot prove adoption.
- Inspect the actual rendered UI at representative mobile and desktop sizes, and
  the space left by navigation/sidebars. Check overflow, text wrapping, alignment,
  sticky elements and primary-action reachability. Inspect open controls too.
  At enlarged text, inspect the contents of cards as well as page overflow:
  a page can fit while a price or translated label is clipped inside its card.
  Compare input and submit-button bounds with their immediate clipping surface,
  not only the document: an overflow-hidden hero can conceal an unreachable action
  while document width still passes. Let search controls wrap before that happens.
  Let comparison columns collapse when their readable minimum width no longer fits.
  Inspect monetary amounts as complete tokens: `overflow-wrap:anywhere` can split
  decimal digits while every overflow assertion passes. Keep amounts intact, give
  units a deliberate line, and recheck the resulting minimum width at normal and
  enlarged text. A nowrap fix alone can replace wrapping with hidden overflow.
  For native grids, exercise fractional device densities in the actual layout
  engine and installed app. A measured width can be pixel-rounded slightly above
  the parent's layout budget; exact-fit columns may wrap despite passing style
  assertions. Leave a safe rounding margin and verify both ordinary and enlarged
  text. A unit test of width arithmetic alone is not rendered-layout evidence.
- Exercise keyboard navigation, visible focus, labels and error feedback; check
  contrast and zoom, and reduced-motion behavior when motion was added. Automated
  accessibility checks alone do not establish full accessibility.
  Verify the rendered focus indicator after custom input resets: a focused DOM
  node is not a visible focus state. A contrasting focus-within outline on the
  containing search surface can restore group feedback without changing shared inputs.
  Submit forms through both their visible button and Enter. Delegated click
  handlers must route only recognized actions, leaving ordinary submit/reset
  controls to their form behavior; an attractive button can otherwise open an
  unrelated fallback dialog. Check layered compositions for obscured action
  labels, including the focus state, rather than relying on page overflow alone.
- Exercise relevant empty, loading, populated, error, disabled and success states.
  Complete the affected journey. A screenshot or DOM assertion alone cannot prove it.
  Keep an unknown or failed count distinct from a loaded zero. When adapting a
  prototype, map sample statuses and controls to actual owner capabilities;
  visual approval does not create a new availability switch or scheduling fact.
- Inspect image/font loading and the cost of added assets, JavaScript and animation.
  Avoid layout shifts and stalled interactions. Report measurements only when run
  in a named environment; no invented performance or conversion scores.
- Compare the result with the design contract and references. When a substantial
  redesign warrants independent review and delegation is allowed, give a UI or
  accessibility reviewer the brief and rendered evidence, not an expected verdict.

Record what was checked, remaining defects and untested states with the app.
Promote only sanitized reusable findings into the central skill; keep application
facts and visual assets with their owner. Installation improves discovery, not
guaranteed skill invocation or UI quality.
