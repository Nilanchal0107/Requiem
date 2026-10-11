import { Egg, Milk, Scissors, Sprout, Store, Wheat, type LucideIcon } from "lucide-react"
import type { ArchetypeSummary } from "@/api"
import { ChoiceCard } from "@/components/ChoiceCard"
import { NumberStepper } from "@/components/NumberStepper"
import { useLang, useT } from "@/i18n"
import { formatValue } from "@/lib/format"
import type { StepProps } from "@/pages/new/draft"

const ICONS: Record<string, LucideIcon> = {
  dairy: Milk,
  onion_cultivation: Sprout,
  poultry: Egg,
  tailoring: Scissors,
  kirana: Store,
  flour_mill: Wheat,
}

export default function StepBusiness({ draft, patch, errors, archetypes }: StepProps & { archetypes: ArchetypeSummary[] }) {
  const t = useT()
  const lang = useLang()
  const chosen = archetypes.find((a) => a.id === draft.archetype_id)
  // Stock value is money; the rest are counts or areas.
  const inRupees = chosen?.unit_label.includes("₹")

  return (
    <div className="flex flex-col gap-4">
      <h2 className="text-h2">{t("wizard.business.title")}</h2>
      <div
        role="radiogroup"
        aria-label={t("wizard.business.title")}
        aria-invalid={errors.archetype ? true : undefined}
        tabIndex={errors.archetype ? -1 : undefined}
        className="grid grid-cols-2 gap-3 outline-none"
      >
        {archetypes.map((a) => (
          <ChoiceCard
            key={a.id}
            icon={ICONS[a.id] ?? Store}
            label={t(`wizard.archetype.${a.id}`)}
            selected={a.id === draft.archetype_id}
            onSelect={() => a.id !== draft.archetype_id && patch({ archetype_id: a.id, unit_scale: a.unit_scale_default })}
          />
        ))}
      </div>
      {errors.archetype && (
        <p role="alert" className="text-sm text-destructive">
          {errors.archetype}
        </p>
      )}

      {chosen && draft.unit_scale !== null && (
        <div className="flex flex-col gap-2">
          <p className="font-semibold">{t(`wizard.ask.${chosen.id}`)}</p>
          <NumberStepper
            label={t(`wizard.unit.${chosen.id}`)}
            value={draft.unit_scale}
            min={chosen.unit_scale_min}
            max={chosen.unit_scale_max}
            step={chosen.unit_scale_step}
            unit={inRupees ? "" : t(`wizard.unit.${chosen.id}`)}
            format={(v) => formatValue(v, inRupees ? "INR" : "count", lang)}
            onChange={(unit_scale) => patch({ unit_scale })}
          />
          <p className="text-sm text-text-muted">
            {t("wizard.business.typical").replace("{n}", formatValue(chosen.unit_scale_default, inRupees ? "INR" : "count", lang))}
          </p>
        </div>
      )}
    </div>
  )
}
