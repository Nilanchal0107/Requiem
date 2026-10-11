import { SourceBadge } from "@/components/SourceBadge"
import { Sheet, SheetContent, SheetDescription, SheetHeader, SheetTitle } from "@/components/ui/sheet"
import { useT } from "@/i18n"
import type { Lang } from "@/i18n/resolve"
import { formatFigure } from "@/lib/format"
import type { components } from "@/types/contracts"

type Figure = components["schemas"]["Figure"]

export type FigureSheetProps = {
  figure: Figure | null
  lang: Lang
  open: boolean
  onOpenChange: (open: boolean) => void
}

export function FigureSheet({ figure, lang, open, onOpenChange }: FigureSheetProps) {
  const t = useT()
  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent side="bottom" className="max-h-[85dvh] overflow-y-auto">
        {figure && (
          <>
            <SheetHeader>
              <SheetTitle>{t("figure.why")}</SheetTitle>
              <SheetDescription>{figure.label}</SheetDescription>
            </SheetHeader>
            <div className="flex flex-col gap-3 px-4 pb-6">
              <p className="text-3xl font-bold">{formatFigure(figure, lang)}</p>
              <div>
                <SourceBadge source={figure.source} />
              </div>
              {figure.source === "assumption" && <p className="text-sm">{t("figure.estimate")}</p>}
              {figure.formula && (
                <section>
                  <h3 className="text-sm font-semibold">{t("figure.how")}</h3>
                  <p className="text-sm">{figure.formula}</p>
                </section>
              )}
              {figure.inputs && Object.keys(figure.inputs).length > 0 && (
                <dl className="flex flex-col gap-1 text-sm">
                  {Object.entries(figure.inputs).map(([name, value]) => (
                    <div key={name} className="flex justify-between gap-4 border-b border-border py-1">
                      <dt className="text-text-muted">{name.replace(/_/g, " ")}</dt>
                      <dd className="font-semibold">{formatFigure({ ...figure, value, unit: "count" }, lang)}</dd>
                    </div>
                  ))}
                </dl>
              )}
              {figure.note && <p className="text-sm text-text-muted">{figure.note}</p>}
            </div>
          </>
        )}
      </SheetContent>
    </Sheet>
  )
}
