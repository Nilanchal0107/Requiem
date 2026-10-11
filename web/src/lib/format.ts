import type { components } from "../types/contracts.ts"
import type { Lang } from "../i18n/resolve.ts"

type Figure = components["schemas"]["Figure"]

// Declared in V1, implemented in V2. Signatures are final; calling them throws until then.

/** Formats a Figure's value: Indian grouping (en-IN), Devanagari digits for hi/mr (-u-nu-deva). Bank View always passes "en". */
export function formatFigure(_figure: Figure, _lang: Lang): string {
  throw new Error("formatFigure: not implemented")
}

/** Words line under a money input: "₹1 lakh" / "₹1 लाख". */
export function formatMoneyWords(_amount: number, _lang: Lang): string {
  throw new Error("formatMoneyWords: not implemented")
}
