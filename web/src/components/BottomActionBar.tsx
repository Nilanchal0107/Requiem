import type { ReactNode } from "react"

export type BottomActionBarProps = {
  children: ReactNode
}

export function BottomActionBar(_props: BottomActionBarProps) {
  return <div className="text-xs text-muted-foreground">BottomActionBar</div>
}
