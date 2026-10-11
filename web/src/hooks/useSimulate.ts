import { postJson } from "../api.ts"
import type { components } from "../types/contracts.ts"

type IntakeInput = components["schemas"]["IntakeInput"]
type EngineResult = components["schemas"]["EngineResult"]

/** Returns a function that POSTs a what-if IntakeInput to /api/simulate. */
export function useSimulate(): (input: IntakeInput) => Promise<EngineResult> {
  return (input) => postJson<EngineResult>("/api/simulate", input)
}
