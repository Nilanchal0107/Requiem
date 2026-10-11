import { useT } from "@/i18n"

export default function MyReports() {
  const t = useT()
  return <h1 className="text-h1">{t("reports.title")}</h1>
}
