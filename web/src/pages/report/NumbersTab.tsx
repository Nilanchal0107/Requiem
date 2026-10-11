import { TriangleAlert } from "lucide-react"
import { CashFlowChart } from "@/components/CashFlowChart"
import { CostBreakdownChart } from "@/components/CostBreakdownChart"
import { FigureChip } from "@/components/FigureChip"
import { MeansOfFinanceChart } from "@/components/MeansOfFinanceChart"
import { MetricRows } from "@/components/MetricRows"
import { RepaymentChart } from "@/components/RepaymentChart"
import { SourceBadge } from "@/components/SourceBadge"
import { useLang, useT } from "@/i18n"
import type { Lang } from "@/i18n/resolve"
import { formatValue } from "@/lib/format"
import { SchemeList } from "@/pages/report/SchemeList"
import type { components } from "@/types/contracts"

type EngineResult = components["schemas"]["EngineResult"]
type Figure = components["schemas"]["Figure"]

export type NumbersTabProps = {
  engine: EngineResult
  onOpenFigure: (figure: Figure, lang: Lang) => void
}

// Plain words only: the jargon (DSCR, break-even) stays in the Bank DPR tab.
export function NumbersTab({ engine, onOpenFigure }: NumbersTabProps) {
  const t = useT()
  const lang = useLang()
  const n = (template: string, value: number) => template.replace("{n}", formatValue(value, "ratio", lang))
  // Each row: the number as a tappable chip (opens "Why this number?") and its Source Badge.
  const row = (label: string, figure: Figure, text?: string) => ({
    label,
    values: [
      <>
        <FigureChip figure={figure} lang={lang} text={text} onOpen={() => onOpenFigure(figure, lang)} />
        <SourceBadge source={figure.source} />
      </>,
    ],
  })
  const { market } = engine
  return (
    <div className="flex flex-col gap-6">
      <MeansOfFinanceChart finance={engine.finance} lang={lang} />
      <CostBreakdownChart cost={engine.cost} lang={lang} />
      <CashFlowChart projections={engine.projections} lang={lang} />
      <RepaymentChart rows={engine.repayment} lang={lang} />
      <section className="flex flex-col gap-2">
        <h2 className="text-h3">{t("report.numbers.key")}</h2>
        <MetricRows
          rows={[
            row(t("report.key.dscr"), engine.min_dscr, n(t("report.key.dscrValue"), engine.min_dscr.value)),
            row(t("report.key.breakEven"), engine.break_even_month, n(t("report.key.monthN"), engine.break_even_month.value)),
            row(t("report.key.payback"), engine.payback_months, n(t("report.key.months"), engine.payback_months.value)),
            row(t("report.key.households"), market.households),
            row(t("report.key.competitors"), market.competitors),
          ]}
        />
        {market.competitor_coverage === "low" && (
          <p role="note" className="flex items-start gap-2 rounded-card border border-warn bg-warn-soft p-3 text-sm text-warn">
            <TriangleAlert aria-hidden="true" className="mt-0.5 size-5 shrink-0" />
            {t("report.fewShops")}
          </p>
        )}
      </section>
      <SchemeList schemes={engine.schemes} />
    </div>
  )
}
