import { useT } from "@/i18n"

export default function NewReport() {
  const t = useT()
  return <h1 className="text-h1">{t("wizard.title")}</h1>
}
