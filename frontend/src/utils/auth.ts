export interface AuthSession {
  username: string
  userId: number
  email?: string | null
  token?: string
  displayName?: string | null
}

const STORAGE_KEY = 'bec_user_session'

export function saveAuthSession(session: AuthSession): void {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(session))
}

export function getAuthSession(): AuthSession | null {
  const raw = localStorage.getItem(STORAGE_KEY)
  if (!raw) return null
  try {
    return JSON.parse(raw) as AuthSession
  } catch (error) {
    console.warn('Invalid auth session cache, clearing', error)
    localStorage.removeItem(STORAGE_KEY)
    return null
  }
}

export function updateAuthSession(partial: Partial<AuthSession>): void {
  const current = getAuthSession()
  if (!current) return
  const next = { ...current, ...partial }
  localStorage.setItem(STORAGE_KEY, JSON.stringify(next))
}

export function clearAuthSession(): void {
  localStorage.removeItem(STORAGE_KEY)
}
