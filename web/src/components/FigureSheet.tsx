import type { components } from "@/types/contracts"
import type { Lang } from "@/i18n/resolve"

type Figure = components["schemas"]["Figure"]

export type FigureSheetProps = {
  figure: Figure | null
  lang: Lang
  open: boolean
  onOpenChange: (open: boolean) => void
}

export function FigureSheet(_props: FigureSheetProps) {
  return <div className="text-xs text-muted-foreground">FigureSheet</div>
}
