import { useT } from "@/i18n"

export default function Compare() {
  const t = useT()
  return <h1 className="text-h1">{t("compare.title")}</h1>
}
