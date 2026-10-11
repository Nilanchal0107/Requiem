import { MoneyInput } from "@/components/MoneyInput"
import { useLang, useT } from "@/i18n"
import type { StepProps } from "@/pages/new/draft"

export default function StepMoney({ draft, patch, errors }: StepProps) {
  const t = useT()
  const lang = useLang()
  return (
    <div className="flex flex-col gap-4">
      <h2 className="text-h2">{t("wizard.money.title")}</h2>
      <MoneyInput
        label={t("wizard.money.label")}
        value={draft.own_contribution}
        lang={lang}
        onChange={(own_contribution) => patch({ own_contribution })}
        error={errors.own_contribution}
      />
      <p className="rounded-xl bg-primary-soft p-3 text-sm">{t("wizard.money.helper")}</p>
    </div>
  )
}
