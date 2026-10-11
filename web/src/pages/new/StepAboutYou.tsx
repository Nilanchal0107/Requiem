import type { ArchetypeSummary } from "@/api"
import { ChipGroup } from "@/components/ChipGroup"
import { NumberStepper } from "@/components/NumberStepper"
import { useT } from "@/i18n"
import type { StepProps } from "@/pages/new/draft"

// Every eligibility field an Archetype can ask for; the Archetype's own list decides which show.
const CHOICES: Record<string, string[]> = {
  gender: ["female", "male", "other"],
  social_category: ["general", "obc", "sc", "st"],
  education: ["none", "below_8th", "8th_pass", "10th_pass", "12th_pass", "graduate"],
  business_status: ["new", "existing"],
  farmland: ["none", "owned", "leased"],
}
const YES_NO = ["prior_subsidy", "prior_tarun_repaid", "artisan_trade"]

export default function StepAboutYou({ draft, patch, errors, archetype }: StepProps & { archetype: ArchetypeSummary | undefined }) {
  const t = useT()
  const asked = archetype?.eligibility_fields ?? []
  const set = (field: string, value: unknown) => patch({ eligibility: { ...draft.eligibility, [field]: value } })
  const e = draft.eligibility as Record<string, string | number | boolean | undefined>

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h2 className="text-h2">{t("wizard.about.title")}</h2>
        <p className="text-text-muted">{t("wizard.about.helper")}</p>
      </div>

      {asked.includes("age") && (
        <div className="flex flex-col gap-2">
          <p className="font-semibold">{t("wizard.field.age")}</p>
          <NumberStepper label={t("wizard.field.age")} value={draft.eligibility.age ?? 30} min={18} max={80} step={1} unit={t("wizard.years")} onChange={(v) => set("age", v)} />
          <p className="text-sm text-text-muted">{t("wizard.reason.age")}</p>
        </div>
      )}

      {Object.entries(CHOICES)
        .filter(([field]) => asked.includes(field))
        .map(([field, values]) => (
          <ChipGroup
            key={field}
            label={t(`wizard.field.${field}`)}
            hint={t(`wizard.reason.${field}`)}
            options={values.map((v) => ({ value: v, label: t(`wizard.opt.${field}.${v}`) }))}
            value={(e[field] as string | undefined) ?? null}
            onChange={(v) => set(field, v)}
            error={errors[field]}
          />
        ))}

      {YES_NO.filter((field) => asked.includes(field)).map((field) => (
        <ChipGroup
          key={field}
          label={t(`wizard.field.${field}`)}
          hint={t(`wizard.reason.${field}`)}
          options={[
            { value: "yes", label: t("wizard.yes") },
            { value: "no", label: t("wizard.no") },
          ]}
          value={e[field] ? "yes" : "no"}
          onChange={(v) => set(field, v === "yes")}
        />
      ))}
    </div>
  )
}
