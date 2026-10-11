# 10: Component declarations

**What to build:** One file per component from `docs/ui-ux.md` §4, each with typed props taken from the generated contract types and an empty body. After this ticket V2 implements components one file at a time, and the pages already import them.

**V2 owner:** Frontend (V1 is built by the single developer)

**Blocked by:** 09

**Status:** done

## Notes

- **Components, one file each:** AppBar, LanguageSwitch, BottomActionBar, Stepper, ChoiceCard, ChipGroup, NumberStepper, MoneyInput, VerdictCard, MetricRows, FigureChip, FigureSheet, SourceBadge, StageTrace, Tabs wrapper if needed, OfflineBanner, ExplanationUnavailable, EmptyState, ErrorState, and five charts (CostBreakdownChart, MeansOfFinanceChart, CashFlowChart, RepaymentChart, ComparisonChart).
- **No barrel `index.ts`.** Pages import each component by its own path, so adding a component never edits a shared file.
- Props come from `types/contracts.ts` (`Figure`, `StageEvent`, `VerdictLevel`, `EngineResult`…). Where a component needs a prop the contract doesn't have (open/closed, callbacks), add it to the props type.
- Bodies are empty or return a single labelled placeholder so a page that mounts them still renders. Behaviour is V2.
- **AppBar:** the stub renders only the product name. Mount it in the shared layout from ticket 09, replacing the header placeholder.
- **Formatting:** declare `formatFigure(figure, lang)` and `formatMoneyWords` signatures in the format module (`Intl.NumberFormat`, locales `en-IN` / `hi-IN` / `mr-IN`, Devanagari digits via `-u-nu-deva`), no implementation. Declare the hooks for features V1 doesn't wire: `useSimulate`, `useChat`, `useCompare` (one file each). Hooks the shells need are implemented in tickets 11–13.
- Declared means the file compiles and exports the right name and props; it does not mean it works.

## Acceptance criteria

- [x] Every component listed above has its own file, exports a typed component, and compiles under `npm run build`.
- [x] No `index.ts` barrel exists anywhere under the components folder.
- [ ] `npm run dev` still renders all 6 routes; the layout now shows the AppBar stub.
- [x] `formatFigure` and the three hooks are declared with signatures and docstrings; they throw "not implemented" if called.
- [x] No component hand-defines a type that already exists in `contracts.ts`.

## Comments

- **Code commit:** `c1bc264` (V1-10: component declarations).
- **Verified:** `npm run build` (tsc -b + vite build) passes; `npm run check` passes, including new asserts that `formatFigure`, `formatMoneyWords`, `useSimulate`, `useChat`, `useCompare` throw "not implemented".
- **Not verified:** `npm run dev` rendering in a browser. Only the build was run, so the route-render criterion stays unticked.
- **Deferred:** the "Tabs wrapper if needed" item. shadcn `web/src/components/ui/tabs.tsx` already exists; add a wrapper only when a page needs one.
- **For V2:** `RootLayout` now mounts `AppBar`. Each component is a placeholder labelled with its own name, so V2 replaces bodies only. Props for open/closed and callbacks were added where the contract lacks them (`FigureSheet.open`, `onSeePath`, `onRetry`, `onSelect`).
- **Review (`70ee677..c1bc264`):** no blocking findings. Minor: components import contract types via `@/types/contracts` while `lib/format.ts` and `hooks/` use relative `.ts` paths (both styles already exist in the repo). Git warned about CRLF on checkout, which is an environment `autocrlf` setting and not a code issue.
