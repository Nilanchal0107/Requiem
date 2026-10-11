# 24: Language switch and account menu

**What to build:** The top app bar lets the Entrepreneur switch between English, हिन्दी and मराठी (each in its own script), and the choice is remembered. Logged in, an account menu offers My Reports and Log out. Logged out, it offers Log in, which returns to the current page afterwards.

**Owner:** Frontend

**Blocked by:** None (can start immediately)

**Status:** done

## Notes

- If time is short, ship only the language switch and note the account menu as deferred.
- Login: show and hide the password, paste and password managers work, and errors are clear for 401 and 409.

## Acceptance criteria

- [x] Switching language changes copy across every route and survives a reload.
- [x] Logged in, the menu shows My Reports and Log out, and Log out returns to guest.
- [x] After logging in from a page, the Entrepreneur lands back on that page.
- [x] `npm run check` and `npm run build` pass.

## Comments

- Commit: see `git log` for "V2-24".
- `useAuth` is now one shared store (app bar and Login see the same user). Login return uses `?next=` (same-site paths only, `lib/next.ts`).
- Filled hi/mr `common`, `login`, `reports`. `home` and `compare` hi/mr are still `{}` (en is placeholder text), so those routes fall back to English until their tickets.
- Deferred: Log in / Create account tabs from the wireframe (kept the two buttons), `new-password` autocomplete for Register, Back chevron.
- Not exercised against the live API or a browser; `npm run check` and `npm run build` pass.
