import { useEffect, useState } from "react"
import { Link } from "react-router"
import { useT } from "@/i18n"
import { ApiError, listReports, type ReportSummary } from "@/api"

export default function MyReports() {
  const t = useT()
  const [reports, setReports] = useState<ReportSummary[] | null>(null)
  const [guest, setGuest] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    listReports()
      .then(setReports)
      .catch((err: unknown) => {
        if (err instanceof ApiError && err.status === 401) setGuest(true)
        else setError(err instanceof Error ? err.message : String(err))
      })
  }, [])

  return (
    <div className="flex flex-col gap-4">
      <h1 className="text-h1">{t("reports.title")}</h1>
      {guest && (
        <div className="flex flex-col items-start gap-2">
          <p>{t("reports.guest")}</p>
          <Link className="text-primary underline" to="/login?next=/reports">
            {t("reports.logIn")}
          </Link>
        </div>
      )}
      {reports && reports.length === 0 && <p>{t("reports.empty")}</p>}
      {reports?.map((r) => (
        <p key={r.id}>
          {r.village_name} · {r.archetype_id} · {r.created_at}
        </p>
      ))}
      {error && <p className="text-sm text-destructive">{error}</p>}
    </div>
  )
}
