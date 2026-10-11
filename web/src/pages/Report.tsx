import { useT } from "@/i18n"

export default function Report() {
  const t = useT()
  return <h1 className="text-h1">{t("report.title")}</h1>
}
