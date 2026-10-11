import { VerdictCard } from "@/components/VerdictCard"
import type { components } from "@/types/contracts"

type EngineResult = components["schemas"]["EngineResult"]
type Figure = components["schemas"]["Figure"]

export type ReportHeaderProps = {
  engine: EngineResult
  onOpenFigure: (figure: Figure) => void
  onSeePath?: () => void
}

export function ReportHeader({ engine, onOpenFigure, onSeePath }: ReportHeaderProps) {
  return (
    <VerdictCard
      verdict={engine.verdict}
      loan={engine.finance.loan}
      emi={engine.figures.emi}
      schemeName={engine.schemes.best?.name ?? null}
      figures={engine.figures}
      onOpenFigure={onOpenFigure}
      onSeePath={onSeePath}
    />
  )
}
