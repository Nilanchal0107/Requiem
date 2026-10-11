import { CircleCheck, LoaderCircle } from "lucide-react"
import { ExplanationUnavailable } from "@/components/ExplanationUnavailable"
import { FigureText } from "@/components/FigureText"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import { useLang, useT } from "@/i18n"
import type { Lang } from "@/i18n/resolve"
import { formatValue } from "@/lib/format"
import { NumbersTab } from "@/pages/report/NumbersTab"
import type { components } from "@/types/contracts"

type Explanation = components["schemas"]["Explanation"]
type EngineResult = components["schemas"]["EngineResult"]
type Figure = components["schemas"]["Figure"]
type Change = components["schemas"]["Change"]

export type ExplanationTabProps = {
  explanation: Explanation | null
  engine: EngineResult
  onOpenFigure: (figure: Figure, lang: Lang) => void
  /** True while the explanation is being written live. */
  writing: boolean
  /** Writes the explanation again. */
  onRetry: () => void
  /** "Try it" on a Path to Yes card. */
  onTry: (change: Change) => void
}

// The numbers in a Path to Yes card come straight from the engine, so they are formatted here, never written by the LLM.
export function changeText(c: Change, t: (key: string) => string, lang: Lang): string {
  const unit = c.field === "own_contribution" ? "INR" : "count"
  return t(`report.path.${c.field}`)
    .replace("{delta}", formatValue(c.to_value - c.from_value, "INR", lang))
    .replace("{from}", formatValue(c.from_value, unit, lang))
    .replace("{to}", formatValue(c.to_value, unit, lang))
}

function PathToYes({ changes, onTry }: { changes: Change[]; onTry: (change: Change) => void }) {
  const t = useT()
  const lang = useLang()
  const text = (c: Change) => changeText(c, t, lang)
  return (
    <section id="path-to-yes" className="flex scroll-mt-20 flex-col gap-2">
      <h2 className="text-base font-semibold">{t("report.path.title")}</h2>
      <ul className="flex flex-col gap-2">
        {changes.map((c) => (
          <li key={c.field} className="flex items-center justify-between gap-2 rounded-card border border-border bg-surface p-3">
            <div className="flex flex-col gap-1">
              <p className="text-sm">{text(c)}</p>
              <p className="text-sm font-semibold text-ok">→ {t(`verdict.${c.resulting_verdict}`)}</p>
            </div>
            <Button variant="outline" className="h-12 shrink-0" onClick={() => onTry(c)}>
              {t("report.path.try")}
            </Button>
          </li>
        ))}
      </ul>
    </section>
  )
}

export function ExplanationTab({ explanation, engine, onOpenFigure, writing, onRetry, onTry }: ExplanationTabProps) {
  const t = useT()
  const path = engine.path_to_yes?.changes.length ? <PathToYes changes={engine.path_to_yes.changes} onTry={onTry} /> : null
  if (!explanation || !explanation.available) {
    // The numbers don't depend on the LLM, so they all still show.
    return (
      <div className="flex flex-col gap-4">
        {writing ? (
          <div role="status" aria-live="polite" className="flex flex-col gap-3 rounded-card border border-border bg-surface p-4">
            <p className="flex items-start gap-2 text-body">
              <LoaderCircle aria-hidden="true" className="mt-1 size-5 shrink-0 animate-spin text-primary" />
              {t("report.explanationWriting")}
            </p>
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-4 w-5/6" />
            <Skeleton className="h-4 w-2/3" />
          </div>
        ) : (
          <ExplanationUnavailable onRetry={onRetry} />
        )}
        {path}
        <NumbersTab engine={engine} onOpenFigure={onOpenFigure} />
      </div>
    )
  }
  // Digits follow the language of the text, not the app bar, so a Marathi explanation never mixes scripts.
  const lang = explanation.language
  const count = (n: number) => formatValue(n, "count", lang)
  const text = (value: string) => <FigureText text={value} figures={engine.figures} lang={lang} onOpen={(f) => onOpenFigure(f, lang)} />
  const swot = explanation.swot
  const lists = [
    { title: t("report.swot.good"), items: [...swot.strengths, ...swot.opportunities] },
    { title: t("report.swot.watch"), items: [...swot.weaknesses, ...swot.threats] },
  ]
  const [main, rest] = [explanation.sections.filter((s) => s.key !== "next_steps"), explanation.sections.filter((s) => s.key === "next_steps")]
  const section = (s: (typeof main)[number]) => (
    <li key={s.key} className="flex flex-col gap-1">
      <h2 className="text-base font-semibold">{s.title}</h2>
      <p className="text-sm leading-relaxed">{text(s.text)}</p>
    </li>
  )
  return (
    <div className="flex flex-col gap-4">
      {writing && (
        <p role="status" aria-live="polite" className="flex items-center gap-2 rounded-card border border-border bg-surface p-3 text-sm">
          <LoaderCircle aria-hidden="true" className="size-5 shrink-0 animate-spin text-primary" />
          {t("report.explanationTranslating")}
        </p>
      )}
      <p className="flex items-center gap-2 text-sm text-text-muted">
        <CircleCheck aria-hidden="true" className="size-5 text-ok" />
        {t("figure.checked")}: {count(explanation.verified)}/{count(explanation.total)}
      </p>
      <ul className="flex flex-col gap-4">{main.map(section)}</ul>
      <div className="grid grid-cols-1 gap-4 min-[400px]:grid-cols-2">
        {lists.map(({ title, items }) => (
          <section key={title} className="flex flex-col gap-1">
            <h2 className="text-base font-semibold">{title}</h2>
            <ul className="list-disc pl-5 text-sm">
              {items.map((item, i) => (
                <li key={i}>{text(item)}</li>
              ))}
            </ul>
          </section>
        ))}
      </div>
      {path}
      <ul className="flex flex-col gap-4">{rest.map(section)}</ul>
      <p className="text-sm text-text-muted">{t("report.disclaimer")}</p>
    </div>
  )
}
