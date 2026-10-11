import { Check, type LucideIcon } from "lucide-react"
import { cn } from "@/lib/utils"

export type ChoiceCardProps = {
  icon: LucideIcon
  label: string
  selected: boolean
  onSelect: () => void
}

/** A large tappable card with an icon and a word; put several in a `role="radiogroup"`. */
export function ChoiceCard({ icon: Icon, label, selected, onSelect }: ChoiceCardProps) {
  return (
    <button
      type="button"
      role="radio"
      aria-checked={selected}
      onClick={onSelect}
      className={cn(
        "relative flex min-h-24 flex-col items-center justify-center gap-2 rounded-xl border-2 p-3 text-center outline-none focus-visible:ring-[3px] focus-visible:ring-ring/50",
        selected ? "border-primary bg-primary-soft font-semibold" : "border-border bg-background",
      )}
    >
      <Icon aria-hidden="true" className="size-8" />
      {label}
      {selected && <Check aria-hidden="true" className="absolute top-2 right-2 size-5 text-primary" />}
    </button>
  )
}
