// src/components/ui/ProtectedRoute.jsx
// UPDATED — checks for real JWT token instead of localStorage data shape

import { Navigate, Outlet } from 'react-router-dom'
import { isAuthenticated, getStoredUser } from '../../lib/api'

export default function ProtectedRoute() {
  if (!isAuthenticated()) {
    return <Navigate to="/login" replace />
  }

  const user = getStoredUser()
  if (user && !user.is_onboarded) {
    return <Navigate to="/onboarding" replace />
  }

  return <Outlet />
}
