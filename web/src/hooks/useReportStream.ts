import { useEffect, useRef, useState } from "react"
import { postJson } from "../api.ts"
import type { components } from "../types/contracts.ts"

type IntakeInput = components["schemas"]["IntakeInput"]
type ReportCreated = components["schemas"]["ReportCreated"]
type StageEvent = components["schemas"]["StageEvent"]

export type StreamHandlers = {
  onStage: (event: StageEvent) => void
  onDone: (reportId: string) => void
  onError: () => void
}

/** POSTs an intake and returns the new report id. */
export async function createReport(intake: IntakeInput): Promise<string> {
  return (await postJson<ReportCreated>("/api/reports", intake)).report_id
}

// Custom SSE event names are typed as plain Event, but the payload is still MessageEvent JSON.
const payload = (e: Event) => JSON.parse((e as MessageEvent).data)

/** Opens the SSE stream for a report and returns a function that closes it. */
export function openReportStream(reportId: string, handlers: StreamHandlers): () => void {
  const source = new EventSource(`/api/reports/${reportId}/stream`)
  source.addEventListener("stage", (e) => handlers.onStage(payload(e)))
  // Close before the handler: the server ends the stream after `done`, which would otherwise fire onerror.
  source.addEventListener("done", (e) => {
    source.close()
    handlers.onDone(payload(e).report_id)
  })
  source.onerror = () => {
    source.close()
    handlers.onError()
  }
  return () => source.close()
}

/** Creates a report and follows its stage events. The page owns navigation; this hook only reports state. */
export function useReportStream() {
  const [events, setEvents] = useState<StageEvent[]>([])
  const [reportId, setReportId] = useState<string | null>(null)
  const [failed, setFailed] = useState(false)
  const close = useRef<() => void>(() => {})

  useEffect(() => () => close.current(), [])

  async function start(intake: IntakeInput) {
    close.current()
    setEvents([])
    setReportId(null)
    setFailed(false)
    try {
      const id = await createReport(intake)
      close.current = openReportStream(id, {
        onStage: (event) => setEvents((prev) => [...prev, event]),
        onDone: setReportId,
        onError: () => setFailed(true),
      })
    } catch {
      setFailed(true)
    }
  }

  return { start, events, reportId, failed }
}
