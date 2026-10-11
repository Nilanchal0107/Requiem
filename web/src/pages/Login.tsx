import { useState, type FormEvent } from "react"
import { useNavigate } from "react-router"
import { useT } from "@/i18n"
import { useAuth } from "@/hooks/useAuth"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"

export default function Login() {
  const t = useT()
  const navigate = useNavigate()
  const auth = useAuth()
  const [username, setUsername] = useState("")
  const [password, setPassword] = useState("")
  const [error, setError] = useState<string | null>(null)

  async function submit(action: "login" | "register", event: FormEvent) {
    event.preventDefault()
    setError(null)
    try {
      await auth[action]({ username, password })
      setPassword("")
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err))
    }
  }

  if (!auth.ready) return null

  if (auth.user) {
    return (
      <div className="flex flex-col gap-4">
        <h1 className="text-h1">{t("login.title")}</h1>
        <p>
          {t("login.signedIn")} {auth.user.username}
        </p>
        <Button variant="outline" onClick={() => auth.logout()}>
          {t("login.logOut")}
        </Button>
      </div>
    )
  }

  return (
    <div className="flex flex-col gap-4">
      <h1 className="text-h1">{t("login.title")}</h1>
      <form className="flex flex-col gap-3" onSubmit={(e) => submit("login", e)}>
        <Input placeholder={t("login.username")} value={username} onChange={(e) => setUsername(e.target.value)} />
        <Input
          type="password"
          placeholder={t("login.password")}
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
        <Button type="submit">{t("login.logIn")}</Button>
        <Button type="button" variant="outline" onClick={(e) => submit("register", e)}>
          {t("login.register")}
        </Button>
      </form>
      <Button variant="ghost" onClick={() => navigate("/")}>
        {t("login.guest")}
      </Button>
      {error && <p className="text-sm text-destructive">{error}</p>}
    </div>
  )
}
