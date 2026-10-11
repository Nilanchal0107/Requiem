import { useEffect, useSyncExternalStore } from "react"
import { login as loginApi, logout as logoutApi, me, register as registerApi, type Credentials, type UserOut } from "../api.ts"

// One shared store, so the app bar and the Login page see the same signed-in Entrepreneur.
type State = { user: UserOut | null; ready: boolean }
let state: State = { user: null, ready: false }
let started = false
const listeners = new Set<() => void>()

function set(next: State) {
  state = next
  listeners.forEach((notify) => notify())
}

function start() {
  if (started) return
  started = true
  me()
    .then((res) => set({ user: res.user, ready: true }))
    .catch(() => set({ user: null, ready: true }))
}

/** The signed-in Entrepreneur, or null for a guest. `ready` is false until the first /me answer. */
export function useAuth() {
  const { user, ready } = useSyncExternalStore(
    (notify) => {
      listeners.add(notify)
      return () => listeners.delete(notify)
    },
    () => state,
  )
  useEffect(start, [])

  return {
    user,
    ready,
    login: async (credentials: Credentials) => set({ user: await loginApi(credentials), ready: true }),
    register: async (credentials: Credentials) => set({ user: await registerApi(credentials), ready: true }),
    logout: async () => {
      await logoutApi()
      set({ user: null, ready: true })
    },
  }
}
