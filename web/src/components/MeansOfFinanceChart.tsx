import type { components } from "@/types/contracts"
import type { Lang } from "@/i18n/resolve"

export type MeansOfFinanceChartProps = {
  finance: components["schemas"]["MeansOfFinance"]
  lang: Lang
}

export function MeansOfFinanceChart(_props: MeansOfFinanceChartProps) {
  return <div className="text-xs text-muted-foreground">MeansOfFinanceChart</div>
}
