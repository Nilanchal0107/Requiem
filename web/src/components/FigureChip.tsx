import type { components } from "@/types/contracts"
import type { Lang } from "@/i18n/resolve"
import { formatFigure } from "@/lib/format"

type Figure = components["schemas"]["Figure"]

export type FigureChipProps = {
  figure: Figure
  lang: Lang
  onOpen?: () => void
  /** Replaces the formatted value when the sentence needs its own wording, e.g. "Month 4". */
  text?: string
}

// The ::after widens the tap area to 48 px without breaking the line height of the sentence.
export function FigureChip({ figure, lang, onOpen, text }: FigureChipProps) {
  return (
    <button
      type="button"
      onClick={onOpen}
      className="relative inline font-semibold text-primary underline decoration-dotted decoration-2 underline-offset-4 after:absolute after:inset-x-0 after:-inset-y-3 after:content-['']"
    >
      {text ?? formatFigure(figure, lang)}
    </button>
  )
}
