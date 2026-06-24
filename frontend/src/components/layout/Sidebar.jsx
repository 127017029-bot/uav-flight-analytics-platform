/**
 * @file Sidebar.jsx
 * @description Premium collapsible sidebar navigation for the UAV Digital Twin
 * Platform. Features gradient brand area, icon + label nav items, active-state
 * glow, and smooth collapse transition.
 */

import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  Plane,
  Route,
  Radio,
  Map,
  Wrench,
  Brain,
  Box,
  Settings,
  ChevronLeft,
  ChevronRight,
} from 'lucide-react';
import './Sidebar.css';

/**
 * Navigation item definition list.
 * @type {Array<{path: string, label: string, icon: React.ElementType}>}
 */
const NAV_ITEMS = [
  { path: '/', label: 'Dashboard', icon: LayoutDashboard },
  { path: '/fleet', label: 'Fleet', icon: Plane },
  { path: '/flights', label: 'Flights', icon: Route },
  { path: '/live-telemetry', label: 'Live Telemetry', icon: Radio },
  { path: '/missions', label: 'Missions', icon: Map },
  { path: '/maintenance', label: 'Maintenance', icon: Wrench },
  { path: '/ai-insights', label: 'AI Insights', icon: Brain },
  { path: '/digital-twin', label: 'Digital Twin', icon: Box },
  { path: '/settings', label: 'Settings', icon: Settings },
];

/**
 * Sidebar — Main navigation component.
 *
 * @param {Object} props
 * @param {boolean} props.collapsed – Whether the sidebar is in collapsed state
 * @param {() => void} props.onToggle – Callback to toggle collapsed state
 * @returns {JSX.Element}
 */
export default function Sidebar({ collapsed, onToggle }) {
  return (
    <aside className={`sidebar ${collapsed ? 'sidebar--collapsed' : ''}`}>
      {/* ---- Brand ---- */}
      <div className="sidebar__brand">
        <div className="sidebar__brand-icon">
          <Plane size={20} />
        </div>
        <span className="sidebar__brand-text">AEROGUARD</span>
      </div>

      {/* ---- Navigation ---- */}
      <nav className="sidebar__nav">
        {NAV_ITEMS.map(({ path, label, icon: Icon }) => (
          <NavLink
            key={path}
            to={path}
            end={path === '/'}
            className={({ isActive }) =>
              `sidebar__nav-item ${isActive ? 'active' : ''}`
            }
          >
            <Icon className="sidebar__nav-icon" size={20} />
            <span className="sidebar__nav-label">{label}</span>
            {collapsed && <span className="sidebar__tooltip">{label}</span>}
          </NavLink>
        ))}
      </nav>

      {/* ---- Collapse toggle ---- */}
      <button
        className="sidebar__toggle"
        onClick={onToggle}
        aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
      >
        {collapsed ? <ChevronRight size={20} /> : <ChevronLeft size={20} />}
      </button>
    </aside>
  );
}
