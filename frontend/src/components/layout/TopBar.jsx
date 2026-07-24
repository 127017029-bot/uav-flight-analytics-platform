/**
 * @file TopBar.jsx
 * @description Glass-effect top bar with dynamic page title, search input,
 * notification bell, and user avatar. The page title resolves from the current
 * route pathname.
 */

import { useLocation, useNavigate } from 'react-router-dom';
import { Search, Bell, LogOut } from 'lucide-react';
import './TopBar.css';

/**
 * Map route paths to human-readable page titles.
 * @type {Record<string, string>}
 */
const ROUTE_TITLES = {
  '/': 'Dashboard',
  '/fleet': 'Fleet Management',
  '/flights': 'Flight History',
  '/live-telemetry': 'Live Telemetry',
  '/missions': 'Mission Planner',
  '/maintenance': 'Maintenance',
  '/ai-insights': 'AI Insights',
  '/digital-twin': 'Digital Twin',
  '/settings': 'Settings',
};

/**
 * TopBar — Application header with contextual page title.
 *
 * @returns {JSX.Element}
 */
export default function TopBar() {
  const { pathname } = useLocation();
  const navigate = useNavigate();
  const title = ROUTE_TITLES[pathname] || 'AEROGUARD';

  // Read authenticated user's details for the avatar
  const userStr = localStorage.getItem('uav_user');
  let initials = 'RA';
  let fullName = 'Riswan Ahmed';

  if (userStr) {
    try {
      const user = JSON.parse(userStr);
      fullName = user.full_name || `${user.first_name || ''} ${user.last_name || ''}`.trim() || user.username || fullName;
      if (user.first_name && user.last_name) {
        initials = `${user.first_name[0]}${user.last_name[0]}`.toUpperCase();
      } else if (user.full_name) {
        const parts = user.full_name.split(' ');
        if (parts.length >= 2) {
          initials = `${parts[0][0]}${parts[1][0]}`.toUpperCase();
        } else {
          initials = user.full_name.slice(0, 2).toUpperCase();
        }
      } else if (user.username) {
        initials = user.username.slice(0, 2).toUpperCase();
      }
    } catch (e) {
      console.warn('Failed to parse user from localStorage', e);
    }
  }

  const handleLogout = () => {
    localStorage.removeItem('uav_token');
    localStorage.removeItem('uav_refresh_token');
    localStorage.removeItem('uav_user');
    navigate('/login', { replace: true });
  };

  return (
    <header className="topbar">
      <h1 className="topbar__title">{title}</h1>

      <div className="topbar__actions">
        {/* Search */}
        <div className="topbar__search">
          <Search className="topbar__search-icon" size={16} />
          <input
            type="text"
            className="topbar__search-input"
            placeholder="Search drones, flights…"
            aria-label="Search"
          />
        </div>

        {/* Notifications */}
        <button className="topbar__notification" aria-label="Notifications">
          <Bell size={20} />
          <span className="topbar__badge">3</span>
        </button>

        {/* User avatar */}
        <div className="topbar__avatar" title={fullName}>
          {initials}
        </div>

        {/* Logout */}
        <button
          className="topbar__logout"
          onClick={handleLogout}
          aria-label="Logout"
          title="Logout"
        >
          <LogOut size={18} />
        </button>
      </div>
    </header>
  );
}
