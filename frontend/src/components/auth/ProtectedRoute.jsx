import React from 'react';
import { Navigate } from 'react-router-dom';

/**
 * ProtectedRoute wraps dashboard views that require authentication.
 * If no valid session token exists in localStorage, it redirects to the login screen.
 *
 * @param {Object} props
 * @param {React.ReactNode} props.children
 * @returns {JSX.Element}
 */
export default function ProtectedRoute({ children }) {
  const token = localStorage.getItem('uav_token');

  if (!token) {
    return <Navigate to="/login" replace />;
  }

  return children;
}
