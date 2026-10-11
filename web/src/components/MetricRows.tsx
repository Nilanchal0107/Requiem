import { Check } from "lucide-react"
import type { ReactNode } from "react"
import { useT } from "@/i18n"

export type MetricRowsProps = {
  rows: { label: string; values: ReactNode[]; betterIndex?: number }[]
}

// Label on the left, value(s) on the right. The better value gets a check and the word, never colour alone.
export function MetricRows({ rows }: MetricRowsProps) {
  const t = useT()
  return (
    <dl className="flex flex-col">
      {rows.map((row) => (
        <div key={row.label} className="flex items-start justify-between gap-4 border-b border-border py-2">
          <dt className="text-sm">{row.label}</dt>
          <dd className="flex gap-2">
            {row.values.map((value, i) => (
              <div key={i} className="flex min-w-22 flex-col items-end gap-1 text-right text-sm">
                {value}
                {row.betterIndex === i && (
                  <span className="flex items-center gap-1 text-ok">
                    <Check aria-hidden="true" className="size-4" />
                    {t("report.better")}
                  </span>
                )}
              </div>
            ))}
          </dd>
        </div>
      ))}
    </dl>
  )
}
