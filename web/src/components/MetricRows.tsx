import type { ReactNode } from "react"

export type MetricRowsProps = {
  rows: { label: string; values: ReactNode[]; betterIndex?: number }[]
}

export function MetricRows(_props: MetricRowsProps) {
  return <div className="text-xs text-muted-foreground">MetricRows</div>
}
