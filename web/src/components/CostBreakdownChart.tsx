import { ChartFrame } from "@/components/ChartFrame"
import { useT } from "@/i18n"
import type { Lang } from "@/i18n/resolve"
import { formatCompact, formatInr } from "@/lib/format"
import type { components } from "@/types/contracts"

export type CostBreakdownChartProps = {
  cost: components["schemas"]["CostBreakdown"]
  lang: Lang
}

// Horizontal bars drawn with widths, largest first. Working capital is not a cost item: the engine lists it as an input of Project Cost.
export function CostBreakdownChart({ cost, lang }: CostBreakdownChartProps) {
  const t = useT()
  const working = cost.project_cost.inputs?.working_capital
  const bars = [
    ...cost.items.map((item) => ({ name: t(`figure.label.${item.figure.id}`, item.name), value: item.figure.value })),
    ...(working ? [{ name: t("report.chart.working"), value: working }] : []),
  ].sort((a, b) => b.value - a.value)
  const max = Math.max(...bars.map((b) => b.value), 1)
  const chart = (
    <ul className="flex flex-col gap-3">
      {bars.map((b) => (
        <li key={b.name} className="flex flex-col gap-1">
          <div className="flex justify-between gap-2 text-sm">
            <span>{b.name}</span>
            <span className="font-semibold tabular-nums">{formatCompact(b.value, lang)}</span>
          </div>
          <div className="h-3 rounded-full bg-surface-soft">
            <div className="h-3 rounded-full bg-chart-1" style={{ width: `${(b.value / max) * 100}%` }} />
          </div>
        </li>
      ))}
    </ul>
  )
  return (
    <ChartFrame
      title={t("report.numbers.cost")}
      summary={t("report.chart.summary.cost")}
      chart={chart}
      head={[t("report.chart.item"), t("report.chart.amount")]}
      rows={[...bars.map((b) => [b.name, formatInr(b.value, lang)]), [t("report.chart.total"), formatInr(cost.project_cost.value, lang)]]}
    />
  )
}
