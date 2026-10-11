import { CircleUser, FileText, LogIn, LogOut } from "lucide-react"
import { Link, useLocation, useNavigate } from "react-router"
import { useT } from "@/i18n"
import { useAuth } from "@/hooks/useAuth"
import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"

export function AccountMenu() {
  const t = useT()
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const here = useLocation()
  const next = encodeURIComponent(here.pathname + here.search)

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" size="icon" className="size-12" aria-label={t("common.account")}>
          <CircleUser className="size-6" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        {user ? (
          <>
            <DropdownMenuItem asChild className="h-12 text-base">
              <Link to="/reports">
                <FileText /> {t("common.myReports")}
              </Link>
            </DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem
              className="h-12 text-base"
              onSelect={() => logout().then(() => here.pathname === "/reports" && navigate("/"))}
            >
              <LogOut /> {t("common.logOut")}
            </DropdownMenuItem>
          </>
        ) : (
          <DropdownMenuItem asChild className="h-12 text-base">
            <Link to={`/login?next=${next}`}>
              <LogIn /> {t("common.logInToSave")}
            </Link>
          </DropdownMenuItem>
        )}
      </DropdownMenuContent>
    </DropdownMenu>
  )
}
