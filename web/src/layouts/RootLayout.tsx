import { Outlet } from "react-router"

export default function RootLayout() {
  return (
    <div className="flex min-h-dvh flex-col">
      {/* Placeholder header; ticket 10 swaps in the AppBar. */}
      <header className="h-14 border-b border-border bg-surface" />
      <main className="mx-auto w-full max-w-160 flex-1 px-4 py-4 md:px-6">
        <Outlet />
      </main>
    </div>
  )
}
