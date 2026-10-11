import { Download, Share2 } from "lucide-react"
import { useEffect, useState, type ReactNode } from "react"
import { toast } from "sonner"
import { listArchetypes, type Report } from "@/api"
import { fillFigures } from "@/components/FigureText"
import { Button } from "@/components/ui/button"
import { useSchemeDates } from "@/hooks/useSchemeDates"
import { useT } from "@/i18n"
import enSource from "@/i18n/en/source.json"
import { formatDate, formatFigure, formatInr, formatValue } from "@/lib/format"
import { shareLink } from "@/lib/share"
import { DprTable } from "@/pages/report/DprTable"
import type { components } from "@/types/contracts"

type Figure = components["schemas"]["Figure"]

// The Bank DPR is always English, whatever the app language, so its words are written here and not in the i18n files.
const SOURCE = enSource as Record<string, string>
const VERDICT = { feasible: "Feasible", feasible_with_changes: "Feasible with changes", not_feasible: "Not feasible" } as const
const REPAYMENT_PREVIEW = 12
const DOCUMENTS = [
  "Aadhaar card",
  "PAN card",
  "Address proof",
  "Passport-size photographs",
  "Bank statements for the last 6 months",
  "Quotations for the animals, machinery or stock to be bought",
  "Education or training certificates",
  "Caste certificate (if you belong to a reserved category)",
  "Land documents such as the 7/12 extract (if you own or lease farmland)",
  "This Detailed Project Report",
]

const en = (iso: string) => formatDate(iso, "en")
const humanize = (value: string) => value.replace(/_/g, " ").replace(/^./, (c) => c.toUpperCase())
const fig = (label: string, f: Figure) => [label, formatFigure(f, "en"), SOURCE[`source.${f.source}`]]

function Section({ n, title, children, className }: { n: number; title: string; children: ReactNode; className?: string }) {
  return (
    <section className={`flex flex-col gap-2 break-inside-avoid ${className ?? ""}`}>
      <h2 className="border-b border-border-strong pb-1 text-base font-semibold">
        {n}. {title}
      </h2>
      {children}
    </section>
  )
}

export type BankTabProps = {
  report: Report
}

export function BankTab({ report }: BankTabProps) {
  const t = useT()
  const dates = useSchemeDates()
  const [showAll, setShowAll] = useState(false)
  const [business, setBusiness] = useState<string | null>(null)
  const { engine, input, explanation } = report
  useEffect(() => {
    let live = true
    listArchetypes()
      .then((all) => live && setBusiness(all.find((a) => a.id === engine?.archetype_id)?.name ?? null))
      .catch(() => {
        // Falls back to the id below.
      })
    return () => {
      live = false
    }
  }, [engine?.archetype_id])
  if (!engine) return null

  const { market, cost, finance, projections, repayment } = engine
  const best = engine.schemes.best
  const prepared = en(report.created_at)
  const businessName = business ?? humanize(engine.archetype_id)
  const e = input.eligibility
  const working = cost.project_cost.inputs?.working_capital
  const figs = engine.figures
  const swot = explanation?.available ? explanation.swot : null
  const risks = explanation?.available ? explanation.sections.find((s) => s.key === "risks") : undefined
  const fill = (text: string) => fillFigures(text, figs, "en")
  const sourceHead = ["Particular", "Value", "Source"]

  const share = async () => {
    const result = await shareLink(navigator, { title: t("report.bank.shareTitle"), url: window.location.href })
    if (result === "copied") toast.success(t("report.bank.copied"))
  }

  return (
    <div className="flex flex-col gap-4">
      <div className="flex gap-2 print:hidden">
        <Button variant="outline" className="h-12 flex-1 gap-2" onClick={share}>
          <Share2 aria-hidden="true" className="size-5" />
          {t("report.bank.share")}
        </Button>
        <Button variant="outline" className="h-12 flex-1 gap-2" onClick={() => window.print()}>
          <Download aria-hidden="true" className="size-5" />
          {t("report.bank.download")}
        </Button>
      </div>

      <article lang="en" className="flex flex-col gap-6 rounded-card border border-border bg-surface p-4 print:border-0 print:p-0">
        <header className="flex flex-col gap-1 border-b-2 border-text pb-3">
          <h2 className="text-h2 tracking-wide">DETAILED PROJECT REPORT</h2>
          <p className="text-body">
            {businessName} · Village code {engine.village_code}
          </p>
          <p className="text-sm text-text-muted">Prepared {prepared}</p>
        </header>

        <Section n={1} title="Entrepreneur profile">
          <DprTable
            head={["Particular", "Detail"]}
            rows={[
              ["Age", String(e.age)],
              ["Gender", humanize(e.gender)],
              ["Social category", e.social_category.toUpperCase()],
              ["Education", humanize(e.education)],
              ["Business status", humanize(e.business_status)],
              ["Farmland", humanize(e.farmland)],
            ]}
          />
          <p className="text-sm text-text-muted">Source: {SOURCE["source.user"]}</p>
        </Section>

        <Section n={2} title="Project summary">
          <DprTable
            head={sourceHead}
            rows={[
              ["Business", businessName, ""],
              ["Scale", formatValue(input.unit_scale, "count", "en"), SOURCE["source.user"]],
              fig("Project Cost", cost.project_cost),
              fig("Own Contribution", finance.own_contribution),
              fig("Loan", finance.loan),
              ["Scheme", best ? `${best.name}${best.tier ? ` ${humanize(best.tier)}` : ""}` : "No Scheme matched", ""],
              ["Verdict", VERDICT[engine.verdict.level], SOURCE["source.computed"]],
            ]}
          />
        </Section>

        <Section n={3} title="Locality market analysis">
          <DprTable
            head={sourceHead}
            rows={[
              // The engine keeps zero-valued placeholders for figures a Business Archetype doesn't use; they say "Not used ...".
              ...[market.households, market.potential_customers, market.demand, market.competitors, market.competitor_capacity, market.market_gap]
                .filter((f) => !f.note?.startsWith("Not used"))
                .map((f) => fig(f.label, f)),
              ["Sales channels", market.channels.join(", ") || "–", ""],
            ]}
          />
          {market.competitor_coverage === "low" && <p className="text-sm">Few competing shops are mapped for this village, so the competitor count may be low. Please verify locally.</p>}
        </Section>

        <Section n={4} title="Project Cost breakdown">
          <DprTable
            head={sourceHead}
            total
            rows={[
              ...cost.items.map((item) => fig(item.name, item.figure)),
              ...(working ? [["Working capital", formatInr(working, "en"), figs.working_capital ? SOURCE[`source.${figs.working_capital.source}`] : ""]] : []),
              fig("Total Project Cost", cost.project_cost),
            ]}
          />
        </Section>

        <Section n={5} title="Means of finance">
          <DprTable
            head={sourceHead}
            rows={[
              fig("Own Contribution", finance.own_contribution),
              fig("Loan", finance.loan),
              fig(finance.subsidy_backended ? "Subsidy (back-ended)" : "Subsidy", finance.subsidy),
              fig("Funding Gap", finance.funding_gap),
            ]}
          />
          {finance.subsidy_backended && <p className="text-sm">Back-ended subsidy: it is not paid at the start of the loan.</p>}
        </Section>

        <Section n={6} title="Scheme terms">
          {best ? (
            <>
              <DprTable
                head={sourceHead}
                rows={[
                  ["Scheme", `${best.name}${best.tier ? ` ${humanize(best.tier)}` : ""}`, ""],
                  ["Principal", formatInr(best.terms.principal, "en"), SOURCE["source.computed"]],
                  ["Interest rate", `${formatValue(best.terms.interest_rate, "count", "en")}% a year`, SOURCE["source.scheme"]],
                  ["Tenure", `${best.terms.tenure_months} months`, SOURCE["source.scheme"]],
                  ["Moratorium", `${best.terms.moratorium_months} months (${best.terms.moratorium_mode})`, SOURCE["source.scheme"]],
                  ["EMI", formatInr(best.terms.emi, "en"), SOURCE["source.computed"]],
                  ["Total interest", formatInr(best.terms.total_interest, "en"), SOURCE["source.computed"]],
                ]}
              />
              <p className="text-sm text-text-muted">
                Scheme page: {best.source_url}
                {dates[best.scheme_id] && ` (verified ${en(dates[best.scheme_id])})`}. The bank sets the final rate.
              </p>
            </>
          ) : (
            <p className="text-sm">No Scheme matched this profile.</p>
          )}
        </Section>

        <Section n={7} title="Repayment schedule" className="print:break-before-page">
          <DprTable
            head={["Month", "Opening", "Interest", "Principal", "Payment", "Closing"]}
            rows={repayment.map((r) => [String(r.month), ...[r.opening, r.interest, r.principal, r.payment, r.closing].map((v) => formatInr(v, "en"))])}
            collapseFrom={showAll ? Infinity : REPAYMENT_PREVIEW}
          />
          {!showAll && repayment.length > REPAYMENT_PREVIEW && (
            <Button variant="ghost" className="h-12 self-start px-0 text-primary print:hidden" onClick={() => setShowAll(true)}>
              Show all {repayment.length}
            </Button>
          )}
          <p className="text-sm text-text-muted">Source: {SOURCE["source.computed"]}</p>
        </Section>

        <Section n={8} title="5-year projected P&L and cash flow" className="print:break-before-page">
          <DprTable
            head={["Year", "Revenue", "Operating cost", "Depreciation", "Interest", "Net profit", "Cash flow"]}
            rows={projections.map((p) => [String(p.year), ...[p.revenue, p.operating_cost, p.depreciation, p.interest, p.net_profit, p.cash_flow].map((v) => formatInr(v, "en"))])}
          />
          <p className="text-sm text-text-muted">Source: {SOURCE["source.computed"]}</p>
        </Section>

        <Section n={9} title="Break-even month">
          <DprTable
            head={sourceHead}
            rows={[
              ["Break-even month", formatFigure(engine.break_even_month, "en"), SOURCE[`source.${engine.break_even_month.source}`]],
              ["Payback period (months)", formatFigure(engine.payback_months, "en"), SOURCE[`source.${engine.payback_months.source}`]],
            ]}
          />
        </Section>

        <Section n={10} title="DSCR per year">
          <DprTable
            head={["Year", "DSCR", "Debt service"]}
            rows={[
              ...projections.map((p) => [String(p.year), p.dscr === null ? "–" : formatValue(p.dscr, "ratio", "en"), formatInr(p.debt_service, "en")]),
              ["Minimum", formatFigure(engine.min_dscr, "en"), ""],
            ]}
            total
          />
          <p className="text-sm text-text-muted">Source: {SOURCE["source.computed"]}</p>
        </Section>

        <Section n={11} title="SWOT and risks">
          {swot ? (
            <>
              {risks && <p className="text-sm">{fill(risks.text)}</p>}
              <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
                {(
                  [
                    ["Strengths", swot.strengths],
                    ["Weaknesses", swot.weaknesses],
                    ["Opportunities", swot.opportunities],
                    ["Threats", swot.threats],
                  ] as const
                ).map(([title, items]) => (
                  <div key={title}>
                    <h3 className="text-sm font-semibold">{title}</h3>
                    <ul className="list-disc pl-5 text-sm">
                      {items.map((item, i) => (
                        <li key={i}>{fill(item)}</li>
                      ))}
                    </ul>
                  </div>
                ))}
              </div>
            </>
          ) : (
            <p className="text-sm">The written analysis is not available for this report.</p>
          )}
        </Section>

        <Section n={12} title="Application document checklist">
          <ul className="flex flex-col gap-1 text-sm">
            {DOCUMENTS.map((doc) => (
              <li key={doc} className="flex items-start gap-2">
                <span aria-hidden="true" className="mt-1 size-4 shrink-0 border border-text" />
                {doc}
              </li>
            ))}
          </ul>
          <p className="text-sm text-text-muted">Typical documents. Your bank may ask for more.</p>
        </Section>

        <footer className="text-sm text-text-muted">
          <p>Sources: {[...new Set(Object.values(figs).map((f) => SOURCE[`source.${f.source}`]))].join("; ")}.</p>
          <p>Indicative only. Verify with your bank.</p>
        </footer>
      </article>

      {/* Repeats on every printed page. */}
      <p className="fixed inset-x-0 bottom-[-12mm] hidden justify-between border-t border-border text-xs text-text-muted print:flex">
        <span>Report {report.id}</span>
        <span>Prepared {prepared}</span>
      </p>
    </div>
  )
}
