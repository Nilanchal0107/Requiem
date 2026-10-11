import { postJson } from "../api.ts"
import type { components } from "../types/contracts.ts"

type CompareRequest = components["schemas"]["CompareRequest"]
type Comparison = components["schemas"]["Comparison"]

/** Returns a function that POSTs archetype ids to /api/compare. */
export function useCompare(): (request: CompareRequest) => Promise<Comparison> {
  return (request) => postJson<Comparison>("/api/compare", request)
}
