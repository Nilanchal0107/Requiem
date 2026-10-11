import { useState, type FormEvent } from "react"
import { Eye, EyeOff } from "lucide-react"
import { Navigate, useNavigate, useSearchParams } from "react-router"
import { ApiError } from "@/api"
import { useT } from "@/i18n"
import { useAuth } from "@/hooks/useAuth"
import { safeNext } from "@/lib/next"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"

export default function Login() {
  const t = useT()
  const navigate = useNavigate()
  const next = safeNext(useSearchParams()[0].get("next"))
  const auth = useAuth()
  const [username, setUsername] = useState("")
  const [password, setPassword] = useState("")
  const [show, setShow] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function submit(action: "login" | "register", event: FormEvent) {
    event.preventDefault()
    setError(null)
    try {
      await auth[action]({ username, password }) // the signed-in redirect below returns to `next`
    } catch (err) {
      const status = err instanceof ApiError ? err.status : 0
      setError(t(status === 401 ? "login.error.401" : status === 409 ? "login.error.409" : "login.error.other"))
    }
  }

  if (!auth.ready) return null
  // Already signed in: go straight back to where the Entrepreneur came from.
  if (auth.user) return <Navigate to={next} replace />

  return (
    <div className="flex flex-col gap-4">
      <h1 className="text-h1">{t("login.title")}</h1>
      <form className="flex flex-col gap-3" onSubmit={(e) => submit("login", e)}>
        <Input
          placeholder={t("login.username")}
          aria-label={t("login.username")}
          autoComplete="username"
          className="h-12"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
        />
        <div className="relative">
          <Input
            type={show ? "text" : "password"}
            placeholder={t("login.password")}
            aria-label={t("login.password")}
            autoComplete="current-password"
            className="h-12 pr-12"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          <Button
            type="button"
            variant="ghost"
            size="icon"
            className="absolute top-0 right-0 size-12"
            aria-label={t(show ? "login.hide" : "login.show")}
            onClick={() => setShow(!show)}
          >
            {show ? <EyeOff /> : <Eye />}
          </Button>
        </div>
        {error && (
          <p role="alert" className="text-sm text-destructive">
            {error}
          </p>
        )}
        <Button type="submit" className="h-12">
          {t("login.logIn")}
        </Button>
        <Button type="button" variant="outline" className="h-12" onClick={(e) => submit("register", e)}>
          {t("login.register")}
        </Button>
      </form>
      <Button variant="outline" className="h-12" onClick={() => navigate("/")}>
        {t("login.guest")}
      </Button>
    </div>
  )
}
