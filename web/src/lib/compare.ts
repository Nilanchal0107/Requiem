import type { components } from "../types/contracts.ts"

type EngineResult = components["schemas"]["EngineResult"]
type Figure = components["schemas"]["Figure"]

/** Index of the better value, or undefined on a tie (nothing to mark). */
export function betterIndex(values: number[], best: "max" | "min"): number | undefined {
  const target = Math[best](...values)
  const at = values.flatMap((v, i) => (v === target ? [i] : []))
  return at.length === 1 ? at[0] : undefined
}

// The summary's placeholders are "<archetype_id>.<figure_id>", so every result's Figures get the same prefix.
export const compareFigures = (results: EngineResult[]): Record<string, Figure> =>
  Object.fromEntries(results.flatMap((r) => Object.entries(r.figures).map(([id, f]) => [`${r.archetype_id}.${id}`, f])))
