import { useT } from "@/i18n"

export default function StepWhere() {
  const t = useT()
  return <p className="text-sm">{t("wizard.step.where")}</p>
}
