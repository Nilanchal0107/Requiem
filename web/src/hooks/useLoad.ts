import { useEffect, useState } from "react"

type Result<T> = { key: string; items: T | null; error: boolean }

/** Runs `load` whenever `deps` change (null skips it). Callers render loading while `items` is null and `error` is false. */
export function useLoad<T>(load: (() => Promise<T>) | null, depKey: string) {
  const [attempt, setAttempt] = useState(0)
  const [result, setResult] = useState<Result<T>>({ key: "", items: null, error: false })
  const key = `${depKey}#${attempt}`

  useEffect(() => {
    if (!load) return
    let live = true
    load()
      .then((items) => live && setResult({ key, items, error: false }))
      .catch(() => live && setResult({ key, items: null, error: true }))
    return () => {
      live = false
    }
    // `load` is a fresh closure each render; `key` already names what it loads.
  }, [key])

  const current = load !== null && result.key === key
  return { items: current ? result.items : null, error: current && result.error, retry: () => setAttempt((n) => n + 1) }
}
