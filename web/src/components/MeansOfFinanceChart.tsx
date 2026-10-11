import { ChartFrame } from "@/components/ChartFrame"
import { useT } from "@/i18n"
import type { Lang } from "@/i18n/resolve"
import { formatCompact, formatInr } from "@/lib/format"
import type { components } from "@/types/contracts"

export type MeansOfFinanceChartProps = {
  finance: components["schemas"]["MeansOfFinance"]
  lang: Lang
}

// One stacked bar drawn with flex widths. The labels sit under it in a list, so nothing clips at 360 px.
export function MeansOfFinanceChart({ finance, lang }: MeansOfFinanceChartProps) {
  const t = useT()
  const parts = [
    { key: "you", label: t("report.chart.you"), value: finance.own_contribution.value, color: "bg-chart-1" },
    { key: "loan", label: t("report.chart.loan"), value: finance.loan.value, color: "bg-chart-2" },
    { key: "subsidy", label: t("report.chart.subsidy"), value: finance.subsidy.value, color: "bg-chart-3" },
  ]
  const shown = parts.filter((p) => p.value > 0)
  const total = shown.reduce((sum, p) => sum + p.value, 0)
  const chart = (
    <div className="flex flex-col gap-3">
      <div className="flex h-8 w-full overflow-hidden rounded-control">
        {shown.map((p) => (
          <div key={p.key} className={p.color} style={{ width: `${(p.value / total) * 100}%` }} />
        ))}
      </div>
      <ul className="flex flex-col gap-1 text-sm">
        {shown.map((p) => (
          <li key={p.key} className="flex items-center gap-2">
            <span aria-hidden="true" className={`size-3 rounded-full ${p.color}`} />
            <span className="flex-1">{p.label}</span>
            <span className="font-semibold tabular-nums">{formatCompact(p.value, lang)}</span>
          </li>
        ))}
      </ul>
      {finance.subsidy_backended && finance.subsidy.value > 0 && <p className="text-sm text-text-muted">{t("report.chart.subsidyLater")}</p>}
    </div>
  )
  return (
    <ChartFrame
      title={t("report.numbers.money")}
      summary={t("report.chart.summary.money")}
      chart={chart}
      head={[t("report.chart.item"), t("report.chart.amount")]}
      rows={[...shown.map((p) => [p.label, formatInr(p.value, lang)]), [t("report.chart.total"), formatInr(total, lang)]]}
    />
  )
}
