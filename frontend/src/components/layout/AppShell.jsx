/**
 * @file AppShell.jsx
 * @description Root layout wrapper that composes the Sidebar, TopBar, and
 * page content (via React Router's Outlet). Manages the sidebar collapsed
 * state locally.
 */

import { useState } from 'react';
import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar';
import TopBar from './TopBar';
import './AppShell.css';

/**
 * AppShell — Top-level layout for all authenticated pages.
 *
 * @returns {JSX.Element}
 */
export default function AppShell() {
  const [collapsed, setCollapsed] = useState(false);

  return (
    <div className="app-shell">
      <Sidebar collapsed={collapsed} onToggle={() => setCollapsed((c) => !c)} />

      <div
        className={`app-shell__content ${
          collapsed ? 'app-shell__content--collapsed' : ''
        }`}
      >
        <TopBar />
        <main className="app-shell__main page-enter">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
