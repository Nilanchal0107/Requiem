import type { components } from "@/types/contracts"
import type { Lang } from "@/i18n/resolve"

export type RepaymentChartProps = {
  rows: components["schemas"]["RepaymentRow"][]
  lang: Lang
}

export function RepaymentChart(_props: RepaymentChartProps) {
  return <div className="text-xs text-muted-foreground">RepaymentChart</div>
}
