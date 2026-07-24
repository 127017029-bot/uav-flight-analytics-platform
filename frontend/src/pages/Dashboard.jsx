import React, { useState, useEffect } from 'react';
import {
  Plane,
  Activity,
  HeartPulse,
  AlertTriangle,
  Clock,
} from 'lucide-react';
import KPICard from '../components/common/KPICard';
import StatusBadge from '../components/common/StatusBadge';
import DataTable from '../components/common/DataTable';
import LoadingSpinner from '../components/common/LoadingSpinner';
import { getFleetOverview, listFlights, listAlerts } from '../api/endpoints';
import './Dashboard.css';

/** Columns for the active flights mini-table */
const FLIGHT_COLUMNS = [
  { key: 'drone', label: 'Drone' },
  {
    key: 'status',
    label: 'Status',
    render: (val) => <StatusBadge status={val} size="sm" />,
  },
  { key: 'altitude', label: 'Altitude' },
  { key: 'speed', label: 'Speed' },
  { key: 'battery', label: 'Battery' },
];

/** Helper to format ISO timestamps into relative "time ago" */
const formatTimeAgo = (dateStr) => {
  if (!dateStr) return '';
  const date = new Date(dateStr);
  const now = new Date();
  const diffMs = now - date;
  if (isNaN(diffMs)) return '';
  const diffMins = Math.floor(diffMs / 60000);
  if (diffMins < 1) return 'Just now';
  if (diffMins < 60) return `${diffMins} min ago`;
  const diffHours = Math.floor(diffMins / 60);
  if (diffHours < 24) return `${diffHours} hr ago`;
  const diffDays = Math.floor(diffHours / 24);
  return `${diffDays} days ago`;
};

/**
 * Dashboard — Overview page with KPIs, alerts, and active flights.
 *
 * @returns {JSX.Element}
 */
export default function Dashboard() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [overview, setOverview] = useState(null);
  const [activeFlights, setActiveFlights] = useState([]);
  const [recentAlerts, setRecentAlerts] = useState([]);

  const loadDashboardData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [overviewRes, flightsRes, alertsRes] = await Promise.all([
        getFleetOverview(),
        listFlights({ status: 'in_progress' }),
        listAlerts({ ordering: '-created_at', limit: 5 }),
      ]);

      setOverview(overviewRes.data);

      // Map API flights to DataTable shape
      const flightItems = Array.isArray(flightsRes.data)
        ? flightsRes.data
        : flightsRes.data?.results || [];

      const mappedFlights = flightItems.map((flight) => ({
        id: flight.id,
        drone: flight.drone_name || `Drone ${flight.drone}`,
        status: flight.status === 'in_progress' ? 'Active' : 'Warning',
        altitude: flight.max_altitude_m ? `${Math.round(flight.max_altitude_m)}m` : '0m',
        speed: flight.avg_speed_ms ? `${Math.round(flight.avg_speed_ms * 3.6)} km/h` : '0 km/h',
        battery: flight.end_battery_pct ? `${Math.round(flight.end_battery_pct)}%` : '100%',
      }));
      setActiveFlights(mappedFlights);

      // Map alerts
      const alertItems = Array.isArray(alertsRes.data)
        ? alertsRes.data
        : alertsRes.data?.results || [];

      const mappedAlerts = alertItems.map((alert) => ({
        id: alert.id,
        title: alert.title,
        severity: alert.severity === 'critical' ? 'Critical' : alert.severity === 'warning' ? 'Warning' : 'Info',
        time: formatTimeAgo(alert.created_at),
      }));
      setRecentAlerts(mappedAlerts);

    } catch (err) {
      console.error('Dashboard load failed:', err);
      setError(err.message || 'Failed to fetch dashboard data. Please verify backend connection.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDashboardData();
  }, []);

  if (loading) {
    return (
      <div className="page-loading" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: '400px', gap: 'var(--space-4)' }}>
        <LoadingSpinner size={40} />
        <span style={{ color: 'var(--color-text-secondary)', fontSize: 'var(--text-base)' }}>Loading dashboard metrics...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="page-error card" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: '350px', gap: 'var(--space-4)', padding: 'var(--space-8)', textAlign: 'center', border: '1px solid var(--color-danger-border)', background: 'var(--color-danger-bg)' }}>
        <AlertTriangle size={48} style={{ color: 'var(--color-danger)' }} />
        <h3 style={{ color: 'var(--color-text-primary)' }}>Failed to Load Dashboard</h3>
        <p style={{ color: 'var(--color-text-secondary)', maxWidth: '450px' }}>{error}</p>
        <button className="btn btn-primary" onClick={loadDashboardData} style={{ marginTop: 'var(--space-2)' }}>Retry Connection</button>
      </div>
    );
  }

  return (
    <div className="page-enter">
      {/* ---- KPI Cards ---- */}
      <div className="dashboard__kpi-grid stagger">
        <KPICard
          icon={Plane}
          label="Total Drones"
          value={overview?.total_drones ?? 0}
          trend="+8%"
          trendDirection="up"
          subtitle="vs. last month"
          color="blue"
        />
        <KPICard
          icon={Activity}
          label="Active Flights"
          value={overview?.active ?? 0}
          trend="+15%"
          trendDirection="up"
          subtitle="currently airborne"
          color="green"
        />
        <KPICard
          icon={HeartPulse}
          label="Fleet Health"
          value={`${overview?.avg_fleet_health ?? '100'}%`}
          trend="-1.2%"
          trendDirection="down"
          subtitle="avg. health score"
          color="purple"
        />
        <KPICard
          icon={AlertTriangle}
          label="Alerts"
          value={overview?.active_alerts ?? 0}
          trend="+3"
          trendDirection="up"
          subtitle="requires attention"
          color="amber"
        />
      </div>

      {/* ---- Bottom Panels ---- */}
      <div className="dashboard__panels">
        {/* Recent Alerts */}
        <section className="dashboard__alert-panel">
          <h3 className="dashboard__panel-title">Recent Alerts</h3>
          {recentAlerts.length === 0 ? (
            <div className="page-empty" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: 'var(--space-6)', color: 'var(--color-text-muted)', textAlign: 'center' }}>
              <span style={{ fontSize: '24px' }}>🛡️</span>
              <p style={{ marginTop: 'var(--space-2)' }}>No active alerts detected.</p>
            </div>
          ) : (
            <div className="dashboard__alert-list">
              {recentAlerts.map((alert) => (
                <div key={alert.id} className="dashboard__alert-item">
                  <AlertTriangle
                    size={18}
                    style={{
                      color:
                        alert.severity === 'Critical'
                          ? 'var(--color-danger)'
                          : 'var(--color-warning)',
                      flexShrink: 0,
                      marginTop: 2,
                    }}
                  />
                  <div className="dashboard__alert-content">
                    <p className="dashboard__alert-title">{alert.title}</p>
                    <div className="dashboard__alert-meta">
                      <StatusBadge status={alert.severity} size="sm" />{' '}
                      <span style={{ marginLeft: 8 }}>
                        <Clock size={12} style={{ verticalAlign: -2 }} />{' '}
                        {alert.time}
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>

        {/* Active Flights */}
        <section className="dashboard__flights-panel">
          <h3 className="dashboard__panel-title">Active Flights</h3>
          {activeFlights.length === 0 ? (
            <div className="page-empty" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: 'var(--space-12)', color: 'var(--color-text-muted)', textAlign: 'center' }}>
              <span style={{ fontSize: '32px' }}>🛰️</span>
              <h4 style={{ color: 'var(--color-text-primary)', marginTop: 'var(--space-2)' }}>No Active Flights</h4>
              <p style={{ fontSize: 'var(--text-sm)', color: 'var(--color-text-secondary)' }}>All drones are currently grounded or offline.</p>
            </div>
          ) : (
            <DataTable columns={FLIGHT_COLUMNS} data={activeFlights} />
          )}
        </section>
      </div>
    </div>
  );
}
