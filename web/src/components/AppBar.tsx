// Stub: renders only the product name. Language switch, account menu and Back are V2.
export type AppBarProps = {
  onBack?: () => void
}

export function AppBar(_props: AppBarProps) {
  return (
    <header className="flex h-14 print:hidden items-center border-b border-border bg-surface px-4">
      <span className="text-lg font-semibold text-primary">Requiem</span>
    </header>
  )
}
