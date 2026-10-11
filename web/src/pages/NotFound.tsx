import { useT } from "@/i18n"

export default function NotFound() {
  const t = useT()
  return <h1 className="text-h1">{t("common.notFound.title")}</h1>
}
