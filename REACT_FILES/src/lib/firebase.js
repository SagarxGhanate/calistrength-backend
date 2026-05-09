// src/lib/firebase.js
// Firebase initialization + Google sign-in helper.
// You fill in the firebaseConfig values from your Firebase Console.

import { initializeApp } from 'firebase/app'
import {
  getAuth,
  GoogleAuthProvider,
  signInWithPopup,
  signInWithEmailAndPassword,
  createUserWithEmailAndPassword,
  signOut as firebaseSignOut,
} from 'firebase/auth'

// ── STEP: Replace these with your actual Firebase project config ──────────────
// Firebase Console → Project Settings → Your apps → Web app → Config
const firebaseConfig = {
  apiKey:            import.meta.env.VITE_FIREBASE_API_KEY,
  authDomain:        import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
  projectId:         import.meta.env.VITE_FIREBASE_PROJECT_ID,
  storageBucket:     import.meta.env.VITE_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID,
  appId:             import.meta.env.VITE_FIREBASE_APP_ID,
}

const firebaseApp  = initializeApp(firebaseConfig)
export const auth  = getAuth(firebaseApp)
const googleProvider = new GoogleAuthProvider()
googleProvider.setCustomParameters({ prompt: 'select_account' })

// ── Sign in with Google popup ─────────────────────────────────────────────────
export async function signInWithGoogle() {
  const result = await signInWithPopup(auth, googleProvider)
  const idToken = await result.user.getIdToken()
  return { idToken, user: result.user }
}

// ── Sign in with email/password (Firebase handles it) ─────────────────────────
export async function signInWithEmail(email, password) {
  const result = await signInWithEmailAndPassword(auth, email, password)
  const idToken = await result.user.getIdToken()
  return { idToken, user: result.user }
}

// ── Register with email/password via Firebase ─────────────────────────────────
export async function registerWithEmail(email, password) {
  const result = await createUserWithEmailAndPassword(auth, email, password)
  const idToken = await result.user.getIdToken()
  return { idToken, user: result.user }
}

// ── Sign out ──────────────────────────────────────────────────────────────────
export async function signOut() {
  await firebaseSignOut(auth)
}
