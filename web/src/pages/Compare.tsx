import { useEffect, useState } from "react"
import { Link, useNavigate, useSearchParams } from "react-router"
import { Egg, Milk, Scissors, Sprout, Store, Wheat, type LucideIcon } from "lucide-react"
import { getReport, listArchetypes } from "@/api"
import { BottomActionBar } from "@/components/BottomActionBar"
import { ChoiceCard } from "@/components/ChoiceCard"
import { EmptyState } from "@/components/EmptyState"
import { ErrorState } from "@/components/ErrorState"
import { FigureText } from "@/components/FigureText"
import { MetricRows } from "@/components/MetricRows"
import { TONE } from "@/components/VerdictCard"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import { useCompare } from "@/hooks/useCompare"
import { useLoad } from "@/hooks/useLoad"
import { useReportStream } from "@/hooks/useReportStream"
import { useLang, useT } from "@/i18n"
import { betterIndex, compareFigures } from "@/lib/compare"
import { formatHeadline, formatValue } from "@/lib/format"
import { firstBadStep, loadDraft, toIntake } from "@/pages/new/draft"
import type { components } from "@/types/contracts"

type IntakeInput = components["schemas"]["IntakeInput"]

const ICONS: Record<string, LucideIcon> = {
  dairy: Milk,
  onion_cultivation: Sprout,
  poultry: Egg,
  tailoring: Scissors,
  kirana: Store,
  flour_mill: Wheat,
}
const MAX_OTHERS = 2

// The village and Own Contribution come from the report named in ?report=, else from the wizard draft.
export default function Compare() {
  const t = useT()
  const lang = useLang()
  const navigate = useNavigate()
  const compare = useCompare()
  const [params] = useSearchParams()
  const reportId = params.get("report")
  const { start, reportId: newId, failed: openFailed, busy } = useReportStream()

  const fromReport = useLoad(reportId ? () => getReport(reportId).then((r) => r.input) : null, reportId ?? "")
  const archetypes = useLoad(listArchetypes, "archetypes")
  const [others, setOthers] = useState<string[]>([])
  const [asked, setAsked] = useState<string[] | null>(null)

  let base: IntakeInput | null = fromReport.items
  if (!reportId) {
    const draft = loadDraft()
    if (firstBadStep(draft, []) === null) base = toIntake(draft, lang)
  }
  const input = base && { ...base, language: lang }

  const result = useLoad(input && asked ? () => compare({ input, archetype_ids: [input.archetype_id, ...asked] }) : null, `${asked}|${lang}`)

  useEffect(() => {
    if (newId) navigate(`/reports/${newId}`)
  }, [newId, navigate])

  if (reportId && fromReport.error) return <ErrorState message={t("compare.error")} retryLabel={t("reports.retry")} onRetry={fromReport.retry} />
  if (reportId && !input) return <Skeleton className="h-24 w-full" />
  if (!input) {
    return (
      <EmptyState
        title={t("compare.empty")}
        body={t("compare.emptyBody")}
        action={
          <Button asChild className="h-12">
            <Link to="/new">{t("reports.buildFirst")}</Link>
          </Button>
        }
      />
    )
  }

  const name = (id: string) => t(`wizard.archetype.${id}`)
  const toggle = (id: string) => setOthers((o) => (o.includes(id) ? o.filter((x) => x !== id) : o.length < MAX_OTHERS ? [...o, id] : o))

  if (!asked || result.error) {
    return (
      <div className="flex flex-col gap-4 pb-24">
        <h1 className="text-h1">{t("compare.with").replace("{name}", name(input.archetype_id))}</h1>
        <p className="text-text-muted">{t("compare.pick")}</p>
        {result.error && <ErrorState message={t("compare.error")} retryLabel={t("reports.retry")} onRetry={result.retry} />}
        {archetypes.error && <ErrorState message={t("compare.error")} retryLabel={t("reports.retry")} onRetry={archetypes.retry} />}
        <div role="group" aria-label={t("compare.pick")} className="grid grid-cols-2 gap-3">
          {archetypes.items?.map((a) => {
            const current = a.id === input.archetype_id
            return (
              <ChoiceCard
                key={a.id}
                icon={ICONS[a.id] ?? Store}
                label={current ? `${name(a.id)} (${t("compare.current")})` : name(a.id)}
                selected={current || others.includes(a.id)}
                onSelect={() => !current && toggle(a.id)}
              />
            )
          })}
        </div>
        <BottomActionBar>
          <Button className="h-12 flex-1" disabled={!others.length} onClick={() => {
              setAsked(others)
              result.retry() // same picks after an error keep the same key, so force a refetch
            }}>
            {t("compare.go")}
          </Button>
        </BottomActionBar>
      </div>
    )
  }

  const res = result.items
  if (!res) return <Skeleton className="h-40 w-full" />
  const rs = res.results
  const rows = [
    {
      label: t("compare.verdict"),
      values: rs.map((r) => {
        const { icon: Icon, card } = TONE[r.verdict.level]
        return (
          <span key={r.archetype_id} className={`flex items-center gap-1 ${card.split(" ").at(-1)}`}>
            <Icon aria-hidden="true" className="size-4 shrink-0" />
            {t(`verdict.${r.verdict.level}`)}
          </span>
        )
      }),
    },
    {
      label: t("verdict.loan"),
      values: rs.map((r) => formatHeadline(r.finance.loan, lang)),
      betterIndex: betterIndex(rs.map((r) => r.finance.loan.value), "max"),
    },
    {
      label: t("verdict.emi"),
      values: rs.map((r) => (r.figures.emi ? formatHeadline(r.figures.emi, lang) : "—")),
      betterIndex: betterIndex(rs.map((r) => r.figures.emi?.value ?? Infinity), "min"),
    },
    {
      label: t("report.key.dscr"),
      values: rs.map((r) => t("report.key.dscrValue").replace("{n}", formatValue(r.min_dscr.value, "ratio", lang))),
      betterIndex: betterIndex(rs.map((r) => r.min_dscr.value), "max"),
    },
    {
      label: t("report.key.payback"),
      values: rs.map((r) => t("report.key.months").replace("{n}", formatValue(r.payback_months.value, "ratio", lang))),
      betterIndex: betterIndex(rs.map((r) => r.payback_months.value), "min"),
    },
    { label: t("verdict.scheme"), values: rs.map((r) => r.schemes.best?.name ?? t("verdict.noScheme")) },
  ]

  return (
    <div className="flex flex-col gap-4 pb-24">
      <h1 className="text-h1">{t("compare.title")}</h1>
      <div>
        <div className="flex justify-end gap-2 border-b border-border pb-1 text-sm font-semibold">
          {rs.map((r) => (
            <span key={r.archetype_id} className="min-w-16 text-right">
              {name(r.archetype_id)}
            </span>
          ))}
        </div>
        <MetricRows rows={rows} />
      </div>
      <section className="flex flex-col gap-1">
        <h2 className="text-base font-semibold">{t("compare.which")}</h2>
        <p className="text-sm leading-relaxed">
          <FigureText text={res.summary} figures={compareFigures(rs)} lang={res.language} />
        </p>
      </section>
      <div className="flex flex-col gap-2">
        {rs.map((r) => {
          const a = archetypes.items?.find((x) => x.id === r.archetype_id)
          return (
            <Button
              key={r.archetype_id}
              variant="outline"
              className="h-12"
              disabled={busy || !a}
              onClick={() => a && start({ ...input, archetype_id: a.id, unit_scale: a.unit_scale_default, tenure_months: null })}
            >
              {t("compare.open").replace("{name}", name(r.archetype_id))}
            </Button>
          )
        })}
        {openFailed && <p className="text-sm text-bad">{t("report.whatIf.makeFailed")}</p>}
      </div>
    </div>
  )
}
