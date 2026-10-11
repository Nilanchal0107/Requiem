import { Link } from "react-router"
import {
  ArrowRight, BadgeCheck, BarChart3, CalendarCheck, FileText, Landmark, Languages, MapPin,
  Scale, Search, SlidersHorizontal, Store, Users, Wallet,
} from "lucide-react"
import type { LucideIcon } from "lucide-react"
import { useT } from "@/i18n"
import { BottomActionBar } from "@/components/BottomActionBar"

const SCHEMES = ["MUDRA", "PMEGP", "Stand-Up India", "PM Vishwakarma", "CMEGP", "KCC"]

const CTA = "inline-flex h-12 items-center justify-center gap-2 rounded-lg bg-cta px-6 font-semibold text-text hover:bg-cta-pressed"

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className="py-6">
      <h2 className="text-h2 mb-3">{title}</h2>
      {children}
    </section>
  )
}

function IconList({ items }: { items: [LucideIcon, string][] }) {
  return (
    <ul className="space-y-3 rounded-xl border bg-surface p-4">
      {items.map(([Icon, text]) => (
        <li key={text} className="flex items-center gap-3">
          <Icon className="size-6 shrink-0 text-primary" aria-hidden />
          <span>{text}</span>
        </li>
      ))}
    </ul>
  )
}

export default function Home() {
  const t = useT()
  return (
    <div className="pb-28 lg:pb-8">
      <section className="grid items-center gap-6 py-6 lg:grid-cols-2">
        <div>
          <h1 className="text-h1">{t("home.hero.title")}</h1>
          <p className="mt-3 text-text-muted">{t("home.hero.body")}</p>
          <Link to="/new" className={`${CTA} mt-6 hidden lg:inline-flex`}>
            {t("home.cta")} <ArrowRight className="size-5" aria-hidden />
          </Link>
        </div>
        <div className="flex items-center justify-center gap-6 rounded-2xl bg-primary-soft p-8 text-primary" aria-hidden>
          <Store className="size-16" />
          <Wallet className="size-16" />
          <FileText className="size-16" />
        </div>
      </section>

      <Section title={t("home.problem.heading")}>
        <IconList items={[[MapPin, t("home.problem.q1")], [Wallet, t("home.problem.q2")], [Landmark, t("home.problem.q3")]]} />
      </Section>

      <Section title={t("home.howItWorks.heading")}>
        <ol className="space-y-3">
          {[t("home.howItWorks.s1"), t("home.howItWorks.s2"), t("home.howItWorks.s3")].map((s, i) => (
            <li key={s} className="flex items-center gap-3">
              <span className="flex size-8 shrink-0 items-center justify-center rounded-full bg-primary font-semibold text-on-primary">
                {i + 1}
              </span>
              <span>{s}</span>
            </li>
          ))}
        </ol>
      </Section>

      <Section title={t("home.different.heading")}>
        <IconList items={[[Search, t("home.different.d1")], [CalendarCheck, t("home.different.d2")], [BadgeCheck, t("home.different.d3")]]} />
      </Section>

      <Section title={t("home.features.heading")}>
        <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
          {([[BarChart3, t("home.features.f1")], [SlidersHorizontal, t("home.features.f2")], [Scale, t("home.features.f3")], [Languages, t("home.features.f4")]] as [LucideIcon, string][]).map(
            ([Icon, text]) => (
              <div key={text} className="flex min-h-24 flex-col gap-2 rounded-xl border bg-surface p-4">
                <Icon className="size-6 text-primary" aria-hidden />
                <span className="font-medium">{text}</span>
              </div>
            ),
          )}
        </div>
      </Section>

      <Section title={t("home.schemes.heading")}>
        <div className="flex flex-wrap gap-2">
          {SCHEMES.map((s) => (
            <span key={s} className="rounded-full border bg-primary-soft px-3 py-1.5 text-sm font-medium text-primary">{s}</span>
          ))}
        </div>
      </Section>

      <Section title={t("home.team.heading")}>
        <p className="flex items-center gap-3">
          <Users className="size-6 text-primary" aria-hidden />
          {t("home.team.body")}
        </p>
      </Section>

      <p className="py-4 text-sm text-text-muted">{t("home.disclaimer")}</p>

      <div className="lg:hidden">
        <BottomActionBar>
          <Link to="/new" className={`${CTA} flex-1`}>{t("home.cta")}</Link>
        </BottomActionBar>
      </div>
    </div>
  )
}
