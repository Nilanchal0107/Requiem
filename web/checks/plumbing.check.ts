// Runnable check for the non-trivial plumbing: i18n fallback and request<T>.
// Run: npm run check
import assert from "node:assert/strict";
import { translate, type Catalog, type Lang } from "../src/i18n/resolve.ts";
import { ApiError, request } from "../src/api.ts";
import { formatFigure, formatMoneyWords } from "../src/lib/format.ts";
import { useSimulate } from "../src/hooks/useSimulate.ts";
import { useChat } from "../src/hooks/useChat.ts";
import { useCompare } from "../src/hooks/useCompare.ts";

// i18n: a missing key in hi/mr falls back to en; a key nobody has is returned as-is.
const catalogs: Record<Lang, Catalog> = {
  en: { "home.title": "Home", "only.en": "English only" },
  hi: { "home.title": "होम" },
  mr: {},
};
assert.equal(translate(catalogs, "hi", "home.title"), "होम");
assert.equal(translate(catalogs, "mr", "home.title"), "Home");
assert.equal(translate(catalogs, "hi", "only.en"), "English only");
assert.equal(translate(catalogs, "en", "missing.key"), "missing.key");

// request<T>: sends credentials, returns JSON on 2xx, throws {status, detail} otherwise.
const seen: RequestInit[] = [];
let reply = new Response(JSON.stringify([{ id: "dairy" }]), {
  status: 200,
  headers: { "content-type": "application/json" },
});
globalThis.fetch = async (_input: unknown, init?: RequestInit) => {
  seen.push(init ?? {});
  return reply;
};

const ok = await request<{ id: string }[]>("/api/archetypes");
assert.deepEqual(ok, [{ id: "dairy" }]);
assert.equal(seen[0].credentials, "include");

reply = new Response(JSON.stringify({ detail: "Not logged in" }), {
  status: 401,
  headers: { "content-type": "application/json" },
});
await assert.rejects(request("/api/auth/me"), (err: unknown) => {
  assert.ok(err instanceof ApiError);
  assert.equal(err.status, 401);
  assert.equal(err.detail, "Not logged in");
  return true;
});

// Declared stubs: formatting and hooks throw "not implemented" until V2.
const figure = { id: "x", label: "x", value: 1, unit: "INR", source: "computed" } as const;
assert.throws(() => formatFigure(figure, "en"), /not implemented/);
assert.throws(() => formatMoneyWords(1e5, "hi"), /not implemented/);
assert.throws(() => useSimulate(), /not implemented/);
assert.throws(() => useChat(), /not implemented/);
assert.throws(() => useCompare(), /not implemented/);

console.log("plumbing checks passed");
