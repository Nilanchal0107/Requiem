import { useEffect } from "react"
import { useNavigate } from "react-router"
import { Button } from "@/components/ui/button"
import { Stepper } from "@/components/Stepper"
import { useReportStream } from "@/hooks/useReportStream"
import { useT } from "@/i18n"
import { CANNED_INTAKE } from "@/pages/new/canned-intake"
import DescribeBox from "@/pages/new/DescribeBox"
import StepAboutYou from "@/pages/new/StepAboutYou"
import StepBusiness from "@/pages/new/StepBusiness"
import StepMoney from "@/pages/new/StepMoney"
import StepWhere from "@/pages/new/StepWhere"

// Pause after `done` so the last stage is visible before the report opens.
const NAVIGATE_DELAY_MS = 600

export default function NewReport() {
  const t = useT()
  const navigate = useNavigate()
  const { start, events, reportId, failed } = useReportStream()

  useEffect(() => {
    if (!reportId) return
    const timer = setTimeout(() => navigate(`/reports/${reportId}`), NAVIGATE_DELAY_MS)
    return () => clearTimeout(timer)
  }, [reportId, navigate])

  const running = events.length > 0 && !failed && !reportId

  return (
    <div className="flex flex-col gap-6">
      <h1 className="text-h1">{t("wizard.title")}</h1>
      <DescribeBox />
      <Stepper current={0} total={4} />
      <StepWhere />
      <StepBusiness />
      <StepMoney />
      <StepAboutYou />

      <Button onClick={() => start(CANNED_INTAKE)} disabled={running}>
        {t("wizard.start")}
      </Button>

      <ul className="flex flex-col gap-1 text-sm">
        {events.map((event, i) => (
          <li key={i}>
            {event.stage}: {event.status}
          </li>
        ))}
      </ul>

      {failed && (
        <div className="flex flex-col items-start gap-2">
          <p role="alert" className="text-sm text-destructive">
            {t("wizard.error")}
          </p>
          <Button variant="outline" onClick={() => start(CANNED_INTAKE)}>
            {t("wizard.retry")}
          </Button>
        </div>
      )}
    </div>
  )
}
