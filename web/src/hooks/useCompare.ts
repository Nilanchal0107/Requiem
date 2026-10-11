import type { components } from "../types/contracts.ts"

type CompareRequest = components["schemas"]["CompareRequest"]
type Comparison = components["schemas"]["Comparison"]

// Declared in V1, implemented in V2. Calling the hook throws until then.
/** Returns a function that POSTs archetype ids to /api/compare. */
export function useCompare(): (_request: CompareRequest) => Promise<Comparison> {
  throw new Error("useCompare: not implemented")
}
