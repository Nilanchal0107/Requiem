import { useT } from "@/i18n"

export default function Home() {
  const t = useT()
  return <h1 className="text-h1">{t("home.title")}</h1>
}
