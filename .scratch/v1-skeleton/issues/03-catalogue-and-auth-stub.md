# 03: Catalogue and auth stub

**What to build:** The API starts with its database tables declared, serves the catalogue from fixtures, and has a working auth stub. `GET /api/localities` (all three levels), `/api/archetypes` and `/api/schemes` return fixture data. Register and login accept any valid body and put a fixture user in the session; logout clears it; `/me` reports whoever is in the session, or a guest.

**V2 owner:** Fullstack (V1 is built by the single developer)

**Blocked by:** 01, 02

**Status:** done

## Notes

- Declare the `user`, `report` and `village` SQLModel tables with the columns in `docs/trd.md` §4.5 and create them at startup. Nothing reads or writes them yet.
- A `USE_FIXTURES` setting (env-driven, default on) decides whether routes serve fixtures. Keep it in its own small module so routers can import it without a circular import with the app. V3 removes it. Add a fixture loader there too.
- Declare `current_user` and `require_user` dependencies. The 401 rule for `/api/reports` uses them in ticket 04.
- **Auth stub (decided):** no hashing and no DB lookup. Real scrypt, the DB user lookup and the 409/401 rules arrive in V2. Declare the scrypt helpers with signatures only.
- Locality queries follow the contract: no query → districts, `district` → blocks, `district` + `block` → villages. Unknown codes return 404 for a village lookup and an empty list otherwise.

## Acceptance criteria

- [x] The server starts, creates the three tables in SQLite, and restarts cleanly.
- [x] The three locality shapes, `/archetypes` and `/schemes` return data that validates against the contract models.
- [x] Login sets a session cookie, `/me` then returns the stub user, logout clears it and `/me` returns `{user: null}`.
- [x] Register and login reject a malformed body with 422 (username 3–30, password ≥ 6) but accept anything valid.
- [x] Password-hash helpers are declared and raise `NotImplementedError`.
- [x] `tests/test_api_smoke.py` exists and covers these endpoints with contract validation.

## Comments

- Done in `1a6f466`. `tests/test_api_smoke.py`: 15 tests, full suite 30 passing.
- **Code review (medium):** fixed `USE_FIXTURES` parsing (`false` / `off` now disable), a block without a district now returns 404, and `/me` reuses `current_user`. Left as is: the stub login accepts any password and register never returns 409 (the ticket asks for the stub; real 401/409 are V2). The `SESSION_SECRET="change-me"` default predates this ticket; fail-on-unset is a V2/V3 decision. The SQLite engine uses default `check_same_thread`; no route touches the DB yet, so V2 must set it when routes start using the DB. The session key `"user"` and the helper names follow the frozen `UserOut` name.
- **Module layout:** `api/settings.py` (env, `USE_FIXTURES`, `fixture()` loader), `api/db.py` (the `user`, `report`, `village` tables and `create_tables`), `api/deps.py` (`current_user`, `require_user`). Password helpers `hash_password` / `verify_password` live in `api/auth.py`.
- **Deviation from `docs/trd.md` §5/§7:** the TRD puts `USE_FIXTURES` in `api/main.py`. The ticket asks for its own module, so routers can import it without a cycle with the app. Followed the ticket.
- **`api/main.py` was edited** (ticket 01 said V2 never edits it). It now runs `create_tables()` in a lifespan hook and reads `SESSION_SECRET` from settings. `load_dotenv()` moved into `api/settings.py`, which closes the ordering note from ticket 01.
- **Stub user:** login and register both put `{id: 1, username: "demo"}` in the session, whatever the body says. Real lookup is V2.
- **Auth routes are not gated by `USE_FIXTURES`:** they are a stub, not fixture data.
- **Not tested here:** `require_user` (the 401 path) has no test; ticket 04 covers it through `/api/reports`.
- **Not run:** no typechecker is configured in `pyproject.toml`, so no typecheck ran. Import and the full pytest run cover the same ground.
- **Local DB:** the restart check created `requiem.db` at the repo root. It is git-ignored.
- **Contract:** no model changed, so `api/contracts.py` and `web/src/types/contracts.ts` are untouched and need no regeneration.
