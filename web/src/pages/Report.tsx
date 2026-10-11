import { useState } from "react"
import { useParams, useSearchParams } from "react-router"
import { BookOpen, Calculator, FileText, MessageCircle, SlidersHorizontal } from "lucide-react"
import { BottomActionBar } from "@/components/BottomActionBar"
import { ErrorState } from "@/components/ErrorState"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { useReport } from "@/hooks/useReport"
import { useT } from "@/i18n"
import { BankTab } from "@/pages/report/BankTab"
import { ChatSheet } from "@/pages/report/ChatSheet"
import { ExplanationTab } from "@/pages/report/ExplanationTab"
import { NumbersTab } from "@/pages/report/NumbersTab"
import { ReportHeader } from "@/pages/report/ReportHeader"
import { parseTab } from "@/pages/report/tab"
import { WhatIfSheet } from "@/pages/report/WhatIfSheet"

// The page owns fetching, the tab in the URL and the two sheets. Tab content lives in its own files.
export default function Report() {
  const t = useT()
  const { id = "" } = useParams()
  const [params, setParams] = useSearchParams()
  const { report, error, retry } = useReport(id)
  const [whatIfOpen, setWhatIfOpen] = useState(false)
  const [chatOpen, setChatOpen] = useState(false)

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
  if (!report.engine) return <p className="text-sm">{t("report.notReady")}</p>

  return (
    <div className="flex flex-col gap-4 pb-24">
      <ReportHeader engine={report.engine} />
      <Tabs value={parseTab(params.get("tab"))} onValueChange={(tab) => setParams({ tab })}>
        <TabsList className="w-full">
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
        <TabsContent value="explanation">
          <ExplanationTab explanation={report.explanation} figures={report.engine.figures} />
        </TabsContent>
        <TabsContent value="numbers">
          <NumbersTab engine={report.engine} />
        </TabsContent>
        <TabsContent value="bank">
          <BankTab />
        </TabsContent>
      </Tabs>

      <BottomActionBar>
        <Button variant="outline" className="h-12 flex-1 gap-2" onClick={() => setWhatIfOpen(true)}>
          <SlidersHorizontal aria-hidden="true" className="size-5" />
          {t("report.tryChanges")}
        </Button>
        <Button variant="outline" className="h-12 flex-1 gap-2" onClick={() => setChatOpen(true)}>
          <MessageCircle aria-hidden="true" className="size-5" />
          {t("report.ask")}
        </Button>
      </BottomActionBar>
      <WhatIfSheet open={whatIfOpen} onOpenChange={setWhatIfOpen} />
      <ChatSheet open={chatOpen} onOpenChange={setChatOpen} />
    </div>
  )
}
