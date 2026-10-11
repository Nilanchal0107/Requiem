import { Area, AreaChart, ResponsiveContainer, XAxis, YAxis } from "recharts"
import { ChartFrame } from "@/components/ChartFrame"
import { useT } from "@/i18n"
import type { Lang } from "@/i18n/resolve"
import { formatCompact, formatInr } from "@/lib/format"
import type { components } from "@/types/contracts"

export type RepaymentChartProps = {
  rows: components["schemas"]["RepaymentRow"][]
  lang: Lang
}

// Area of the balance still owed, month by month.
export function RepaymentChart({ rows, lang }: RepaymentChartProps) {
  const t = useT()
  const data = rows.map((r) => ({ month: r.month, balance: r.closing }))
  const chart = (
    <ResponsiveContainer width="100%" height={200}>
      <AreaChart data={data} margin={{ top: 8, right: 8, bottom: 0, left: 0 }}>
        <XAxis dataKey="month" type="number" domain={["dataMin", "dataMax"]} tickLine={false} tickCount={5} tick={{ fontSize: 14 }} />
        <YAxis width={56} tickCount={4} tickLine={false} tick={{ fontSize: 14 }} tickFormatter={(v) => formatCompact(Number(v), lang)} />
        <Area dataKey="balance" stroke="var(--chart-1)" fill="var(--chart-1)" fillOpacity={0.25} isAnimationActive={false} />
      </AreaChart>
    </ResponsiveContainer>
  )
  return (
    <ChartFrame
      title={t("report.numbers.repay")}
      summary={t("report.chart.summary.repay")}
      chart={chart}
      head={[t("report.chart.month"), t("report.chart.paid"), t("report.chart.balance")]}
      rows={rows.map((r) => [String(r.month), formatInr(r.payment, lang), formatInr(r.closing, lang)])}
    />
  )
}
