import { useState } from "react"
import { CircleCheck } from "lucide-react"
import { FigureSheet } from "@/components/FigureSheet"
import { FigureText } from "@/components/FigureText"
import { useT } from "@/i18n"
import { formatFigure } from "@/lib/format"
import type { components } from "@/types/contracts"

type Explanation = components["schemas"]["Explanation"]
type Figure = components["schemas"]["Figure"]

export type ExplanationTabProps = {
  explanation: Explanation | null
  figures: Record<string, Figure>
}

export function ExplanationTab({ explanation, figures }: ExplanationTabProps) {
  const t = useT()
  const [open, setOpen] = useState<Figure | null>(null)
  const [sheetOpen, setSheetOpen] = useState(false)
  if (!explanation) return <p className="text-sm">{t("report.notReady")}</p>
  // Digits follow the language of the text, not the app bar, so a Marathi explanation never mixes scripts.
  const lang = explanation.language
  const count = (n: number) => formatFigure({ id: "", label: "", value: n, unit: "count", source: "computed" }, lang)
  return (
    <div className="flex flex-col gap-4">
      <p className="flex items-center gap-2 text-sm text-text-muted">
        <CircleCheck aria-hidden="true" className="size-5 text-ok" />
        {t("figure.checked")}: {count(explanation.verified)}/{count(explanation.total)}
      </p>
      <ul className="flex flex-col gap-4">
        {explanation.sections.map((section) => (
          <li key={section.key} className="flex flex-col gap-1">
            <h2 className="text-base font-semibold">{section.title}</h2>
            <p className="text-sm leading-relaxed">
              <FigureText
                text={section.text}
                figures={figures}
                lang={lang}
                onOpen={(f) => {
                  setOpen(f)
                  setSheetOpen(true)
                }}
              />
            </p>
          </li>
        ))}
      </ul>
      <FigureSheet figure={open} lang={lang} open={sheetOpen} onOpenChange={setSheetOpen} />
    </div>
  )
}
