import { useEffect, useState } from "react"
import { getReport, type Report } from "../api.ts"

type Result = { key: string; report: Report | null; error: boolean }

/** Loads one report. `retry` refetches after an error. Callers render loading while `report` is null and `error` is false. */
export function useReport(id: string) {
  const [attempt, setAttempt] = useState(0)
  const [result, setResult] = useState<Result>({ key: "", report: null, error: false })
  // Results are tagged with the id and attempt they belong to, so a new id never shows the old report.
  const key = `${id}#${attempt}`

  useEffect(() => {
    let live = true
    getReport(id)
      .then((report) => live && setResult({ key, report, error: false }))
      .catch(() => live && setResult({ key, report: null, error: true }))
    // A late response for a previous id or attempt must not overwrite the current one.
    return () => {
      live = false
    }
  }, [id, attempt, key])

  const current = result.key === key
  return {
    report: current ? result.report : null,
    error: current && result.error,
    retry: () => setAttempt((n) => n + 1),
  }
}
