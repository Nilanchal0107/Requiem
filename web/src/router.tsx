import { createBrowserRouter } from "react-router"
import type { ComponentType } from "react"
import RootLayout from "@/layouts/RootLayout"

// Each page is its own chunk, so the first load stays small on budget phones.
function page(load: () => Promise<{ default: ComponentType }>) {
  return async () => ({ Component: (await load()).default })
}

export const router = createBrowserRouter([
  {
    Component: RootLayout,
    children: [
      { index: true, lazy: page(() => import("@/pages/Home")) },
      { path: "login", lazy: page(() => import("@/pages/Login")) },
      { path: "new", lazy: page(() => import("@/pages/NewReport")) },
      { path: "reports/:id", lazy: page(() => import("@/pages/Report")) },
      { path: "compare", lazy: page(() => import("@/pages/Compare")) },
      { path: "reports", lazy: page(() => import("@/pages/MyReports")) },
      { path: "profile", lazy: page(() => import("@/pages/Profile")) },
      { path: "*", lazy: page(() => import("@/pages/NotFound")) },
    ],
  },
])
