import type { components } from "@/types/contracts"
import type { Lang } from "@/i18n/resolve"

export type CostBreakdownChartProps = {
  cost: components["schemas"]["CostBreakdown"]
  lang: Lang
}

export function CostBreakdownChart(_props: CostBreakdownChartProps) {
  return <div className="text-xs text-muted-foreground">CostBreakdownChart</div>
}
