// src/pages/auth/LoginPage.jsx
// UPDATED — calls Firebase then your FastAPI backend

import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useApp } from '../../context/AppContext'
import { signInWithGoogle, signInWithEmail } from '../../lib/firebase'
import { api, saveAuthResult } from '../../lib/api'
import styles from './AuthPages.module.css'
import darkLogo  from '../../assets/Logo/Dark theme logo.png'
import lightLogo from '../../assets/Logo/Light theme logo.png'

export default function LoginPage() {
  const navigate = useNavigate()
  const { theme } = useApp()
  const [email, setEmail]       = useState('')
  const [password, setPassword] = useState('')
  const [error, setError]       = useState('')
  const [loading, setLoading]   = useState(false)

  // ── After a successful auth, decide where to redirect ────────────────────
  function handleAuthSuccess(result) {
    saveAuthResult(result)
    if (!result.is_onboarded) {
      navigate('/onboarding')
    } else {
      navigate('/')
    }
  }

  // ── Email + Password login ────────────────────────────────────────────────
  async function handleEmailLogin(e) {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      // Step 1: Sign in via Firebase (validates credentials)
      const { idToken } = await signInWithEmail(email, password)
      // Step 2: Send Firebase token to your backend → get your JWT
      const result = await api.firebaseLogin(idToken)
      handleAuthSuccess(result)
    } catch (err) {
      // Friendly Firebase error messages
      const msg = err.message || ''
      if (msg.includes('user-not-found') || msg.includes('wrong-password') || msg.includes('invalid-credential')) {
        setError('Invalid email or password.')
      } else if (msg.includes('too-many-requests')) {
        setError('Too many attempts. Please try again later.')
      } else {
        setError(err.message || 'Login failed. Please try again.')
      }
    } finally {
      setLoading(false)
    }
  }

  // ── Google login ──────────────────────────────────────────────────────────
  async function handleGoogleLogin() {
    setError('')
    setLoading(true)
    try {
      const { idToken } = await signInWithGoogle()
      const result = await api.firebaseLogin(idToken)
      handleAuthSuccess(result)
    } catch (err) {
      if (err.code === 'auth/popup-closed-by-user') {
        setError('')  // user closed popup — not an error
      } else {
        setError(err.message || 'Google sign-in failed.')
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className={styles.authWrapper}>
      <div className={styles.authCard}>
        <div className={styles.authLogo}>
          <img src={theme === 'dark' ? darkLogo : lightLogo} alt="CaliStrength" />
          <p>Sign in to continue</p>
        </div>

        {error && <p className={styles.errorMsg}>{error}</p>}

        <form onSubmit={handleEmailLogin}>
          <div className={styles.formGroup}>
            <label>Email Address</label>
            <input
              type="email"
              className={styles.formInput}
              placeholder="you@example.com"
              value={email}
              onChange={e => setEmail(e.target.value)}
              required
              disabled={loading}
            />
          </div>
          <div className={styles.formGroup}>
            <label>Password</label>
            <input
              type="password"
              className={styles.formInput}
              placeholder="••••••••"
              value={password}
              onChange={e => setPassword(e.target.value)}
              required
              disabled={loading}
            />
          </div>
          <button type="submit" className={styles.btnBrand} disabled={loading}>
            {loading ? 'Signing in…' : 'Sign In'}
          </button>
        </form>

        <div className={styles.divider}>or</div>

        <button className={styles.btnGoogle} onClick={handleGoogleLogin} disabled={loading}>
          <svg viewBox="0 0 24 24" width="20" height="20">
            <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
            <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
            <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/>
            <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
          </svg>
          {loading ? 'Please wait…' : 'Continue with Google'}
        </button>

        <p className={styles.toggleAuth}>
          Don't have an account? <Link to="/signup">Sign up here</Link>
        </p>
      </div>
    </div>
  )
}
