import { StrictMode } from "react"
import { createRoot } from "react-dom/client"
import { RouterProvider } from "react-router"
import "@fontsource/mukta/400.css"
import "@fontsource/mukta/500.css"
import "@fontsource/mukta/600.css"
import "@fontsource/mukta/700.css"
import "./index.css"
import { router } from "@/router"

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <RouterProvider router={router} />
  </StrictMode>,
)
