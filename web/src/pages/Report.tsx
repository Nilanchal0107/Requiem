import { useState } from "react"
import { useParams, useSearchParams } from "react-router"
import { BookOpen, Calculator, FileText, MessageCircle, SlidersHorizontal } from "lucide-react"
import { BottomActionBar } from "@/components/BottomActionBar"
import { ErrorState } from "@/components/ErrorState"
import { FigureSheet } from "@/components/FigureSheet"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { useReport } from "@/hooks/useReport"
import { useLang, useT } from "@/i18n"
import type { Lang } from "@/i18n/resolve"
import { BankTab } from "@/pages/report/BankTab"
import { ChatSheet } from "@/pages/report/ChatSheet"
import { ExplanationTab } from "@/pages/report/ExplanationTab"
import { NumbersTab } from "@/pages/report/NumbersTab"
import { ReportHeader } from "@/pages/report/ReportHeader"
import { parseTab } from "@/pages/report/tab"
import { WhatIfSheet } from "@/pages/report/WhatIfSheet"
import type { components } from "@/types/contracts"

type Figure = components["schemas"]["Figure"]
type Change = components["schemas"]["Change"]

// The page owns fetching, the tab in the URL, the Figure sheet and the two other sheets. Tab content lives in its own files.
export default function Report() {
  const t = useT()
  const lang = useLang()
  const { id = "" } = useParams()
  const [params, setParams] = useSearchParams()
  const { report, error, retry } = useReport(id)
  const [whatIfOpen, setWhatIfOpen] = useState(false)
  // The Path to Yes change the sheet opens with; null when opened from the bottom bar.
  const [whatIfChange, setWhatIfChange] = useState<Change | null>(null)
  const openWhatIf = (change: Change | null) => {
    setWhatIfChange(change)
    setWhatIfOpen(true)
  }
  const [chatOpen, setChatOpen] = useState(false)
  // The figure stays set while the sheet closes, so its content doesn't vanish mid-animation.
  const [shown, setShown] = useState<{ figure: Figure; lang: Lang } | null>(null)
  const [figureOpen, setFigureOpen] = useState(false)
  const openFigure = (figure: Figure, figureLang: Lang) => {
    setShown({ figure, lang: figureLang })
    setFigureOpen(true)
  }

  if (error) {
    return <ErrorState message={t("report.error")} retryLabel={t("report.retry")} onRetry={retry} />
  }
  if (!report) {
    return (
      <div className="flex flex-col gap-2">
        <Skeleton className="h-24 w-full" />
        <p className="text-sm">{t("report.loading")}</p>
      </div>
    )
  }
  const { engine } = report
  if (!engine) return <p className="text-sm">{t("report.notReady")}</p>

  const tab = parseTab(params.get("tab"))
  const hasPath = !!engine.path_to_yes?.changes.length
  const seePath = () => {
    setParams({ tab: "explanation" })
    // The Explanation tab may not be mounted yet, so wait a tick before scrolling to it.
    setTimeout(() => document.getElementById("path-to-yes")?.scrollIntoView(), 50)
  }

  return (
    <div className="flex flex-col gap-4 pb-24">
      <div className="print:hidden">
        <ReportHeader engine={engine} onOpenFigure={(f) => openFigure(f, lang)} onSeePath={hasPath ? seePath : undefined} />
      </div>
      <Tabs value={tab} onValueChange={(next) => setParams({ tab: next })}>
        <div className="sticky top-0 z-10 bg-bg py-1 print:hidden">
          <TabsList className="h-auto w-full">
            <TabsTrigger value="explanation" className="min-h-12 flex-1 gap-2">
              <BookOpen aria-hidden="true" className="size-5" />
              {t("report.tab.explanation")}
            </TabsTrigger>
            <TabsTrigger value="numbers" className="min-h-12 flex-1 gap-2">
              <Calculator aria-hidden="true" className="size-5" />
              {t("report.tab.numbers")}
            </TabsTrigger>
            <TabsTrigger value="bank" className="min-h-12 flex-1 gap-2">
              <FileText aria-hidden="true" className="size-5" />
              {t("report.tab.bank")}
            </TabsTrigger>
          </TabsList>
        </div>
        <TabsContent value="explanation" className="print:hidden">
          <ExplanationTab
            explanation={report.explanation}
            engine={engine}
            onOpenFigure={openFigure}
            onRetry={retry}
            onTry={openWhatIf}
          />
        </TabsContent>
        <TabsContent value="numbers" className="print:hidden">
          <NumbersTab engine={engine} onOpenFigure={openFigure} />
        </TabsContent>
        {/* Always mounted, so printing from any tab prints the Bank View and nothing else. */}
        <TabsContent value="bank" forceMount className="data-[state=inactive]:hidden print:data-[state=inactive]:block!">
          <BankTab report={report} />
        </TabsContent>
      </Tabs>

      <BottomActionBar>
        <Button variant="outline" className="h-12 flex-1 gap-2" onClick={() => openWhatIf(null)}>
          <SlidersHorizontal aria-hidden="true" className="size-5" />
          {t("report.tryChanges")}
        </Button>
        <Button variant="outline" className="h-12 flex-1 gap-2" onClick={() => setChatOpen(true)}>
          <MessageCircle aria-hidden="true" className="size-5" />
          {t("report.ask")}
        </Button>
      </BottomActionBar>
      <FigureSheet figure={shown?.figure ?? null} lang={shown?.lang ?? lang} open={figureOpen} onOpenChange={setFigureOpen} />
      <WhatIfSheet open={whatIfOpen} onOpenChange={setWhatIfOpen} report={report} change={whatIfChange} />
      <ChatSheet
        open={chatOpen}
        onOpenChange={setChatOpen}
        report={report}
        onOpenFigure={openFigure}
        onTry={(change) => {
          setChatOpen(false)
          openWhatIf(change)
        }}
      />
    </div>
  )
}
