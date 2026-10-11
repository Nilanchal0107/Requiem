import { useT } from "@/i18n"

export default function StepBusiness() {
  const t = useT()
  return <p className="text-sm">{t("wizard.step.business")}</p>
}
