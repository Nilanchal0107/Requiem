// Runnable check for the non-trivial plumbing: i18n fallback, request<T>, and the shell hooks.
// Run: npm run check
import assert from "node:assert/strict";
import { translate, type Catalog, type Lang } from "../src/i18n/resolve.ts";
import { ApiError, getReport, login, listReports, request } from "../src/api.ts";
import { parseTab } from "../src/pages/report/tab.ts";
import { formatCompact, formatDate, formatFigure, formatHeadline, formatInr, formatMoneyWords } from "../src/lib/format.ts";
import { whatChanged, worstSignal } from "../src/lib/verdict.ts";
import { safeNext } from "../src/lib/next.ts";
import { shareLink } from "../src/lib/share.ts";
import { useSimulate } from "../src/hooks/useSimulate.ts";
import { useChat } from "../src/hooks/useChat.ts";
import { useCompare } from "../src/hooks/useCompare.ts";
import { createReport, openReportStream } from "../src/hooks/useReportStream.ts";
import { EMPTY_DRAFT, clearDraft, firstBadStep, loadDraft, saveDraft, toIntake, validate } from "../src/pages/new/draft.ts";

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
// Headline: lakh words from one lakh up, exact rupees below; chart label and date forms.
assert.equal(formatHeadline(figure, "en"), "₹4.17 lakh");
assert.equal(formatHeadline({ ...figure, value: 9632 }, "en"), "₹9,632");
assert.equal(formatHeadline({ ...figure, value: 9632 }, "mr"), "₹९,६३२");
assert.equal(formatInr(1234567, "en"), "₹12,34,567");
assert.equal(formatCompact(164600, "en"), "₹1.6L");
assert.equal(formatCompact(164600, "hi").replace(/\s/g, " "), "₹१.६ लाख"); // ICU puts a no-break space before the word
assert.equal(formatDate("2026-10-11", "en"), "11 Oct 2026");

// worstSignal: the worst level explains the Verdict; the first one wins a tie; no signals gives null.
const sig = (name: "dscr" | "market_gap" | "payback" | "scheme", level: "feasible" | "feasible_with_changes" | "not_feasible") => ({ name, level, figure_id: null });
assert.equal(worstSignal({ level: "feasible", signals: [] }), null);
assert.equal(worstSignal({ level: "not_feasible", signals: [sig("dscr", "feasible"), sig("payback", "not_feasible"), sig("scheme", "feasible_with_changes")] })!.name, "payback");
assert.equal(worstSignal({ level: "feasible_with_changes", signals: [sig("dscr", "feasible_with_changes"), sig("scheme", "feasible_with_changes")] })!.name, "dscr");

// shareLink: native sheet when present; copy the link when it is missing or fails; a closed sheet copies nothing.
const page = { title: "DPR", url: "https://x/reports/1?tab=bank" };
const copied: string[] = [];
const clipboard = { writeText: async (text: string) => void copied.push(text) };
assert.equal(await shareLink({ share: async () => {}, clipboard }, page), "shared");
assert.equal(await shareLink({ clipboard }, page), "copied");
assert.deepEqual(copied, [page.url]);
assert.equal(await shareLink({ share: async () => { throw new Error("denied"); }, clipboard }, page), "copied");
const abort = Object.assign(new Error("closed"), { name: "AbortError" });
assert.equal(await shareLink({ share: async () => { throw abort; }, clipboard }, page), "cancelled");
assert.equal(copied.length, 2);

// useSimulate: POSTs the changed intake to /api/simulate and returns the EngineResult.
reply = new Response(JSON.stringify({ archetype_id: "dairy" }), { status: 200, headers: { "content-type": "application/json" } });
assert.deepEqual(await useSimulate()({ own_contribution: 150000 } as never), { archetype_id: "dairy" });
assert.equal(seen.at(-1)!.url, "/api/simulate");
assert.equal(seen.at(-1)!.init.body, JSON.stringify({ own_contribution: 150000 }));

// whatChanged: flags a switched Scheme and a switched Verdict, and nothing when both hold.
const result = (scheme: string | null, level: string) =>
  ({ schemes: { best: scheme && { scheme_id: scheme } }, verdict: { level } }) as never;
assert.deepEqual(whatChanged(result("mudra", "feasible"), result("mudra", "feasible")), { scheme: false, verdict: false });
assert.deepEqual(whatChanged(result("mudra", "not_feasible"), result("pmegp", "feasible")), { scheme: true, verdict: true });
assert.deepEqual(whatChanged(result(null, "feasible"), result("mudra", "feasible")), { scheme: true, verdict: false });

// Wizard draft: each step names what is missing, the draft survives a reload, and the intake matches the entries.
const needs = ["age", "gender", "social_category", "education"];
assert.deepEqual(Object.keys(validate(0, EMPTY_DRAFT, needs)), ["village"]);
assert.deepEqual(Object.keys(validate(3, EMPTY_DRAFT, needs)), ["gender", "social_category", "education"]);
assert.deepEqual(Object.keys(validate(3, EMPTY_DRAFT, ["age"])), [], "only the Archetype's fields are asked");
assert.equal(firstBadStep(EMPTY_DRAFT, needs), 0);
const filled = {
  ...EMPTY_DRAFT,
  village_code: "FX1002",
  archetype_id: "dairy",
  unit_scale: 5,
  own_contribution: 0,
  eligibility: { ...EMPTY_DRAFT.eligibility, gender: "female", social_category: "obc", education: "10th_pass" },
} as const;
assert.equal(firstBadStep(filled, needs), null, "₹0 Own Contribution is a valid entry");
const intake = toIntake(filled, "mr");
assert.deepEqual([intake.village_code, intake.archetype_id, intake.unit_scale, intake.own_contribution, intake.language], ["FX1002", "dairy", 5, 0, "mr"]);
assert.equal(intake.eligibility.gender, "female");
const mem = new Map<string, string>();
const store = { getItem: (k: string) => mem.get(k) ?? null, setItem: (k: string, v: string) => void mem.set(k, v), removeItem: (k: string) => void mem.delete(k) };
saveDraft({ ...filled, step: 2 }, store);
assert.equal(loadDraft(store).step, 2);
assert.equal(loadDraft(store).village_code, "FX1002");
clearDraft(store);
assert.deepEqual(loadDraft(store), EMPTY_DRAFT);
mem.set("requiem.wizardDraft", "{broken");
assert.deepEqual(loadDraft(store), EMPTY_DRAFT, "a corrupt draft starts fresh");

// safeNext: only same-site paths survive; anything else falls back to home.
assert.equal(safeNext("/reports/r-1?tab=bank"), "/reports/r-1?tab=bank");
for (const bad of [null, "", "https://evil.example", "//evil.example", "/\\evil.example", "reports"]) assert.equal(safeNext(bad), "/");

// Declared stubs: the V2 hooks throw "not implemented" until their ticket.
assert.throws(() => useChat(), /not implemented/);

console.log("plumbing checks passed");
