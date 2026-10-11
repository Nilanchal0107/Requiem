# 09: Web foundation

**What to build:** A React app that runs with `npm run dev`, with all 6 routes wired to placeholder pages, the `/api` proxy to FastAPI, the design tokens, every dependency and shadcn component installed up front, and the i18n loader. After this ticket V2 never edits the router, `package.json`, or any i18n loader code.

**V2 owner:** Frontend (V1 is built by the single developer)

**Blocked by:** 01

**Status:** done

## Notes

- Stack from `docs/trd.md` §1: Vite, React, TypeScript, React Router (`createBrowserRouter`), Tailwind (`@tailwindcss/vite`), shadcn/ui, Recharts, `lucide-react`, `@fontsource/mukta` (400, 500, 600, 700).
- **Install everything V2 could need now.** Add every shadcn primitive named in `docs/ui-ux.md` §4 (button, card, command, dialog or drawer/sheet, tabs, tooltip, slider, input, label, skeleton, toast, radio group, popover…). V2 must not run `npm install` or `shadcn add`.
- **Routes:** `/`, `/login`, `/new`, `/reports/:id`, `/compare`, `/reports`, each lazy-loaded and pointing at its own page file (`ui-ux.md` §8). Each page renders a distinct `h1` and nothing else.
- **Layout:** a shared layout with a plain header placeholder and an outlet. Ticket 10 swaps in the real AppBar stub.
- **Tokens:** every colour, radius, spacing and shadow from `docs/ui-ux.md` §2 as CSS variables on `:root`, mapped to Tailwind. Light theme only. Components use tokens, never raw hex.
- **Plumbing, implemented for real:** the Vite proxy for `/api` to `localhost:8000`; `request<T>` in the API module (`credentials: "include"`, throws `{status, detail}` on non-2xx); the i18n `t()` that falls back to `en`; language kept in `localStorage` inside try/catch.
- **i18n layout (decided):** one JSON file per screen per language, e.g. `i18n/en/home.json`, `i18n/hi/home.json`, `i18n/mr/home.json`, merged by the loader (`import.meta.glob`). Namespaces: common, home, login, wizard, report, compare, reports, verdict, figure, source. Create all files for all three languages now; hi and mr start as `{}`. Keys stay flat and dotted (`home.hero.title`).
- The formatter and every UI component are declared in ticket 10, not here.

## Acceptance criteria

- [ ] `npm install && npm run dev` serves the app; `npm run build` type-checks and succeeds.
- [x] Each of the 6 routes renders its own `h1` through `t()`; an unknown route shows a not-found page.
- [x] `fetch("/api/archetypes")` from the browser reaches FastAPI through the proxy (no CORS config).
- [x] `web/src/types/contracts.ts` is imported by the API module and compiles; it is not edited.
- [x] `package.json` already contains Recharts, Lucide, Mukta and every shadcn primitive named in `ui-ux.md` §4.
- [ ] All i18n files exist for all three languages and all ten namespaces; switching language changes the `h1`s once a `hi` or `mr` key exists.
- [x] Mukta is self-hosted (no CDN request) and the page uses `min-h-dvh`, never `100vh`.

## Comments

- Done in `aa7201b`.
- Verified: `npx tsc -b`, `npm run check` (i18n fallback and `request<T>`), `npm run build`, and `vite` serving all routes with `/api/archetypes` proxied to FastAPI on :8000.
- Not verified in a browser: that each route paints its `h1`. The build and module transforms pass; a browser pass is still needed.
- Not done: switching language changes the `h1`s. Setting the language has no caller until ticket 10 adds `LanguageSwitch`, and `hi`/`mr` are still `{}`.
- Deferred to ticket 10 (components): primary button is still shadcn teal, not `--cta` amber; button, input and tab heights are `h-9`, not 48 px; icons are 16 px, not 24 px; default `rounded-md` is 8 px, not the 10 px in ui-ux §2.3.
- Deferred: Mukta weights 400 and 600 are not preloaded (ui-ux §8). All four weights are imported in `main.tsx`; the browser only fetches a font when a glyph needs it.
- `i18n/index.ts` loads all 30 catalogues eagerly. Fine for V1; make it lazy per namespace if the entry chunk passes the 200 KB budget in ui-ux §8.
- `ApiError` extends `Error`, so `instanceof Error` holds for route error handlers.
- Spec drift fixed: `ui-ux.md` §6.3 and `trd.md` §1 now show the `<lang>/<namespace>.json` layout this ticket decided.
- Notes for 10: `TooltipProvider` is not needed (the shadcn Tooltip wraps its own provider). Keep `shadcn add` output under `src/components/ui`: without an `@` alias it writes to a literal `@` folder.
