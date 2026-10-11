# 11: Home, Login, Compare and My Reports shells

**What to build:** Four routes that render real structure and talk to the stub API. Home shows its seven sections as separate components with headings. Login can log in, register and continue as guest against the auth stub, and shows the signed-in state. Compare calls the compare endpoint and shows the summary text. My Reports lists reports, or shows the 401 state for a guest.

**V2 owner:** Frontend (V1 is built by the single developer)

**Blocked by:** 03, 05, 10

**Status:** done

## Notes

- **Home:** one section component per section in `docs/prd.md` F1 (Hero, Problem, How it works, Different, Features, Schemes, Team), in one folder, composed by the page. Each renders its heading and a one-line placeholder from i18n. Copy and visuals are V2.
- **Login:** a minimal form posting to the register or login endpoint, a "Continue without account" button, and the signed-in name read from `/api/auth/me`. Implement the `useAuth` hook for real (it is plumbing). No styling polish.
- **Compare:** call the compare endpoint with a canned input from the fixture catalogue (two archetypes) and render the summary paragraph unformatted, with placeholders left as raw text. Use the declared `useCompare`.
- **My Reports:** call the list endpoint; on 401 show an EmptyState stub with a login link; otherwise list the summaries.
- **i18n:** add the `en` keys these pages need to their own namespace files (home, login, compare, reports). Do not touch other namespaces.
- Show errors as plain text; real states come in V2.

## Acceptance criteria

- [x] `/` renders seven distinct sections, each its own file.
- [ ] Logging in on `/login` then reloading shows the signed-in state; logging out clears it; continuing as a guest navigates away without error.
- [ ] `/compare` shows the summary returned by the stub endpoint.
- [ ] `/reports` shows a guest state before login and one summary row after login.
- [x] Each page changes only its own i18n namespace files and its own folder.
- [x] `npm run build` passes.

## Comments

- **Code commit:** see `git log` for the `V1-11` commit that carries this update.
- **Verified:** `npm run build` passes; `npm run check` passes (new asserts for `login`, `listReports`, `useCompare` POST). Python suite 86 passed, 5 skipped. Through the Vite proxy with the real API: guest `/api/auth/me` returns `user: null`, guest `/api/reports` returns 401, login sets the session, reports return one row after login, compare returns the summary, logout clears the session.
- **Not verified in a browser:** the three UI criteria (signed-in state after reload, `/compare` render, `/reports` guest then row). The data paths behind them are checked above; a visual pass is still open.
- **Deviations from the ticket:**
  - `useCompare` was declared to throw. It is now implemented (one POST, no state), because the ticket asks the page to use it. `checks/plumbing.check.ts` asserts it works now.
  - `useAuth` did not exist. Created `src/hooks/useAuth.ts`, with the HTTP calls in `src/api.ts` (`login`, `register`, `logout`, `me`, `listReports`, `postJson`).
  - The shared `EmptyState` is still a stub (renders no title or action), so the My Reports guest state renders its own text and login link inline.
- **Known gaps:** the Login page renders nothing until `/me` answers (`useAuth().ready` gates it), so a reload does not flash the form before the signed-in state. Errors are plain text. Compare uses a canned input and the summary placeholders are raw text, as the ticket says. Only `en` keys were added; `hi`/`mr` fall back to `en`.
- **For V2:** Home section bodies are one shared placeholder line. `reports` rows are plain text, not links.
- **Review findings deferred to V2 (standards and spec axes, `/code-review`):**
  - Touch targets: shadcn Button and Input default to h-9, under the 48 px target (`docs/ui-ux.md` §2.3). Login's "Log in" is not yet the amber CTA.
  - Login: no tabs or "Create account" wording, guest button is ghost not secondary, no autocomplete, no show-password, no return to origin page, placeholder-only inputs (§5.8, §7).
  - Plain words and states: My Reports shows raw `archetype_id` and ISO `created_at`, no empty-state icon or action, no skeletons on Compare or My Reports (§1.5, §4.18).
  - `cannedInput` copies `fixtures/report.json` by hand, and the compare ids are bare strings.
  - `hi`/`mr` namespace files are not translated yet, so those languages show English on these screens.
  - Home `home.placeholder` is developer-facing copy.
  - Duplication: the seven Home section files differ only by name and key. Kept as separate files because the ticket requires one file per section.
  - Shared hook state is per-call, so the V2 AppBar account menu would not see a login made on `/login`.
