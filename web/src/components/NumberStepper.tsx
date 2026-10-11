import { Minus, Plus } from "lucide-react"
import { Button } from "@/components/ui/button"

export type NumberStepperProps = {
  /** What the buttons change, for screen readers. */
  label: string
  value: number
  min: number
  max: number
  step: number
  unit: string
  /** How the value reads; defaults to the plain number. */
  format?: (value: number) => string
  onChange: (value: number) => void
}

/** − / + buttons around the value; the unit is the word shown after it. */
export function NumberStepper({ label, value, min, max, step, unit, format = String, onChange }: NumberStepperProps) {
  const move = (dir: number) => onChange(Math.min(max, Math.max(min, value + dir * step)))
  return (
    <div className="flex items-center gap-2">
      <Button type="button" variant="outline" className="size-12" aria-label={`− ${label}`} disabled={value <= min} onClick={() => move(-1)}>
        <Minus aria-hidden="true" className="size-5" />
      </Button>
      <span className="min-w-24 text-center font-semibold tabular-nums">
        {format(value)} {unit}
      </span>
      <Button type="button" variant="outline" className="size-12" aria-label={`+ ${label}`} disabled={value >= max} onClick={() => move(1)}>
        <Plus aria-hidden="true" className="size-5" />
      </Button>
    </div>
  )
}
