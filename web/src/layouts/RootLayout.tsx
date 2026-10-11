import { Outlet } from "react-router"
import { AppBar } from "@/components/AppBar"
import { Toaster } from "@/components/ui/sonner"

export default function RootLayout() {
  return (
    <div className="flex min-h-dvh flex-col">
      <AppBar />
      <main className="mx-auto w-full max-w-160 flex-1 px-4 py-4 md:px-6">
        <Outlet />
      </main>
      {/* Above the 72 px bottom action bar, 4 s, polite (ui-ux 4.17). */}
      <Toaster position="bottom-center" offset={96} duration={4000} />
    </div>
  )
}
