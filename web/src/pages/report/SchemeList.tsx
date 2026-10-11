import { ExternalLink, Landmark, Lock } from "lucide-react"
import { MetricRows } from "@/components/MetricRows"
import { SourceBadge } from "@/components/SourceBadge"
import { useSchemeDates } from "@/hooks/useSchemeDates"
import { useLang, useT } from "@/i18n"
import type { Lang } from "@/i18n/resolve"
import { formatDate, formatValue } from "@/lib/format"
import type { components } from "@/types/contracts"

type SchemeMatch = components["schemas"]["SchemeMatch"]
type SchemeOption = components["schemas"]["SchemeOption"]

const withNumber = (template: string, n: string) => template.replace("{n}", n)

function SchemeCard({ option, best, lang, verifiedOn }: { option: SchemeOption; best: boolean; lang: Lang; verifiedOn?: string }) {
  const t = useT()
  const { terms } = option
  const cell = (value: string, source: "scheme" | "computed" = "scheme") => (
    <>
      <span className="font-semibold tabular-nums">{value}</span>
      <SourceBadge source={source} />
    </>
  )
  return (
    <article className="flex flex-col gap-2 rounded-card border border-border bg-surface p-4">
      <h3 className="flex items-center gap-2 text-h3">
        <Landmark aria-hidden="true" className="size-5 shrink-0 text-primary" />
        {option.name}
        {option.tier && <span className="text-sm font-normal capitalize text-text-muted">{option.tier}</span>}
      </h3>
      {best && <p className="text-sm font-semibold text-primary">{t("report.schemes.best")}</p>}
      <MetricRows
        rows={[
          { label: t("report.schemes.rate"), values: [cell(withNumber(t("report.schemes.ratePerYear"), formatValue(terms.interest_rate, "count", lang)))] },
          { label: t("report.schemes.tenure"), values: [cell(withNumber(t("report.key.months"), formatValue(terms.tenure_months, "count", lang)))] },
          { label: t("report.schemes.moratorium"), values: [cell(withNumber(t("report.key.months"), formatValue(terms.moratorium_months, "count", lang)))] },
          { label: t("report.schemes.emi"), values: [cell(formatValue(terms.emi, "INR", lang), "computed")] },
        ]}
      />
      {/* Reasons come from the engine, in English. */}
      <ul className="list-disc pl-5 text-sm">
        {option.reasons.map((reason) => (
          <li key={reason}>{reason}</li>
        ))}
      </ul>
      <p className="flex flex-wrap items-center gap-x-4 text-sm">
        <a
          href={option.source_url}
          target="_blank"
          rel="noreferrer noopener"
          className="inline-flex min-h-12 items-center gap-1 text-primary underline underline-offset-4"
        >
          {t("report.schemes.source")}
          <ExternalLink aria-hidden="true" className="size-4" />
        </a>
        {verifiedOn && <span className="text-text-muted">{t("report.schemes.verified").replace("{date}", formatDate(verifiedOn, lang))}</span>}
      </p>
    </article>
  )
}

export function SchemeList({ schemes }: { schemes: SchemeMatch }) {
  const t = useT()
  const lang = useLang()
  const dates = useSchemeDates()
  const options = [...(schemes.best ? [schemes.best] : []), ...schemes.alternatives]
  return (
    <section className="flex flex-col gap-3">
      <h2 className="text-h3">{t("report.schemes.title")}</h2>
      {options.map((option, i) => (
        <SchemeCard key={`${option.scheme_id}-${option.tier}`} option={option} best={i === 0 && !!schemes.best} lang={lang} verifiedOn={dates[option.scheme_id]} />
      ))}
      {schemes.ineligible.length > 0 && (
        <div className="flex flex-col gap-2">
          <h3 className="text-base font-semibold">{t("report.schemes.not")}</h3>
          <ul className="flex flex-col gap-2">
            {schemes.ineligible.map((s) => (
              <li key={s.scheme_id} className="flex gap-2 rounded-card bg-surface-soft p-3 text-sm">
                <Lock aria-hidden="true" className="mt-1 size-4 shrink-0" />
                <span>
                  <span className="font-semibold">{s.name}</span>: {s.failed_rule}
                  {s.unlock_hint && (
                    <>
                      {" "}
                      <span className="text-text-muted">
                        {t("report.schemes.unlock")}: {s.unlock_hint}
                      </span>
                    </>
                  )}
                </span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </section>
  )
}
