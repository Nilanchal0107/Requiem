import { FileText } from "lucide-react"
import type { ReactNode } from "react"

export type EmptyStateProps = {
  title: string
  body?: string
  action?: ReactNode
}

export function EmptyState({ title, body, action }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center gap-3 py-12 text-center">
      <FileText aria-hidden="true" className="size-12 text-text-muted" />
      <h2 className="text-h2">{title}</h2>
      {body && <p className="text-text-muted">{body}</p>}
      {action}
    </div>
  )
}
