import { useState, type ReactNode } from "react"
import { Button } from "@/components/ui/button"
import { useT } from "@/i18n"

export type ChartFrameProps = {
  title: string
  /** One sentence for screen readers; the chart itself is a picture. */
  summary: string
  chart: ReactNode
  /** The same data as a table, behind the "Show as table" toggle. Rows are already formatted. */
  head: string[]
  rows: string[][]
}

export function ChartFrame({ title, summary, chart, head, rows }: ChartFrameProps) {
  const t = useT()
  const [asTable, setAsTable] = useState(false)
  return (
    <section className="flex flex-col gap-2">
      <h2 className="text-h3">{title}</h2>
      {asTable ? (
        <table className="w-full text-sm tabular-nums">
          <caption className="sr-only">{summary}</caption>
          <thead>
            <tr className="border-b border-border-strong">
              {head.map((h, i) => (
                <th key={h} scope="col" className={i === 0 ? "py-1 text-left font-semibold" : "py-1 text-right font-semibold"}>
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((row, r) => (
              <tr key={r} className="border-b border-border">
                {row.map((cell, i) => (
                  <td key={i} className={i === 0 ? "py-1 text-left" : "py-1 text-right"}>
                    {cell}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      ) : (
        <div role="img" aria-label={summary}>
          {chart}
        </div>
      )}
      <Button variant="ghost" className="h-12 self-start px-0 text-primary" aria-pressed={asTable} onClick={() => setAsTable(!asTable)}>
        {asTable ? t("report.chart.showChart") : t("report.chart.showTable")}
      </Button>
    </section>
  )
}
