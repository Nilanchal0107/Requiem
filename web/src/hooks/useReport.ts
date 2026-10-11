import { useEffect, useState } from "react"
import { getReport, type Report } from "../api.ts"

/** Loads one report. `retry` refetches after an error. Callers render loading while `report` is null and `error` is false. */
export function useReport(id: string) {
  const [report, setReport] = useState<Report | null>(null)
  const [error, setError] = useState(false)
  const [attempt, setAttempt] = useState(0)

  useEffect(() => {
    let live = true
    setReport(null)
    setError(false)
    getReport(id)
      .then((r) => live && setReport(r))
      .catch(() => live && setError(true))
    // A late response for a previous id or attempt must not overwrite the current one.
    return () => {
      live = false
    }
  }, [id, attempt])

  return { report, error, retry: () => setAttempt((n) => n + 1) }
}
