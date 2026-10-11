import { cn } from "@/lib/utils"

export type DprTableProps = {
  head: string[]
  rows: string[][]
  /** Bold the last row, for totals. */
  total?: boolean
  /** Rows from this index on are hidden on screen but still print. */
  collapseFrom?: number
}

// A real table everywhere. With more than three columns it reflows into stacked cells on a phone
// (each cell carries its column name), and goes back to a table on A4 because that is wider than 640 px.
export function DprTable({ head, rows, total, collapseFrom = Infinity }: DprTableProps) {
  const stack = head.length > 3
  return (
    <table className="w-full text-sm tabular-nums">
      <thead className={cn(stack && "max-sm:sr-only")}>
        <tr className="border-b border-border-strong">
          {head.map((h, i) => (
            <th key={h} scope="col" className={cn("py-1 font-semibold", i === 0 ? "text-left" : "text-right")}>
              {h}
            </th>
          ))}
        </tr>
      </thead>
      <tbody>
        {rows.map((row, r) => (
          <tr
            key={r}
            className={cn(
              "border-b border-border align-top",
              stack && "max-sm:grid max-sm:grid-cols-2 max-sm:gap-x-4 max-sm:py-2",
              r >= collapseFrom && "hidden print:table-row",
              total && r === rows.length - 1 && "font-semibold",
            )}
          >
            {row.map((cell, i) => (
              <td
                key={i}
                data-label={head[i]}
                className={cn(
                  "py-1",
                  i === 0 ? "text-left" : "text-right",
                  stack && "max-sm:text-left max-sm:before:block max-sm:before:text-sm max-sm:before:font-normal max-sm:before:text-text-muted max-sm:before:content-[attr(data-label)]",
                )}
              >
                {cell}
              </td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  )
}
