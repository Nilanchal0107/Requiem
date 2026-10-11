import type { components } from "@/types/contracts"

export type SourceBadgeProps = {
  source: components["schemas"]["Figure"]["source"]
}

export function SourceBadge(_props: SourceBadgeProps) {
  return <span className="text-xs text-muted-foreground">SourceBadge</span>
}
