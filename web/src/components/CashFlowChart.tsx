import { Bar, BarChart, LabelList, ResponsiveContainer, XAxis } from "recharts"
import { ChartFrame } from "@/components/ChartFrame"
import { useT } from "@/i18n"
import type { Lang } from "@/i18n/resolve"
import { formatCompact, formatInr } from "@/lib/format"
import type { components } from "@/types/contracts"

export type CashFlowChartProps = {
  projections: components["schemas"]["YearProjection"][]
  lang: Lang
}

// One labelled column of profit per year. No entrance animation: cheaper on budget phones and fine for reduced motion.
export function CashFlowChart({ projections, lang }: CashFlowChartProps) {
  const t = useT()
  const data = projections.map((p) => ({ year: `${t("report.chart.year")} ${p.year}`, profit: p.net_profit }))
  const chart = (
    <ResponsiveContainer width="100%" height={200}>
      <BarChart data={data} margin={{ top: 20, right: 0, bottom: 0, left: 0 }}>
        <XAxis dataKey="year" tickLine={false} axisLine={false} interval={0} tick={{ fontSize: 14 }} />
        <Bar dataKey="profit" fill="var(--chart-1)" radius={[4, 4, 0, 0]} isAnimationActive={false}>
          <LabelList dataKey="profit" position="top" fontSize={14} formatter={(v) => formatCompact(Number(v), lang)} />
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  )
  return (
    <ChartFrame
      title={t("report.numbers.profit")}
      summary={t("report.chart.summary.profit")}
      chart={chart}
      head={[t("report.chart.year"), t("report.chart.profit"), t("report.chart.cash")]}
      rows={projections.map((p) => [String(p.year), formatInr(p.net_profit, lang), formatInr(p.cash_flow, lang)])}
    />
  )
}
