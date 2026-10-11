# 10: Real auth

**What to build:** An Entrepreneur can register, log in, stay logged in, and log out for real. The password is hashed. A taken username gets a clear 409, and a wrong username or password gets a 401.

**Owner:** Fullstack

**Blocked by:** None (can start immediately)

**Status:** ready-for-agent

## Notes

- Use the user table already declared. Usernames are unique.
- Passwords use standard-library scrypt in the declared `scrypt$<salt hex>$<hash hex>` format, compared in constant time.
- The signed session cookie holds the user id. Return the same 401 message for an unknown user and for a wrong password.
- Remove the stub-login `shortcut:` comment once it's real.

## Acceptance criteria

- [ ] Register, then register again with the same username: the second gets 409.
- [ ] Login with a wrong password gets 401. Login with the right one sets the cookie, and `me` returns the user.
- [ ] After logout, `me` returns no user.
- [ ] The stored password is not the plain text and verifies through scrypt.
- [ ] Tests run against a fresh SQLite database per test run.
