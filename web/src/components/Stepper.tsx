import { useT } from "@/i18n"
import { cn } from "@/lib/utils"

export type StepperProps = {
  /** Zero-based index of the step being shown. */
  current: number
  total: number
  /** Called with an earlier step's index; later steps cannot be jumped to. */
  onSelect?: (step: number) => void
}

const STEP_KEYS = ["where", "business", "money", "aboutYou"]

export function Stepper({ current, total, onSelect }: StepperProps) {
  const t = useT()
  return (
    <div className="flex flex-col gap-2">
      <p className="text-sm text-text-muted">{t("wizard.stepOf").replace("{n}", String(current + 1)).replace("{total}", String(total))}</p>
      <ol className="flex gap-1">
        {Array.from({ length: total }, (_, i) => (
          <li key={i} className="flex-1">
            <button
              type="button"
              disabled={i >= current || !onSelect}
              aria-current={i === current ? "step" : undefined}
              aria-label={t(`wizard.step.${STEP_KEYS[i]}`)}
              onClick={() => onSelect?.(i)}
              // The bar is 8 px; the button is taller so a thumb can hit it.
              className="flex h-6 w-full items-center disabled:cursor-default"
            >
              <span className={cn("h-2 w-full rounded-full border border-primary", i < current ? "bg-primary" : "bg-transparent", i > current && "border-border")} />
            </button>
          </li>
        ))}
      </ol>
    </div>
  )
}
