import type { LucideIcon } from "lucide-react"

export type ChoiceCardProps = {
  icon: LucideIcon
  label: string
  selected: boolean
  onSelect: () => void
}

export function ChoiceCard(_props: ChoiceCardProps) {
  return <div className="text-xs text-muted-foreground">ChoiceCard</div>
}
