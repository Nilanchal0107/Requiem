import { useT } from "@/i18n"

export default function DescribeBox() {
  const t = useT()
  return <p className="text-sm">{t("wizard.describe")}</p>
}
