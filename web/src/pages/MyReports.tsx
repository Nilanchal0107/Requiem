import { ChevronRight } from "lucide-react"
import { Link, Navigate } from "react-router"
import { BottomActionBar } from "@/components/BottomActionBar"
import { EmptyState } from "@/components/EmptyState"
import { ErrorState } from "@/components/ErrorState"
import { TONE } from "@/components/VerdictCard"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import { listReports } from "@/api"
import { useAuth } from "@/hooks/useAuth"
import { useLoad } from "@/hooks/useLoad"
import { useLang, useT } from "@/i18n"
import { formatDate } from "@/lib/format"

export default function MyReports() {
  const t = useT()
  const lang = useLang()
  const { user, ready } = useAuth()
  const { items: reports, error, retry } = useLoad(user ? listReports : null, String(user?.id ?? ""))

  if (!ready) return null
  if (!user) return <Navigate to="/login?next=/reports" replace />

  const build = (
    <Button asChild className="h-12 w-full">
      <Link to="/new">{reports?.length ? t("reports.buildNew") : t("reports.buildFirst")}</Link>
    </Button>
  )

  return (
    <div className="flex flex-col gap-4 pb-24">
      <h1 className="text-h1">{t("reports.title")}</h1>
      {error && <ErrorState message={t("reports.error")} retryLabel={t("reports.retry")} onRetry={retry} />}
      {!error && !reports && <Skeleton className="h-20 w-full" />}
      {reports?.length === 0 && <EmptyState title={t("reports.empty")} body={t("reports.emptyBody")} action={build} />}
      {reports?.map((r) => {
        const tone = r.verdict && TONE[r.verdict]
        return (
          <Link
            key={r.id}
            to={`/reports/${r.id}`}
            className="flex min-h-[72px] items-center gap-2 rounded-card border p-4"
          >
            <div className="flex flex-1 flex-col gap-1">
              <span className="font-bold">
                {t(`wizard.archetype.${r.archetype_id}`)} · {r.village_name}
              </span>
              <span className="flex flex-wrap items-center gap-x-2 text-sm text-text-muted">
                {tone && r.verdict && (
                  <span className={`flex items-center gap-1 rounded px-1 ${tone.card}`}>
                    <tone.icon aria-hidden="true" className="size-4" />
                    {t(`verdict.${r.verdict}`)}
                  </span>
                )}
                {formatDate(r.created_at, lang)}
              </span>
            </div>
            <ChevronRight aria-hidden="true" className="size-5 shrink-0 text-text-muted" />
          </Link>
        )
      })}
      {reports && reports.length > 0 && (
        <BottomActionBar>{build}</BottomActionBar>
      )}
    </div>
  )
}
