import type { components } from "../types/contracts.ts"

type IntakeInput = components["schemas"]["IntakeInput"]
type EngineResult = components["schemas"]["EngineResult"]

// Declared in V1, implemented in V2. Calling the hook throws until then.
/** Returns a function that POSTs a what-if IntakeInput to /api/simulate. */
export function useSimulate(): (_input: IntakeInput) => Promise<EngineResult> {
  throw new Error("useSimulate: not implemented")
}
