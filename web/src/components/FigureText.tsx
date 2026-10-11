import { Fragment } from "react"
import { FigureChip } from "@/components/FigureChip"
import type { Lang } from "@/i18n/resolve"
import { formatFigure } from "@/lib/format"
import type { components } from "@/types/contracts"

type Figure = components["schemas"]["Figure"]

export type FigureTextProps = {
  text: string
  figures: Record<string, Figure>
  lang: Lang
  onOpen?: (figure: Figure) => void
}

// Ids are snake_case with optional dotted groups ("cost.animals", "dairy.min_dscr"). split() with one
// capture group puts the id at every odd index.
const PLACEHOLDER = /\{\{\s*([a-z0-9_.]+)\s*\}\}/gi

/** The same text as a plain string, for places that must not hold buttons (the printed Bank DPR). */
export function fillFigures(text: string, figures: Record<string, Figure>, lang: Lang): string {
  return text.replace(PLACEHOLDER, (_, id: string) => (figures[id] ? formatFigure(figures[id], lang) : "–"))
}

/** Turns text with {{figure_id}} into text plus FigureChips. An unknown id shows a dash, never raw braces. */
export function FigureText({ text, figures, lang, onOpen }: FigureTextProps) {
  return text.split(PLACEHOLDER).map((part, i) => {
    if (i % 2 === 0) return <Fragment key={i}>{part}</Fragment>
    const figure = figures[part]
    return figure ? <FigureChip key={i} figure={figure} lang={lang} onOpen={() => onOpen?.(figure)} /> : <Fragment key={i}>–</Fragment>
  })
}
