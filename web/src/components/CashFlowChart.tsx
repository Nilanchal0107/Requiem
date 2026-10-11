import type { components } from "@/types/contracts"
import type { Lang } from "@/i18n/resolve"

export type CashFlowChartProps = {
  projections: components["schemas"]["YearProjection"][]
  lang: Lang
}

export function CashFlowChart(_props: CashFlowChartProps) {
  return <div className="text-xs text-muted-foreground">CashFlowChart</div>
}
