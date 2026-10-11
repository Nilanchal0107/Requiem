import { Check, ChevronRight, CircleCheck, FileText, LogOut, TriangleAlert, UserRound } from "lucide-react"
import { Link, Navigate, useNavigate } from "react-router"
import { BottomActionBar } from "@/components/BottomActionBar"
import { Button } from "@/components/ui/button"
import { listReports } from "@/api"
import { useAuth } from "@/hooks/useAuth"
import { useLoad } from "@/hooks/useLoad"
import { setLang, useLang, useT } from "@/i18n"
import type { Lang } from "@/i18n/resolve"
import { formatValue } from "@/lib/format"

// Each language is written in its own script, so it is readable before it is chosen.
const LANGS: { lang: Lang; name: string }[] = [
  { lang: "en", name: "English" },
  { lang: "hi", name: "हिन्दी" },
  { lang: "mr", name: "मराठी" },
]

// The account holds only a username (frozen contract), so the profile shows that plus what we already know: saved reports and language.
export default function Profile() {
  const t = useT()
  const lang = useLang()
  const navigate = useNavigate()
  const { user, ready, logout } = useAuth()
  const { items: reports } = useLoad(user ? listReports : null, String(user?.id ?? ""))

  if (!ready) return null
  if (!user) return <Navigate to="/login?next=/profile" replace />

  const count = (n: number) => formatValue(n, "count", lang)
  const feasible = reports?.filter((r) => r.verdict === "feasible").length ?? 0
  const notYet = reports ? reports.length - feasible : 0

  return (
    <div className="flex flex-col gap-6 pb-24">
      <section className="flex items-center gap-4">
        <span className="flex size-16 items-center justify-center rounded-full bg-primary-soft text-primary">
          <UserRound aria-hidden="true" className="size-8" />
        </span>
        <div className="flex flex-col">
          <h1 className="text-h1">{user.username}</h1>
          <span className="text-sm text-text-muted">{t("profile.subtitle")}</span>
        </div>
      </section>

      <section className="flex flex-col gap-2">
        <h2 className="text-h3">{t("profile.reports")}</h2>
        <dl className="grid grid-cols-3 gap-2">
          {[
            { icon: FileText, label: t("profile.total"), value: reports?.length },
            { icon: CircleCheck, label: t("verdict.feasible"), value: reports ? feasible : undefined },
            { icon: TriangleAlert, label: t("profile.needWork"), value: reports ? notYet : undefined },
          ].map(({ icon: Icon, label, value }) => (
            <div key={label} className="flex flex-col gap-1 rounded-card border border-border bg-surface p-3">
              <dt className="flex items-center gap-1 text-sm text-text-muted">
                <Icon aria-hidden="true" className="size-4 shrink-0" />
                {label}
              </dt>
              <dd className="text-2xl font-bold tabular-nums">{value === undefined ? "–" : count(value)}</dd>
            </div>
          ))}
        </dl>
        <Link to="/reports" className="flex min-h-12 items-center justify-between rounded-card border border-border bg-surface px-4">
          {t("common.myReports")}
          <ChevronRight aria-hidden="true" className="size-5 text-text-muted" />
        </Link>
      </section>

      <section className="flex flex-col gap-2">
        <h2 className="text-h3">{t("profile.language")}</h2>
        <div role="radiogroup" aria-label={t("profile.language")} className="grid grid-cols-3 gap-2">
          {LANGS.map((o) => (
            <Button
              key={o.lang}
              role="radio"
              aria-checked={lang === o.lang}
              variant="outline"
              className={`h-12 gap-1 ${lang === o.lang ? "border-primary bg-primary-soft text-primary" : ""}`}
              onClick={() => setLang(o.lang)}
            >
              {lang === o.lang && <Check aria-hidden="true" className="size-4" />}
              {o.name}
            </Button>
          ))}
        </div>
        <p className="text-sm text-text-muted">{t("profile.languageNote")}</p>
      </section>

      <Button variant="outline" className="h-12 gap-2" onClick={() => logout().then(() => navigate("/"))}>
        <LogOut aria-hidden="true" className="size-5" />
        {t("common.logOut")}
      </Button>

      <BottomActionBar>
        <Button asChild className="h-12 w-full">
          <Link to="/new">{t("common.newDpr")}</Link>
        </Button>
      </BottomActionBar>
    </div>
  )
}
