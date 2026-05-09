// src/pages/auth/SignupPage.jsx
// UPDATED — registers via Firebase then sends token to your backend

import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useApp } from '../../context/AppContext'
import { registerWithEmail, signInWithGoogle } from '../../lib/firebase'
import { api, saveAuthResult } from '../../lib/api'
import styles from './AuthPages.module.css'
import darkLogo  from '../../assets/Logo/Dark theme logo.png'
import lightLogo from '../../assets/Logo/Light theme logo.png'

export default function SignupPage() {
  const navigate = useNavigate()
  const { theme } = useApp()
  const [name, setName]         = useState('')
  const [email, setEmail]       = useState('')
  const [password, setPassword] = useState('')
  const [error, setError]       = useState('')
  const [loading, setLoading]   = useState(false)

  function handleAuthSuccess(result) {
    saveAuthResult(result)
    navigate('/onboarding')  // always onboard after signup
  }

  async function handleEmailSignup(e) {
    e.preventDefault()
    setError('')
    if (password.length < 6) {
      setError('Password must be at least 6 characters.')
      return
    }
    setLoading(true)
    try {
      // Step 1: Create user in Firebase (handles password security)
      const { idToken } = await registerWithEmail(email, password)
      // Step 2: Send token to backend — backend stores user in MySQL with the name
      // We use the firebase endpoint but also pass name via a custom header or
      // use the direct /auth/signup endpoint that accepts name separately.
      // Since Firebase doesn't store "name" on register, we call /auth/firebase
      // then update the profile — simplest: call /auth/signup directly instead.
      const result = await api.emailSignup(name, email, password)
      handleAuthSuccess(result)
    } catch (err) {
      const msg = err.message || ''
      if (msg.includes('email-already-in-use')) {
        setError('This email is already registered. Please log in.')
      } else if (msg.includes('weak-password')) {
        setError('Password is too weak. Use at least 6 characters.')
      } else {
        setError(msg || 'Sign up failed. Please try again.')
      }
    } finally {
      setLoading(false)
    }
  }

  async function handleGoogleSignup() {
    setError('')
    setLoading(true)
    try {
      const { idToken } = await signInWithGoogle()
      const result = await api.firebaseLogin(idToken)
      handleAuthSuccess(result)
    } catch (err) {
      if (err.code !== 'auth/popup-closed-by-user') {
        setError(err.message || 'Google sign-up failed.')
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
          <p>Create your account</p>
        </div>

        {error && <p className={styles.errorMsg}>{error}</p>}

        <form onSubmit={handleEmailSignup}>
          <div className={styles.formGroup}>
            <label>Full Name</label>
            <input type="text" className={styles.formInput} placeholder="Your name"
              value={name} onChange={e => setName(e.target.value)} required disabled={loading} />
          </div>
          <div className={styles.formGroup}>
            <label>Email Address</label>
            <input type="email" className={styles.formInput} placeholder="you@example.com"
              value={email} onChange={e => setEmail(e.target.value)} required disabled={loading} />
          </div>
          <div className={styles.formGroup}>
            <label>Password</label>
            <input type="password" className={styles.formInput} placeholder="Min. 6 characters"
              value={password} onChange={e => setPassword(e.target.value)} required disabled={loading} />
          </div>
          <button type="submit" className={styles.btnBrand} disabled={loading}>
            {loading ? 'Creating account…' : 'Create Account'}
          </button>
        </form>

        <div className={styles.divider}>or</div>

        <button className={styles.btnGoogle} onClick={handleGoogleSignup} disabled={loading}>
          <svg viewBox="0 0 24 24" width="20" height="20">
            <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
            <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
            <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/>
            <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
          </svg>
          {loading ? 'Please wait…' : 'Continue with Google'}
        </button>

        <p className={styles.toggleAuth}>
          Already have an account? <Link to="/login">Sign in</Link>
        </p>
      </div>
    </div>
  )
}
