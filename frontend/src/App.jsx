import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import AppShell from './components/layout/AppShell';
import Dashboard from './pages/Dashboard';
import Fleet from './pages/Fleet';
import Flights from './pages/Flights';
import LiveTelemetry from './pages/LiveTelemetry';
import Missions from './pages/Missions';
import Maintenance from './pages/Maintenance';
import AIInsights from './pages/AIInsights';
import DigitalTwin from './pages/DigitalTwin';
import Settings from './pages/Settings';
import './App.css';

/**
 * App - Root component with routing configuration.
 * All routes are nested under AppShell layout (sidebar + topbar).
 */
function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<AppShell />}>
          <Route index element={<Dashboard />} />
          <Route path="fleet" element={<Fleet />} />
          <Route path="flights" element={<Flights />} />
          <Route path="live-telemetry" element={<LiveTelemetry />} />
          <Route path="missions" element={<Missions />} />
          <Route path="maintenance" element={<Maintenance />} />
          <Route path="ai-insights" element={<AIInsights />} />
          <Route path="digital-twin" element={<DigitalTwin />} />
          <Route path="settings" element={<Settings />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;