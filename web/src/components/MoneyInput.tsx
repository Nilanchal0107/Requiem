import { useId } from "react"
import { Input } from "@/components/ui/input"
import { formatCompact, formatMoneyWords } from "@/lib/format"
import type { Lang } from "@/i18n/resolve"
import { cn } from "@/lib/utils"

export type MoneyInputProps = {
  label: string
  value: number | null
  lang: Lang
  onChange: (value: number | null) => void
  error?: string
}

const CHIPS = [25000, 50000, 100000, 200000]
// Keeps the amount inside what the backend and a phone's number type both handle.
const MAX = 1_000_000_000

/** A ₹ field with a numeric keypad, Indian digit grouping while typing, amount chips and the amount in words. */
export function MoneyInput({ label, value, lang, onChange, error }: MoneyInputProps) {
  const id = useId()
  return (
    <div className="flex flex-col gap-2">
      <label htmlFor={id} className="font-semibold">
        {label}
      </label>
      <div className="relative">
        <span aria-hidden="true" className="absolute top-1/2 left-3 -translate-y-1/2 text-lg">
          ₹
        </span>
        <Input
          id={id}
          inputMode="numeric"
          autoComplete="off"
          value={value === null ? "" : value.toLocaleString("en-IN")}
          onChange={(e) => {
            const digits = e.target.value.replace(/\D/g, "")
            onChange(digits ? Math.min(Number(digits), MAX) : null)
          }}
          aria-invalid={error ? true : undefined}
          aria-describedby={error ? `${id}-error` : `${id}-words`}
          className="h-12 pl-8 text-lg tabular-nums"
        />
      </div>
      <p id={`${id}-words`} aria-live="polite" className="min-h-6 text-text-muted">
        {value !== null && value > 0 ? formatMoneyWords(value, lang) : ""}
      </p>
      {error && (
        <p id={`${id}-error`} role="alert" className="text-sm text-destructive">
          {error}
        </p>
      )}
      <div className="flex flex-wrap gap-2">
        {CHIPS.map((amount) => (
          <button
            key={amount}
            type="button"
            aria-pressed={value === amount}
            onClick={() => onChange(amount)}
            className={cn(
              "h-12 rounded-full border px-4 outline-none focus-visible:ring-[3px] focus-visible:ring-ring/50",
              value === amount ? "border-primary bg-primary-soft font-semibold" : "border-border-strong bg-background",
            )}
          >
            {formatCompact(amount, lang)}
          </button>
        ))}
      </div>
    </div>
  )
}
