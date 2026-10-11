import type { components } from "@/types/contracts"

export type StageTraceProps = {
  events: components["schemas"]["StageEvent"][]
}

export function StageTrace(_props: StageTraceProps) {
  return <div className="text-xs text-muted-foreground">StageTrace</div>
}
