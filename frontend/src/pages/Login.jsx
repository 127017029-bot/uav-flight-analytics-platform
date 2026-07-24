import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Plane, Eye, EyeOff, AlertTriangle, Loader2 } from 'lucide-react';
import { login as loginApi } from '../api/endpoints';
import './Login.css';

/**
 * Login — User authentication page with modern dark UI matching AeroGuard theme.
 *
 * @returns {JSX.Element}
 */
export default function Login() {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // If user is already authenticated, redirect to Dashboard
  useEffect(() => {
    const token = localStorage.getItem('uav_token');
    if (token) {
      navigate('/', { replace: true });
    }
  }, [navigate]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!email || !password) {
      setError('Please enter both email and password.');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await loginApi({ email, password });
      
      // Handle success
      const token = response.data?.access || response.data?.token || '';
      const refresh = response.data?.refresh || '';
      const user = response.data?.user || response.data || {};

      if (!token) {
        throw new Error('Authentication succeeded but no token was returned.');
      }

      localStorage.setItem('uav_token', token);
      if (refresh) {
        localStorage.setItem('uav_refresh_token', refresh);
      }
      localStorage.setItem('uav_user', JSON.stringify(user));

      if (rememberMe) {
        localStorage.setItem('uav_remember_email', email);
      } else {
        localStorage.removeItem('uav_remember_email');
      }

      // Redirect to the main application
      navigate('/', { replace: true });
    } catch (err) {
      console.error('Login error:', err);
      // Retrieve friendly error message from standardized client response
      setError(err.message || 'Invalid email or password. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // Populate remembered email if present
  useEffect(() => {
    const rememberedEmail = localStorage.getItem('uav_remember_email');
    if (rememberedEmail) {
      setEmail(rememberedEmail);
      setRememberMe(true);
    }
  }, []);

  return (
    <div className="login-container page-enter">
      <div className="login-bg-glow" />
      
      <div className="login-card card">
        <div className="login-header">
          <div className="login-logo">
            <Plane size={28} />
          </div>
          <h1>AEROGUARD</h1>
          <p className="login-subtitle">UAV Digital Twin & Operations Platform</p>
        </div>

        {error && (
          <div className="login-error-alert" role="alert">
            <AlertTriangle size={18} className="error-icon" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="login-form">
          <div className="form-group">
            <label htmlFor="email">Email Address</label>
            <input
              type="email"
              id="email"
              className="form-control"
              placeholder="name@organization.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              autoComplete="email"
              disabled={loading}
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Password</label>
            <div className="password-input-wrapper">
              <input
                type={showPassword ? 'text' : 'password'}
                id="password"
                className="form-control password-control"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                autoComplete="current-password"
                disabled={loading}
              />
              <button
                type="button"
                className="password-toggle-btn"
                onClick={() => setShowPassword((show) => !show)}
                aria-label={showPassword ? 'Hide password' : 'Show password'}
                disabled={loading}
              >
                {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
              </button>
            </div>
          </div>

          <div className="login-options">
            <label className="remember-me">
              <input
                type="checkbox"
                checked={rememberMe}
                onChange={(e) => setRememberMe(e.target.checked)}
                disabled={loading}
              />
              <span>Remember Me</span>
            </label>
            <a href="#forgot" className="forgot-password-link" onClick={(e) => e.preventDefault()}>
              Forgot Password?
            </a>
          </div>

          <button
            type="submit"
            className="btn btn-primary btn-block login-submit-btn"
            disabled={loading}
          >
            {loading ? (
              <span className="btn-loading-wrapper">
                <Loader2 size={16} className="spinner" />
                Signing In...
              </span>
            ) : (
              'Sign In'
            )}
          </button>
        </form>

        <div className="login-footer">
          <p>AeroGuard Operations Control Console</p>
          <span className="app-version">v1.2.0-prod</span>
        </div>
      </div>
    </div>
  );
}
