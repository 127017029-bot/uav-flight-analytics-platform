/**
 * @file TopBar.jsx
 * @description Glass-effect top bar with dynamic page title, search input,
 * notification bell, and user avatar. The page title resolves from the current
 * route pathname.
 */

import { useLocation } from 'react-router-dom';
import { Search, Bell } from 'lucide-react';
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
  const title = ROUTE_TITLES[pathname] || 'AEROGUARD';

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
        <div className="topbar__avatar" title="Riswan A">
          RA
        </div>
      </div>
    </header>
  );
}
