# 10: Real auth

**What to build:** An Entrepreneur can register, log in, stay logged in, and log out for real. The password is hashed. A taken username gets a clear 409, and a wrong username or password gets a 401.

**Owner:** Fullstack

**Blocked by:** None (can start immediately)

**Status:** done

## Notes

- Use the user table already declared. Usernames are unique.
- Passwords use standard-library scrypt in the declared `scrypt$<salt hex>$<hash hex>` format, compared in constant time.
- The signed session cookie holds the user id. Return the same 401 message for an unknown user and for a wrong password.
- Remove the stub-login `shortcut:` comment once it's real.

## Acceptance criteria

- [x] Register, then register again with the same username: the second gets 409.
- [x] Login with a wrong password gets 401. Login with the right one sets the cookie, and `me` returns the user.
- [x] After logout, `me` returns no user.
- [x] The stored password is not the plain text and verifies through scrypt.
- [x] Tests run against a fresh SQLite database per test run.

## Comments

- Commit: see `V2-10: Real auth` in git log.
- `api/deps.py` gains `get_session()` (a SQLModel `Session` on `api.db.engine`). Tickets 11–13 should take it as a dependency, not open their own sessions.
- Tests: the `client` fixture in `tests/test_api_smoke.py` now builds a fresh SQLite file under `tmp_path` and overrides `get_session`; use the `db_engine` fixture to inspect rows directly. No `conftest.py` was added, since `tests/conftest.py` has no row in the V2 file map.
- The session cookie holds `{id, username}` (the existing `current_user` shape), signed by `SessionMiddleware`. No DB lookup on each request, so a deleted user keeps a valid cookie until logout. Fine for the demo.
- Duplicate usernames are caught by the unique index (`IntegrityError` → 409), so a race between two registers still gets one 409.
- Deferred: no login rate-limiting.
