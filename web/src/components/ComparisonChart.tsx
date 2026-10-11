import type { components } from "@/types/contracts"
import type { Lang } from "@/i18n/resolve"

export type ComparisonChartProps = {
  results: components["schemas"]["EngineResult"][]
  lang: Lang
}

export function ComparisonChart(_props: ComparisonChartProps) {
  return <div className="text-xs text-muted-foreground">ComparisonChart</div>
}
