import { useEffect, useState } from "react"
import { useT } from "@/i18n"
import { useCompare } from "@/hooks/useCompare"
import type { components } from "@/types/contracts"

// Canned input from fixtures/report.json; V2 takes it from the Entrepreneur's own report.
const cannedInput: components["schemas"]["IntakeInput"] = {
  village_code: "FX1002",
  archetype_id: "dairy",
  unit_scale: 5,
  own_contribution: 100000,
  eligibility: {
    age: 34,
    gender: "female",
    social_category: "obc",
    education: "10th_pass",
    business_status: "new",
    prior_subsidy: false,
    prior_tarun_repaid: false,
    artisan_trade: false,
    farmland: "none",
  },
  language: "en",
  competitor_override: null,
  tenure_months: null,
}

export default function Compare() {
  const t = useT()
  const compare = useCompare()
  const [summary, setSummary] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    compare({ input: cannedInput, archetype_ids: ["dairy", "poultry"] })
      .then((res) => setSummary(res.summary))
      .catch((err: Error) => setError(err.message))
  }, [])

  return (
    <div className="flex flex-col gap-4">
      <h1 className="text-h1">{t("compare.title")}</h1>
      {summary && <p>{summary}</p>}
      {error && <p className="text-sm text-destructive">{error}</p>}
    </div>
  )
}
