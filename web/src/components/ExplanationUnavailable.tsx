import { TriangleAlert } from "lucide-react"
import { Button } from "@/components/ui/button"
import { useT } from "@/i18n"

export type ExplanationUnavailableProps = {
  onRetry?: () => void
}

export function ExplanationUnavailable({ onRetry }: ExplanationUnavailableProps) {
  const t = useT()
  return (
    <div role="status" className="flex flex-col items-start gap-2 rounded-card border border-warn bg-warn-soft p-4 text-warn">
      <p className="flex items-start gap-2 text-body">
        <TriangleAlert aria-hidden="true" className="mt-1 size-5 shrink-0" />
        {t("report.explanationUnavailable")}
      </p>
      {onRetry && (
        <Button variant="outline" className="h-12" onClick={onRetry}>
          {t("report.retry")}
        </Button>
      )}
    </div>
  )
}
