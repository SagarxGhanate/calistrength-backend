// src/lib/api.js
// Central API client — all backend calls go through here.

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

function getToken() {
  return localStorage.getItem('cs_token')
}

async function request(path, options = {}) {
  const token = getToken()
  const headers = {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...options.headers,
  }

  const res = await fetch(`${BASE_URL}${path}`, { ...options, headers })
  const data = await res.json().catch(() => ({}))

  if (!res.ok) {
    const msg = data.detail || `Request failed: ${res.status}`
    throw new Error(msg)
  }
  return data
}

// ── Auth ──────────────────────────────────────────────────────────────────────

export const api = {
  // Called after ANY Firebase sign-in (Google or email/password via Firebase)
  firebaseLogin: (idToken) =>
    request('/auth/firebase', {
      method: 'POST',
      body: JSON.stringify({ id_token: idToken }),
    }),

  // Called from SignupPage if NOT using Firebase for email/password
  emailSignup: (name, email, password) =>
    request('/auth/signup', {
      method: 'POST',
      body: JSON.stringify({ name, email, password }),
    }),

  // Called from LoginPage for email/password (non-Firebase flow)
  emailLogin: (email, password) =>
    request('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    }),

  // Called at end of OnboardingPage
  saveOnboarding: (data) =>
    request('/auth/onboarding', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  // Get current user profile
  getMe: () => request('/auth/me'),
}

// ── Token helpers ─────────────────────────────────────────────────────────────

export function saveAuthResult(result) {
  // result = { access_token, user_id, name, email, avatar, is_onboarded }
  localStorage.setItem('cs_token', result.access_token)
  localStorage.setItem('cs_user', JSON.stringify({
    id: result.user_id,
    name: result.name,
    email: result.email,
    avatar: result.avatar,
    is_onboarded: result.is_onboarded,
  }))
}

export function clearAuth() {
  localStorage.removeItem('cs_token')
  localStorage.removeItem('cs_user')
}

export function getStoredUser() {
  try {
    return JSON.parse(localStorage.getItem('cs_user'))
  } catch {
    return null
  }
}

export function isAuthenticated() {
  return !!getToken() && !!getStoredUser()
}
