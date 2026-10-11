import type { components } from "./types/contracts.ts";

export type ArchetypeSummary = components["schemas"]["ArchetypeSummary"];
export type Credentials = components["schemas"]["Credentials"];
export type UserOut = components["schemas"]["UserOut"];
export type MeOut = components["schemas"]["MeOut"];
export type ReportSummary = components["schemas"]["ReportSummary"];

// Thrown for any non-2xx response; the shape matches what FastAPI sends back.
export class ApiError extends Error {
  status: number;
  detail: unknown;

  constructor(status: number, detail: unknown) {
    super(typeof detail === "string" ? detail : `Request failed with ${status}`);
    this.status = status;
    this.detail = detail;
  }
}

export async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const res = await fetch(path, { ...init, credentials: "include" });
  const body = (await res.json().catch(() => null)) as { detail?: unknown } | null;
  if (!res.ok) throw new ApiError(res.status, body?.detail ?? res.statusText);
  return body as T;
}

export function postJson<T>(path: string, body: unknown): Promise<T> {
  return request<T>(path, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(body),
  });
}

export function listArchetypes(): Promise<ArchetypeSummary[]> {
  return request<ArchetypeSummary[]>("/api/archetypes");
}

export function login(credentials: Credentials): Promise<UserOut> {
  return postJson<UserOut>("/api/auth/login", credentials);
}

export function register(credentials: Credentials): Promise<UserOut> {
  return postJson<UserOut>("/api/auth/register", credentials);
}

export function logout(): Promise<unknown> {
  return postJson("/api/auth/logout", {});
}

export function me(): Promise<MeOut> {
  return request<MeOut>("/api/auth/me");
}

export function listReports(): Promise<ReportSummary[]> {
  return request<ReportSummary[]>("/api/reports");
}
