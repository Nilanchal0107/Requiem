import { useT } from "@/i18n"

export default function Hero() {
  const t = useT()
  return (
    <section className="py-4">
      <h2 className="text-h2">{t("home.hero.heading")}</h2>
      <p className="text-sm text-muted-foreground">{t("home.placeholder")}</p>
    </section>
  )
}
