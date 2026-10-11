import type { components } from "./types/contracts.ts";

export type ArchetypeSummary = components["schemas"]["ArchetypeSummary"];

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

export function listArchetypes(): Promise<ArchetypeSummary[]> {
  return request<ArchetypeSummary[]>("/api/archetypes");
}
