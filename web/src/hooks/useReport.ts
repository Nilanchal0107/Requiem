import { useEffect, useRef, useState } from "react"
import { getReport, rewriteExplanation, type Report } from "../api.ts"
import { useLang } from "../i18n/index.ts"

type Result = { key: string; report: Report | null; error: boolean }

/**
 * Loads one report. `retry` refetches after an error. Callers render loading while `report` is null and `error` is false.
 * A report without an explanation, or with one in another language than the one chosen, gets one written live, once per
 * load and language; `writing` is true meanwhile and `rewrite` asks again.
 */
export function useReport(id: string) {
  const lang = useLang()
  const [attempt, setAttempt] = useState(0)
  const [result, setResult] = useState<Result>({ key: "", report: null, error: false })
  const [writing, setWriting] = useState(false)
  const autoWritten = useRef("")
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
  const report = current ? result.report : null

  const rewrite = () => {
    setWriting(true)
    rewriteExplanation(id, lang)
      .then((next) => setResult((r) => (r.key === key ? { ...r, report: next } : r)))
      .catch(() => {}) // the unavailable card (or the old language) stays, with its Try again button
      .finally(() => setWriting(false))
  }

  const explanation = report?.explanation
  const needed = !!report?.engine && (!explanation?.available || explanation.language !== lang)
  useEffect(() => {
    // Once per load and language, so a failed write (offline, replay cache miss) does not loop.
    if (!needed || writing || autoWritten.current === `${key}@${lang}`) return
    autoWritten.current = `${key}@${lang}`
    rewrite()
  })

  return {
    report,
    error: current && result.error,
    retry: () => setAttempt((n) => n + 1),
    writing,
    rewrite,
  }
}
