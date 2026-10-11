import { useT } from "@/i18n"

export default function StepMoney() {
  const t = useT()
  return <p className="text-sm">{t("wizard.step.money")}</p>
}
