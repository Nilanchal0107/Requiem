import { useRef, useState } from "react"
import { ExternalLink, Send } from "lucide-react"
import type { Report } from "@/api"
import { FigureText } from "@/components/FigureText"
import { Button } from "@/components/ui/button"
import { Sheet, SheetContent, SheetHeader, SheetTitle } from "@/components/ui/sheet"
import { useChat } from "@/hooks/useChat"
import { useLang, useT } from "@/i18n"
import type { Lang } from "@/i18n/resolve"
import { changeText } from "@/pages/report/ExplanationTab"
import type { components } from "@/types/contracts"

type Change = components["schemas"]["Change"]
type ChatResponse = components["schemas"]["ChatResponse"]
type Figure = components["schemas"]["Figure"]

export type ChatSheetProps = {
  open: boolean
  onOpenChange: (open: boolean) => void
  report: Report
  onOpenFigure: (figure: Figure, lang: Lang) => void
  /** "Try it" on a suggested change: the page closes this sheet and opens the what-if sheet with it. */
  onTry: (change: Change) => void
}

type Message = { role: "user" | "assistant"; content: string; reply?: ChatResponse }

const STARTERS = [1, 2, 3]
const HISTORY_TURNS = 10

// Bottom sheet on a phone, side panel from sm up.
const PANEL = "h-[90dvh] sm:inset-x-auto sm:inset-y-0 sm:right-0 sm:h-full sm:w-96 sm:max-w-sm sm:border-t-0 sm:border-l"

function Reply({ reply, report, onOpenFigure, onTry }: { reply: ChatResponse } & Pick<ChatSheetProps, "report" | "onOpenFigure" | "onTry">) {
  const t = useT()
  const lang = useLang()
  // Figures from the chat's own simulate call sit beside the report's.
  const figures = { ...report.engine?.figures, ...reply.figures }
  return (
    <div className="flex flex-col gap-2">
      <p>
        <FigureText text={reply.reply} figures={figures} lang={lang} onOpen={(f) => onOpenFigure(f, lang)} />
      </p>
      {reply.citations.map((c) => (
        <a
          key={c.source_url}
          href={c.source_url}
          target="_blank"
          rel="noreferrer"
          className="flex min-h-12 items-center gap-2 rounded-lg border border-border-strong p-2 text-sm"
        >
          <ExternalLink aria-hidden="true" className="size-4 shrink-0" />
          <span>
            <span className="font-semibold">{t("report.chat.source")}</span>: {c.snippet}
          </span>
        </a>
      ))}
      {reply.suggested_changes.length > 0 && <p className="text-sm text-text-muted">{t("report.chat.suggested")}</p>}
      {reply.suggested_changes.map((c) => (
        <div key={c.field} className="flex items-center justify-between gap-2 rounded-card border border-border-strong p-2">
          <div>
            <p className="text-sm">{changeText(c, t, lang)}</p>
            <p className="text-sm font-semibold text-ok">→ {t(`verdict.${c.resulting_verdict}`)}</p>
          </div>
          <Button variant="outline" className="h-12 shrink-0" onClick={() => onTry(c)}>
            {t("report.path.try")}
          </Button>
        </div>
      ))}
    </div>
  )
}

export function ChatSheet({ open, onOpenChange, report, onOpenFigure, onTry }: ChatSheetProps) {
  const t = useT()
  const lang = useLang()
  const chat = useChat()
  // The sheet stays mounted while closed, so the conversation survives closing and reopening.
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState("")
  const [busy, setBusy] = useState(false)
  const [failed, setFailed] = useState(false)
  const end = useRef<HTMLDivElement>(null)

  async function send(text: string) {
    const message = text.trim()
    if (!message || busy) return
    const history = messages.slice(-HISTORY_TURNS).map(({ role, content }) => ({ role, content }))
    setMessages((m) => [...m, { role: "user", content: message }])
    setInput("")
    setBusy(true)
    setFailed(false)
    try {
      const reply = await chat({ report_id: report.id, message, language: lang, history })
      setMessages((m) => [...m, { role: "assistant", content: reply.reply, reply }])
    } catch {
      // The question goes back in the box so it can be sent again.
      setMessages((m) => m.slice(0, -1))
      setInput(message)
      setFailed(true)
    } finally {
      setBusy(false)
      setTimeout(() => end.current?.scrollIntoView({ block: "end" }), 0)
    }
  }

  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent side="bottom" className={PANEL}>
        <SheetHeader>
          <SheetTitle>{t("report.chat.title")}</SheetTitle>
        </SheetHeader>
        <div className="flex flex-1 flex-col gap-3 overflow-y-auto px-4" aria-live="polite">
          {messages.length === 0 &&
            STARTERS.map((n) => (
              <Button key={n} variant="outline" className="h-auto min-h-12 justify-start whitespace-normal text-left" onClick={() => send(t(`report.chat.starter.${n}`))}>
                {t(`report.chat.starter.${n}`)}
              </Button>
            ))}
          {messages.map((m, i) =>
            m.reply ? (
              <Reply key={i} reply={m.reply} report={report} onOpenFigure={onOpenFigure} onTry={onTry} />
            ) : (
              <p key={i} className="self-end rounded-card bg-primary-soft p-2">
                {m.content}
              </p>
            ),
          )}
          {busy && <p className="text-sm text-text-muted">{t("report.chat.thinking")}</p>}
          {failed && (
            <p role="alert" className="text-sm text-destructive">
              {t("report.chat.error")}
            </p>
          )}
          <div ref={end} />
        </div>
        <form
          className="flex gap-2 p-4"
          onSubmit={(e) => {
            e.preventDefault()
            send(input)
          }}
        >
          <input
            aria-label={t("report.chat.placeholder")}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder={t("report.chat.placeholder")}
            className="h-12 min-w-0 flex-1 rounded-lg border border-border-strong bg-background px-3 text-base outline-none focus-visible:ring-[3px] focus-visible:ring-ring/50"
          />
          <Button type="submit" className="h-12 gap-2" disabled={busy || !input.trim()}>
            <Send aria-hidden="true" className="size-5" />
            {t("report.chat.send")}
          </Button>
        </form>
      </SheetContent>
    </Sheet>
  )
}
