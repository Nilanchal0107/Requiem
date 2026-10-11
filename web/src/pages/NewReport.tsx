import { useEffect, useState } from "react"
import { useNavigate } from "react-router"
import { listArchetypes } from "@/api"
import { BottomActionBar } from "@/components/BottomActionBar"
import { ErrorState } from "@/components/ErrorState"
import { Stepper } from "@/components/Stepper"
import { Button } from "@/components/ui/button"
import { useLoad } from "@/hooks/useLoad"
import { useReportStream } from "@/hooks/useReportStream"
import { useLang, useT } from "@/i18n"
import DescribeBox from "@/pages/new/DescribeBox"
import { applyParsed, clearDraft, firstBadStep, loadDraft, saveDraft, stillMissing, toIntake, validate, type Draft } from "@/pages/new/draft"
import StepAboutYou from "@/pages/new/StepAboutYou"
import StepBusiness from "@/pages/new/StepBusiness"
import StepMoney from "@/pages/new/StepMoney"
import StepWhere from "@/pages/new/StepWhere"

// Pause after `done` so the last stage is visible before the report opens.
const NAVIGATE_DELAY_MS = 600
const STEPS = 4

export default function NewReport() {
  const t = useT()
  const lang = useLang()
  const navigate = useNavigate()
  const { start, events, reportId, failed, busy } = useReportStream()
  const archetypes = useLoad(listArchetypes, "archetypes")
  const [draft, setDraft] = useState<Draft>(loadDraft)
  // Errors show only after a failed Next; `attempt` re-runs the focus effect on every failed try.
  const [attempt, setAttempt] = useState(0)
  const [showErrors, setShowErrors] = useState(false)
  // Dot paths the describe box could not fill; shown on every step until answered.
  const [parsedMissing, setParsedMissing] = useState<string[]>([])

  const building = busy || events.length > 0 || failed
  const chosen = archetypes.items?.find((a) => a.id === draft.archetype_id)
  const required = chosen?.eligibility_fields ?? []
  const step = draft.step

  const patch = (changes: Partial<Draft>) => setDraft((d) => ({ ...d, ...changes }))
  const goTo = (to: number) => {
    patch({ step: to })
    setShowErrors(false)
    window.scrollTo(0, 0)
  }
  const fail = () => {
    setShowErrors(true)
    setAttempt((n) => n + 1)
  }

  const describedMissing = stillMissing(draft, parsedMissing)
    .map((path) => t(path === "village_code" ? "wizard.where.village" : path === "own_contribution" ? "wizard.money.label" : `wizard.field.${path.replace("eligibility.", "")}`))
    .join(", ")

  const errors = Object.fromEntries(Object.entries(showErrors ? validate(step, draft, required) : {}).map(([f, key]) => [f, t(key)]))

  // Focus moves to the first problem (ui-ux 5.1).
  useEffect(() => {
    if (attempt) document.querySelector<HTMLElement>('[aria-invalid="true"]')?.focus()
  }, [attempt])

  // The draft is kept until the server has accepted it: the first stage event proves the report exists.
  useEffect(() => {
    if (events.length > 0) clearDraft()
    else if (!building) saveDraft(draft)
  }, [draft, events.length, building])

  useEffect(() => {
    if (!reportId) return
    const timer = setTimeout(() => navigate(`/reports/${reportId}`), NAVIGATE_DELAY_MS)
    return () => clearTimeout(timer)
  }, [reportId, navigate])

  function next() {
    if (Object.keys(validate(step, draft, required)).length) return fail()
    if (step < STEPS - 1) return goTo(step + 1)
    const bad = firstBadStep(draft, required)
    if (bad !== null) {
      goTo(bad)
      return fail()
    }
    start(toIntake(draft, lang))
  }

  if (building) {
    return (
      <div className="flex flex-col gap-4">
        <h1 className="text-h1">{t("wizard.building")}</h1>
        <ul className="flex flex-col gap-1 text-sm">
          {events.map((event, i) => (
            <li key={i}>
              {event.stage}: {event.status}
            </li>
          ))}
        </ul>
        {failed && (
          <ErrorState message={t("wizard.error")} retryLabel={t("wizard.retry")} onRetry={() => start(toIntake(draft, lang))} />
        )}
      </div>
    )
  }

  const stepProps = { draft, patch, errors }
  return (
    <div className="flex flex-col gap-6 pb-28">
      <h1 className="text-h1">{t("wizard.title")}</h1>
      {step === 0 && (
        <DescribeBox
          onParsed={({ fields, missing }) => {
            setDraft((d) => applyParsed(d, fields))
            setParsedMissing(missing)
          }}
        />
      )}
      {describedMissing && <p className="rounded-xl bg-primary-soft p-3 text-sm">{t("wizard.describe.missing").replace("{fields}", describedMissing)}</p>}
      <Stepper current={step} total={STEPS} onSelect={goTo} />

      {archetypes.error ? (
        <ErrorState message={t("wizard.loadError")} retryLabel={t("wizard.retry")} onRetry={archetypes.retry} />
      ) : (
        <>
          {step === 0 && <StepWhere {...stepProps} />}
          {step === 1 && archetypes.items && <StepBusiness {...stepProps} archetypes={archetypes.items} />}
          {step === 2 && <StepMoney {...stepProps} />}
          {step === 3 && <StepAboutYou {...stepProps} archetype={chosen} />}
        </>
      )}

      <BottomActionBar>
        {step > 0 && (
          <Button variant="outline" className="h-12 flex-1" onClick={() => goTo(step - 1)}>
            {t("wizard.back")}
          </Button>
        )}
        <Button className="h-12 flex-[2]" onClick={next}>
          {step === STEPS - 1 ? t("wizard.start") : t("wizard.next")}
        </Button>
      </BottomActionBar>
    </div>
  )
}
