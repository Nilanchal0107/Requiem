import { useT } from "@/i18n"

export default function StepAboutYou() {
  const t = useT()
  return <p className="text-sm">{t("wizard.step.aboutYou")}</p>
}
