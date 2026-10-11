import type { ReactNode } from "react"

export type BottomActionBarProps = {
  children: ReactNode
}

export function BottomActionBar({ children }: BottomActionBarProps) {
  return (
    <div className="fixed inset-x-0 bottom-0 flex gap-2 border-t bg-background p-4 shadow-[0_-2px_8px_rgba(0,0,0,0.08)]">
      {children}
    </div>
  )
}
