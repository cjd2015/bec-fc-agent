import React from 'react'
import { Navigate, useLocation } from 'react-router-dom'
import { getAuthSession } from '@/utils/auth'

interface Props {
  children: React.ReactElement
}

const RequireAuth: React.FC<Props> = ({ children }) => {
  const location = useLocation()
  const session = getAuthSession()

  if (!session) {
    return <Navigate to="/login" state={{ from: location }} replace />
  }

  return children
}

export default RequireAuth
