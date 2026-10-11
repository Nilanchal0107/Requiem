import { AccountMenu } from "@/components/AccountMenu"
import { LanguageSwitch } from "@/components/LanguageSwitch"

// Back is V2 and not part of this ticket; `onBack` is kept so callers stay valid.
export type AppBarProps = {
  onBack?: () => void
}

export function AppBar(_props: AppBarProps) {
  return (
    <header className="flex h-14 print:hidden items-center border-b border-border bg-surface px-4">
      <span className="text-lg font-semibold text-primary">Requiem</span>
      <div className="ml-auto flex items-center gap-1">
        <LanguageSwitch />
        <AccountMenu />
      </div>
    </header>
  )
}
