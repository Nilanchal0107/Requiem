import { useId } from "react"
import { cn } from "@/lib/utils"

export type ChipGroupProps = {
  label: string
  options: { value: string; label: string }[]
  value: string | null
  onChange: (value: string) => void
  /** One line saying why we ask. */
  hint?: string
  error?: string
}

/** Single-choice chips that wrap onto new lines; never scrolls sideways. */
export function ChipGroup({ label, options, value, onChange, hint, error }: ChipGroupProps) {
  const id = useId()
  return (
    <div className="flex flex-col gap-2">
      <span id={id} className="font-semibold">
        {label}
      </span>
      {hint && <span id={`${id}-hint`} className="text-sm text-text-muted">{hint}</span>}
      <div
        role="radiogroup"
        aria-labelledby={id}
        aria-describedby={error ? `${id}-error` : hint ? `${id}-hint` : undefined}
        aria-invalid={error ? true : undefined}
        tabIndex={error ? -1 : undefined}
        className="flex flex-wrap gap-2 rounded-lg outline-none"
      >
        {options.map((o) => (
          <button
            key={o.value}
            type="button"
            role="radio"
            aria-checked={o.value === value}
            onClick={() => onChange(o.value)}
            className={cn(
              "h-12 rounded-full border px-4 text-base outline-none focus-visible:ring-[3px] focus-visible:ring-ring/50",
              o.value === value ? "border-primary bg-primary-soft font-semibold" : "border-border-strong bg-background",
            )}
          >
            {o.label}
          </button>
        ))}
      </div>
      {error && (
        <p id={`${id}-error`} role="alert" className="text-sm text-destructive">
          {error}
        </p>
      )}
    </div>
  )
}
