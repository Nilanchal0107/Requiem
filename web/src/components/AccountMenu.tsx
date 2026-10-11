import { CircleUser, FilePlus, FileText, House, LogIn, LogOut, UserRound } from "lucide-react"
import { Link, useLocation, useNavigate } from "react-router"
import { useT } from "@/i18n"
import { useAuth } from "@/hooks/useAuth"
import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"

export function AccountMenu() {
  const t = useT()
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const here = useLocation()
  const next = encodeURIComponent(here.pathname + here.search)
  const item = "h-12 text-base"

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" size="icon" className="size-12" aria-label={t("common.account")}>
          <CircleUser className="size-6" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        {user && <DropdownMenuLabel className="text-sm text-text-muted">{user.username}</DropdownMenuLabel>}
        <DropdownMenuItem asChild className={item}>
          <Link to="/new">
            <FilePlus /> {t("common.newDpr")}
          </Link>
        </DropdownMenuItem>
        <DropdownMenuItem asChild className={item}>
          <Link to="/">
            <House /> {t("common.home")}
          </Link>
        </DropdownMenuItem>
        <DropdownMenuSeparator />
        {user ? (
          <>
            <DropdownMenuItem asChild className={item}>
              <Link to="/profile">
                <UserRound /> {t("common.profile")}
              </Link>
            </DropdownMenuItem>
            <DropdownMenuItem asChild className={item}>
              <Link to="/reports">
                <FileText /> {t("common.myReports")}
              </Link>
            </DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem
              className={item}
              onSelect={() => logout().then(() => ["/reports", "/profile"].includes(here.pathname) && navigate("/"))}
            >
              <LogOut /> {t("common.logOut")}
            </DropdownMenuItem>
          </>
        ) : (
          <DropdownMenuItem asChild className={item}>
            <Link to={`/login?next=${next}`}>
              <LogIn /> {t("common.logInToSave")}
            </Link>
          </DropdownMenuItem>
        )}
      </DropdownMenuContent>
    </DropdownMenu>
  )
}
