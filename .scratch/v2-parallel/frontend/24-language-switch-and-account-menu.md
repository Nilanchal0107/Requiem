# 24: Language switch and account menu

**What to build:** The top app bar lets the Entrepreneur switch between English, हिन्दी and मराठी (each in its own script), and the choice is remembered. Logged in, an account menu offers My Reports and Log out. Logged out, it offers Log in, which returns to the current page afterwards.

**Owner:** Frontend

**Blocked by:** None (can start immediately)

**Status:** ready-for-agent

## Notes

- If time is short, ship only the language switch and note the account menu as deferred.
- Login: show and hide the password, paste and password managers work, and errors are clear for 401 and 409.

## Acceptance criteria

- [ ] Switching language changes copy across every route and survives a reload.
- [ ] Logged in, the menu shows My Reports and Log out, and Log out returns to guest.
- [ ] After logging in from a page, the Entrepreneur lands back on that page.
- [ ] `npm run check` and `npm run build` pass.
