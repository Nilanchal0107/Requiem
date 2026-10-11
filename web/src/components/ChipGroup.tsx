export type ChipGroupProps = {
  label: string
  options: { value: string; label: string }[]
  value: string | null
  onChange: (value: string) => void
}

export function ChipGroup(_props: ChipGroupProps) {
  return <div className="text-xs text-muted-foreground">ChipGroup</div>
}
