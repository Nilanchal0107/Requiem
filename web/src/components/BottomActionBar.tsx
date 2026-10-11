import type { ReactNode } from "react"

export type BottomActionBarProps = {
  children: ReactNode
}

// Keeps the buttons clear of the phone's home indicator.
export function BottomActionBar({ children }: BottomActionBarProps) {
  return (
    <div className="fixed inset-x-0 bottom-0 flex gap-2 border-t bg-background px-4 pt-4 pb-[max(1rem,env(safe-area-inset-bottom))] shadow-[0_-2px_12px_rgb(0_0_0/0.08)]">
      {children}
    </div>
  )
}
