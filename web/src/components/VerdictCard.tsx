import type { components } from "@/types/contracts"

type Verdict = components["schemas"]["Verdict"]
type Figure = components["schemas"]["Figure"]

export type VerdictCardProps = {
  verdict: Verdict
  loan: Figure
  emi: Figure
  schemeName: string | null
  onSeePath?: () => void
}

export function VerdictCard(_props: VerdictCardProps) {
  return <div className="text-xs text-muted-foreground">VerdictCard</div>
}
