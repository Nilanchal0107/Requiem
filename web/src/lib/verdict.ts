import type { components } from "../types/contracts.ts"

type EngineResult = components["schemas"]["EngineResult"]
type Verdict = components["schemas"]["Verdict"]
type Signal = Verdict["signals"][number]

const SEVERITY: Record<Verdict["level"], number> = { feasible: 0, feasible_with_changes: 1, not_feasible: 2 }

/** The signal that explains the Verdict: the worst level, first one on a tie. Null when there are no signals. */
export function worstSignal(verdict: Verdict): Signal | null {
  return verdict.signals.reduce<Signal | null>((worst, s) => (!worst || SEVERITY[s.level] > SEVERITY[worst.level] ? s : worst), null)
}

/** What a what-if changed against the original result: the best Scheme and the Verdict level. */
export const whatChanged = (before: EngineResult, after: EngineResult) => ({
  scheme: before.schemes.best?.scheme_id !== after.schemes.best?.scheme_id,
  verdict: before.verdict.level !== after.verdict.level,
})
