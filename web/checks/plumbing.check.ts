// Runnable check for the non-trivial plumbing: i18n fallback, request<T>, and the shell hooks.
// Run: npm run check
import assert from "node:assert/strict";
import { translate, type Catalog, type Lang } from "../src/i18n/resolve.ts";
import { ApiError, getReport, login, listReports, request } from "../src/api.ts";
import { parseTab } from "../src/pages/report/tab.ts";
import { formatFigure, formatMoneyWords } from "../src/lib/format.ts";
import { useSimulate } from "../src/hooks/useSimulate.ts";
import { useChat } from "../src/hooks/useChat.ts";
import { useCompare } from "../src/hooks/useCompare.ts";
import { createReport, openReportStream } from "../src/hooks/useReportStream.ts";

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

// Every call records its URL and init, and answers with `reply`.
const seen: { url: string; init: RequestInit }[] = [];
let reply = new Response(JSON.stringify([{ id: "dairy" }]), {
  status: 200,
  headers: { "content-type": "application/json" },
});
globalThis.fetch = async (input: unknown, init?: RequestInit) => {
  seen.push({ url: String(input), init: init ?? {} });
  return reply;
};

// request<T>: sends credentials, returns JSON on 2xx, throws {status, detail} otherwise.
const ok = await request<{ id: string }[]>("/api/archetypes");
assert.deepEqual(ok, [{ id: "dairy" }]);
assert.equal(seen[0].init.credentials, "include");

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

// login: POSTs the credentials as JSON to the stub endpoint and returns the user.
reply = new Response(JSON.stringify({ id: 1, username: "demo" }), {
  status: 200,
  headers: { "content-type": "application/json" },
});
const user = await login({ username: "demo", password: "secret1" });
assert.deepEqual(user, { id: 1, username: "demo" });
assert.equal(seen.at(-1)!.url, "/api/auth/login");
assert.equal(seen.at(-1)!.init.method, "POST");
assert.equal(seen.at(-1)!.init.body, JSON.stringify({ username: "demo", password: "secret1" }));

// listReports: GET the list endpoint.
reply = new Response(JSON.stringify([]), { status: 200, headers: { "content-type": "application/json" } });
assert.deepEqual(await listReports(), []);
assert.equal(seen.at(-1)!.url, "/api/reports");

// getReport: GET the report by id.
reply = new Response(JSON.stringify({ id: "r-1" }), { status: 200, headers: { "content-type": "application/json" } });
assert.deepEqual(await getReport("r-1"), { id: "r-1" });
assert.equal(seen.at(-1)!.url, "/api/reports/r-1");

// parseTab: the ?tab= value is trusted only when it names a tab; everything else is Explanation.
assert.equal(parseTab("numbers"), "numbers");
assert.equal(parseTab("bank"), "bank");
assert.equal(parseTab("explanation"), "explanation");
assert.equal(parseTab("nope"), "explanation");
assert.equal(parseTab(null), "explanation");

// useCompare: POSTs the compare request as JSON and returns the Comparison.
reply = new Response(JSON.stringify({ summary: "x" }), { status: 200, headers: { "content-type": "application/json" } });
const compareRequest = { input: {}, archetype_ids: ["dairy", "poultry"] } as never;
assert.deepEqual(await useCompare()(compareRequest), { summary: "x" });
assert.equal(seen.at(-1)!.url, "/api/compare");
assert.equal(seen.at(-1)!.init.method, "POST");
assert.equal(seen.at(-1)!.init.body, JSON.stringify(compareRequest));

// createReport: POSTs the intake and returns the new report id.
reply = new Response(JSON.stringify({ report_id: "r-1" }), { status: 200, headers: { "content-type": "application/json" } });
assert.equal(await createReport({ village_code: "FX1002" } as never), "r-1");
assert.equal(seen.at(-1)!.url, "/api/reports");
assert.equal(seen.at(-1)!.init.method, "POST");

// openReportStream: a fake EventSource records listeners so the check can fire events by hand.
type Listener = (e: { data: string }) => void;
class FakeEventSource {
  static last: FakeEventSource;
  url: string;
  listeners: Record<string, Listener> = {};
  onerror: (() => void) | null = null;
  closed = false;
  constructor(url: string) {
    this.url = url;
    FakeEventSource.last = this;
  }
  addEventListener(name: string, fn: Listener) {
    this.listeners[name] = fn;
  }
  close() {
    this.closed = true;
  }
}
globalThis.EventSource = FakeEventSource as never;

const stages: string[] = [];
const doneIds: string[] = [];
let failures = 0;
const close = openReportStream("r-1", {
  onStage: (e) => stages.push(`${e.stage}:${e.status}`),
  onDone: (id) => doneIds.push(id),
  onError: () => failures++,
});
const src = FakeEventSource.last;
assert.equal(src.url, "/api/reports/r-1/stream");
src.listeners.stage({ data: JSON.stringify({ stage: "intake", status: "running" }) });
src.listeners.stage({ data: JSON.stringify({ stage: "intake", status: "done" }) });
assert.deepEqual(stages, ["intake:running", "intake:done"]);
src.listeners.done({ data: JSON.stringify({ report_id: "r-1" }) });
assert.deepEqual(doneIds, ["r-1"]);
assert.equal(src.closed, true, "done closes the stream before the server's end-of-stream error");
assert.equal(failures, 0);

const failed = openReportStream("r-2", { onStage: () => {}, onDone: () => {}, onError: () => failures++ });
FakeEventSource.last.onerror!();
assert.equal(failures, 1);
assert.equal(FakeEventSource.last.closed, true);
failed();
close();

// Formatting: lakh grouping, Devanagari digits for hi/mr, words line.
const figure = { id: "x", label: "x", value: 417460, unit: "INR", source: "computed" } as const;
assert.equal(formatFigure(figure, "en"), "₹4,17,460");
assert.equal(formatFigure(figure, "mr"), "₹४,१७,४६०");
assert.equal(formatFigure({ ...figure, value: 2.06, unit: "ratio" }, "en"), "2.06");
assert.equal(formatFigure({ ...figure, value: 10, unit: "%" }, "hi"), "१०%");
assert.equal(formatMoneyWords(1e5, "en"), "₹1 lakh");
assert.equal(formatMoneyWords(150000, "hi"), "₹१.५ लाख");
assert.equal(formatMoneyWords(500, "en"), "₹500");
// Declared stubs: the V2 hooks throw "not implemented" until their ticket.
assert.throws(() => useSimulate(), /not implemented/);
assert.throws(() => useChat(), /not implemented/);

console.log("plumbing checks passed");
