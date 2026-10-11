import { VerdictCard } from "@/components/VerdictCard"
import { useT } from "@/i18n"
import type { components } from "@/types/contracts"

type EngineResult = components["schemas"]["EngineResult"]

export type ReportHeaderProps = {
  engine: EngineResult
}

export function ReportHeader({ engine }: ReportHeaderProps) {
  const t = useT()
  const schemeName = engine.schemes.best?.name ?? null
  return (
    <header className="flex flex-col gap-2">
      <p className="text-base font-semibold">{t(`verdict.${engine.verdict.level}`)}</p>
      <p className="text-sm">
        {t("verdict.scheme")}: {schemeName ?? t("verdict.noScheme")}
      </p>
      <VerdictCard
        verdict={engine.verdict}
        loan={engine.finance.loan}
        emi={engine.figures.emi}
        schemeName={schemeName}
      />
    </header>
  )
}
