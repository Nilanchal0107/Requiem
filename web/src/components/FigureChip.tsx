import type { components } from "@/types/contracts"
import type { Lang } from "@/i18n/resolve"

type Figure = components["schemas"]["Figure"]

export type FigureChipProps = {
  figure: Figure
  lang: Lang
  onOpen?: () => void
}

export function FigureChip(_props: FigureChipProps) {
  return <span className="text-xs text-muted-foreground">FigureChip</span>
}
