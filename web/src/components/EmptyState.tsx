import type { ReactNode } from "react"

export type EmptyStateProps = {
  title: string
  body?: string
  action?: ReactNode
}

export function EmptyState(_props: EmptyStateProps) {
  return <div className="text-xs text-muted-foreground">EmptyState</div>
}
