import { Outlet } from "react-router"
import { AppBar } from "@/components/AppBar"

export default function RootLayout() {
  return (
    <div className="flex min-h-dvh flex-col">
      <AppBar />
      <main className="mx-auto w-full max-w-160 flex-1 px-4 py-4 md:px-6">
        <Outlet />
      </main>
    </div>
  )
}
