import { useEffect, useState } from "react"
import { listSchemes } from "../api.ts"

/** Scheme id -> `verified_on`. The report only carries each Scheme's terms, so the date comes from the catalogue. Empty until loaded or if it fails. */
export function useSchemeDates(): Record<string, string> {
  const [dates, setDates] = useState<Record<string, string>>({})
  useEffect(() => {
    let live = true
    listSchemes()
      .then((schemes) => live && setDates(Object.fromEntries(schemes.map((s) => [s.id, s.verified_on]))))
      .catch(() => {
        // The date is extra; the Scheme list reads fine without it.
      })
    return () => {
      live = false
    }
  }, [])
  return dates
}
