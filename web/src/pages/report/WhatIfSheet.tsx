import { Sheet, SheetContent, SheetHeader, SheetTitle } from "@/components/ui/sheet"
import { useT } from "@/i18n"

export type WhatIfSheetProps = {
  open: boolean
  onOpenChange: (open: boolean) => void
}

export function WhatIfSheet({ open, onOpenChange }: WhatIfSheetProps) {
  const t = useT()
  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent side="bottom">
        <SheetHeader>
          <SheetTitle>{t("report.whatIf.title")}</SheetTitle>
        </SheetHeader>
        <p className="px-4 pb-4 text-sm">{t("report.sheet.empty")}</p>
      </SheetContent>
    </Sheet>
  )
}
