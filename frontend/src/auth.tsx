import { createContext, useContext, useEffect, useMemo, useState, type ReactNode } from 'react'
import { request } from './api'
import type { AuthResult, User } from './types'

type AuthContextType = {
  token: string | null
  user: User | null
  loading: boolean
  setSession: (result: AuthResult) => void
  logout: () => void
}
const AuthContext = createContext<AuthContextType | undefined>(undefined)
const storageKey = 'datsan-sprint1-token'

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(() => localStorage.getItem(storageKey))
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(Boolean(localStorage.getItem(storageKey)))

  useEffect(() => {
    if (!token) { setLoading(false); return }
    let live = true
    request<User>('/auth/me', {}, token)
      .then(u => { if (live) setUser(u) })
      .catch(() => { if (live) { localStorage.removeItem(storageKey); setToken(null); setUser(null) } })
      .finally(() => { if (live) setLoading(false) })
    return () => { live = false }
  }, [token])

  const value = useMemo<AuthContextType>(() => ({
    token, user, loading,
    setSession: result => {
      localStorage.setItem(storageKey, result.access_token)
      setUser(result.user)
      setToken(result.access_token)
      setLoading(false)
    },
    logout: () => { localStorage.removeItem(storageKey); setToken(null); setUser(null); setLoading(false) }
  }), [token, user, loading])
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('AuthProvider missing')
  return ctx
}
