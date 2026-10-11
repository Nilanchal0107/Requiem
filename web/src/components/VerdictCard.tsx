import { CircleCheck, CircleX, Landmark, TriangleAlert, type LucideIcon } from "lucide-react"
import { FigureText } from "@/components/FigureText"
import { Button } from "@/components/ui/button"
import { useLang, useT } from "@/i18n"
import { formatHeadline } from "@/lib/format"
import { cn } from "@/lib/utils"
import { worstSignal } from "@/lib/verdict"
import type { components } from "@/types/contracts"

type Verdict = components["schemas"]["Verdict"]
type Figure = components["schemas"]["Figure"]

export type VerdictCardProps = {
  verdict: Verdict
  loan: Figure
  emi: Figure
  schemeName: string | null
  /** All the report's Figures, so the reason line can show its number as a chip. */
  figures?: Record<string, Figure>
  onOpenFigure?: (figure: Figure) => void
  /** Shown as a "See how to make it work" link when the Verdict is not feasible. */
  onSeePath?: () => void
}

// Icon + word + colour, never colour alone.
const TONE: Record<Verdict["level"], { icon: LucideIcon; card: string }> = {
  feasible: { icon: CircleCheck, card: "border-ok bg-ok-soft text-ok" },
  feasible_with_changes: { icon: TriangleAlert, card: "border-warn bg-warn-soft text-warn" },
  not_feasible: { icon: CircleX, card: "border-bad bg-bad-soft text-bad" },
}

export function VerdictCard({ verdict, loan, emi, schemeName, figures = {}, onOpenFigure, onSeePath }: VerdictCardProps) {
  const t = useT()
  const lang = useLang()
  const { icon: Icon, card } = TONE[verdict.level]
  const worst = worstSignal(verdict)
  return (
    <section className={cn("flex flex-col gap-3 rounded-card border p-4", card)}>
      <h1 className="flex items-center gap-2 text-h2">
        <Icon aria-hidden="true" className="size-7 shrink-0" />
        {t(`verdict.${verdict.level}`)}
      </h1>
      {worst && (
        <p className="text-body text-text">
          <FigureText text={t(`verdict.reason.${worst.name}.${worst.level}`)} figures={figures} lang={lang} onOpen={onOpenFigure} />
        </p>
      )}
      <dl className="grid grid-cols-2 gap-4 text-text">
        {[
          { label: t("verdict.loan"), figure: loan },
          { label: t("verdict.emi"), figure: emi },
        ].map(({ label, figure }) => (
          <div key={figure.id}>
            <dt className="text-sm text-text-muted">{label}</dt>
            <dd>
              <button
                type="button"
                onClick={() => onOpenFigure?.(figure)}
                className="min-h-12 text-left text-2xl font-bold tabular-nums underline decoration-dotted decoration-2 underline-offset-4"
              >
                {formatHeadline(figure, lang)}
              </button>
            </dd>
          </div>
        ))}
      </dl>
      <p className="flex items-center gap-2 text-sm text-text">
        <Landmark aria-hidden="true" className="size-5 shrink-0" />
        {schemeName ?? t("verdict.noScheme")}
      </p>
      {verdict.level !== "feasible" && onSeePath && (
        <Button variant="link" className="h-12 justify-start px-0 text-primary" onClick={onSeePath}>
          {t("verdict.seePath")} ↓
        </Button>
      )}
    </section>
  )
}
