import { useEffect, useEffectEvent, useState } from "react"
import { useNavigate } from "react-router"
import { RotateCcw } from "lucide-react"
import { listArchetypes, type ArchetypeSummary, type Report } from "@/api"
import { NumberStepper } from "@/components/NumberStepper"
import { VerdictCard } from "@/components/VerdictCard"
import { Button } from "@/components/ui/button"
import { Sheet, SheetContent, SheetHeader, SheetTitle } from "@/components/ui/sheet"
import { Slider } from "@/components/ui/slider"
import { useReportStream } from "@/hooks/useReportStream"
import { useSimulate } from "@/hooks/useSimulate"
import { useLang, useT } from "@/i18n"
import { formatInr } from "@/lib/format"
import { whatChanged } from "@/lib/verdict"
import type { components } from "@/types/contracts"

type Change = components["schemas"]["Change"]
type EngineResult = components["schemas"]["EngineResult"]
type IntakeInput = components["schemas"]["IntakeInput"]

type Values = { own_contribution: number; unit_scale: number; tenure_months: number }
type Simulated = { key: string; result: EngineResult | null; failed: boolean }

export type WhatIfSheetProps = {
  open: boolean
  onOpenChange: (open: boolean) => void
  report: Report
  /** A Path to Yes change to apply when the sheet opens. */
  change: Change | null
}

const DEBOUNCE_MS = 300
const CONTRIBUTION_STEP = 10000

// Bottom sheet on a phone, side panel from sm up.
const PANEL =
  "max-h-[90dvh] overflow-y-auto sm:inset-x-auto sm:inset-y-0 sm:right-0 sm:h-full sm:max-h-none sm:w-96 sm:max-w-sm sm:border-t-0 sm:border-l"

function Row({ label, value, children }: { label: string; value: string; children: React.ReactNode }) {
  return (
    <div className="flex flex-col gap-2">
      <div className="flex items-baseline justify-between gap-2">
        <span className="text-sm text-text-muted">{label}</span>
        <span className="font-semibold tabular-nums">{value}</span>
      </div>
      {children}
    </div>
  )
}

function WhatIfBody({ report, change, close }: { report: Report; change: Change | null; close: () => void }) {
  const t = useT()
  const lang = useLang()
  const simulate = useSimulate()
  const navigate = useNavigate()
  const { start, reportId, failed: makeFailed, busy } = useReportStream()
  const { input } = report
  const base = report.engine as EngineResult
  const original: Values = {
    own_contribution: input.own_contribution,
    unit_scale: input.unit_scale,
    // no Scheme matched = no tenure figure; 60 is only the slider start, unmoved it still sends null
    tenure_months: input.tenure_months ?? base.figures.tenure_months?.value ?? 60,
  }
  const [values, setValues] = useState<Values>(change ? { ...original, [change.field]: change.to_value } : original)
  const [archetype, setArchetype] = useState<ArchetypeSummary | null>(null)
  const [simulated, setSimulated] = useState<Simulated | null>(null)

  const changed = (Object.keys(original) as (keyof Values)[]).some((k) => values[k] !== original[k])
  // The tenure stays null (the Scheme's own) until the Entrepreneur moves it.
  const intake: IntakeInput = {
    ...input,
    ...values,
    tenure_months: values.tenure_months === original.tenure_months ? input.tenure_months : values.tenure_months,
  }
  const key = JSON.stringify(intake)

  useEffect(() => {
    let live = true
    listArchetypes()
      .then((all) => live && setArchetype(all.find((a) => a.id === input.archetype_id) ?? null))
      .catch(() => {
        // The sliders fall back to a range around the current size.
      })
    return () => {
      live = false
    }
  }, [input.archetype_id])

  // Debounced, so dragging a slider sends one call when it settles. Results are tagged with their intake key,
  // so a late answer for an older value never overwrites a newer one.
  useEffect(() => {
    if (!changed) return
    let live = true
    const timer = setTimeout(() => {
      simulate(JSON.parse(key))
        .then((result) => live && setSimulated({ key, result, failed: false }))
        .catch(() => live && setSimulated((prev) => ({ key, result: prev?.result ?? null, failed: true })))
    }, DEBOUNCE_MS)
    return () => {
      live = false
      clearTimeout(timer)
    }
    // `simulate` is a fresh closure each render; the intake key is what matters.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [key, changed])

  // An effect event, so a new `close` closure on each render doesn't re-run the navigation.
  const leave = useEffectEvent((id: string) => {
    close()
    navigate(`/reports/${id}`)
  })
  useEffect(() => {
    if (reportId) leave(reportId)
  }, [reportId])

  const shown = changed && simulated?.result ? simulated.result : base
  // A failed call leaves the last good result on screen, dimmed, and blocks "Make this a new DPR" on numbers that never arrived.
  const stale = changed && (simulated?.key !== key || simulated.failed)
  const diff = whatChanged(base, shown)
  const set = (field: keyof Values) => (value: number) => setValues((v) => ({ ...v, [field]: value }))

  const controls = [
    {
      field: "own_contribution",
      label: t("report.whatIf.contribution"),
      min: 0,
      max: Math.max(Math.ceil(base.figures.project_cost.value / CONTRIBUTION_STEP) * CONTRIBUTION_STEP, values.own_contribution),
      step: CONTRIBUTION_STEP,
      unit: "",
      format: (n: number) => formatInr(n, lang),
    },
    {
      field: "unit_scale",
      label: t("report.whatIf.size"),
      min: Math.min(archetype?.unit_scale_min ?? 1, values.unit_scale),
      max: Math.max(archetype?.unit_scale_max ?? Math.max(10, original.unit_scale * 2), values.unit_scale),
      step: archetype?.unit_scale_step ?? 1,
      unit: archetype?.unit_label ?? "",
      format: undefined,
    },
    {
      field: "tenure_months",
      label: t("report.whatIf.tenure"),
      min: Math.min(12, values.tenure_months),
      max: Math.max(84, values.tenure_months),
      step: 6,
      unit: t("report.whatIf.months"),
      format: undefined,
    },
  ] as const

  return (
    <div className="flex flex-col gap-5 px-4 pb-4">
      {controls.map(({ field, label, format, ...range }) => (
        <Row key={field} label={label} value={`${(format ?? String)(values[field])} ${range.unit}`.trim()}>
          <Slider
            aria-label={label}
            min={range.min}
            max={range.max}
            step={range.step}
            value={[values[field]]}
            onValueChange={([v]) => set(field)(v)}
            className="h-6"
          />
          <NumberStepper label={label} value={values[field]} format={format} onChange={set(field)} {...range} />
        </Row>
      ))}

      <div aria-live="polite" className={stale ? "opacity-60" : undefined}>
        <VerdictCard
          verdict={shown.verdict}
          loan={shown.finance.loan}
          emi={shown.figures.emi}
          schemeName={shown.schemes.best?.name ?? null}
          figures={shown.figures}
        />
      </div>
      {diff.scheme && (
        <p className="rounded-card border border-warn bg-warn-soft p-3 text-sm font-semibold">
          {t("report.whatIf.schemeChanged").replace("{to}", shown.schemes.best?.name ?? t("verdict.noScheme"))}
        </p>
      )}
      {diff.verdict && (
        <p className="rounded-card border border-warn bg-warn-soft p-3 text-sm font-semibold">
          {t("report.whatIf.verdictChanged").replace("{to}", t(`verdict.${shown.verdict.level}`))}
        </p>
      )}
      {simulated?.failed && simulated.key === key && <p className="text-sm text-bad">{t("report.whatIf.failed")}</p>}

      <div className="flex flex-col gap-2">
        <Button className="h-12" disabled={!changed || busy || stale} onClick={() => start(intake)}>
          {busy ? t("report.whatIf.making") : t("report.whatIf.makeNew")}
        </Button>
        {makeFailed && <p className="text-sm text-bad">{t("report.whatIf.makeFailed")}</p>}
        <Button variant="outline" className="h-12 gap-2" disabled={!changed} onClick={() => setValues(original)}>
          <RotateCcw aria-hidden="true" className="size-5" />
          {t("report.whatIf.reset")}
        </Button>
      </div>
    </div>
  )
}

export function WhatIfSheet({ open, onOpenChange, report, change }: WhatIfSheetProps) {
  const t = useT()
  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent side="bottom" className={PANEL}>
        <SheetHeader>
          <SheetTitle>{t("report.whatIf.title")}</SheetTitle>
        </SheetHeader>
        {/* Mounted only while open, so each opening starts from the original values (or the Path to Yes change). */}
        <WhatIfBody report={report} change={change} close={() => onOpenChange(false)} />
      </SheetContent>
    </Sheet>
  )
}
