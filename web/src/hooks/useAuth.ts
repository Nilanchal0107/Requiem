import { useEffect, useState } from "react"
import { login as loginApi, logout as logoutApi, me, register as registerApi, type Credentials, type UserOut } from "../api.ts"

/** The signed-in Entrepreneur, or null for a guest. `ready` is false until the first /me answer. */
export function useAuth() {
  const [user, setUser] = useState<UserOut | null>(null)
  const [ready, setReady] = useState(false)

  useEffect(() => {
    me()
      .then((res) => setUser(res.user))
      .catch(() => setUser(null))
      .finally(() => setReady(true))
  }, [])

  return {
    user,
    ready,
    login: async (credentials: Credentials) => setUser(await loginApi(credentials)),
    register: async (credentials: Credentials) => setUser(await registerApi(credentials)),
    logout: async () => {
      await logoutApi()
      setUser(null)
    },
  }
}
