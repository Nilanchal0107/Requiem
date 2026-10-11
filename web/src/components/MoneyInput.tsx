import type { Lang } from "@/i18n/resolve"

export type MoneyInputProps = {
  label: string
  value: number | null
  lang: Lang
  onChange: (value: number | null) => void
}

export function MoneyInput(_props: MoneyInputProps) {
  return <div className="text-xs text-muted-foreground">MoneyInput</div>
}
