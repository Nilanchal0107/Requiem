import { Link } from "react-router"
import { AccountMenu } from "@/components/AccountMenu"
import { LanguageSwitch } from "@/components/LanguageSwitch"

// Back is V2 and not part of this ticket; `onBack` is kept so callers stay valid.
export type AppBarProps = {
  onBack?: () => void
}

export function AppBar(_props: AppBarProps) {
  return (
    <header className="flex h-14 print:hidden items-center border-b border-border bg-surface px-4">
      <Link to="/" className="flex min-h-12 items-center text-lg font-semibold text-primary" translate="no">
        Requiem
      </Link>
      <div className="ml-auto flex items-center gap-1">
        <LanguageSwitch />
        <AccountMenu />
      </div>
    </header>
  )
}
