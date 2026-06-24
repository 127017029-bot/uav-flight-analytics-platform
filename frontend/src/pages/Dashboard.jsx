/**
 * @file Dashboard.jsx
 * @description Main dashboard page with KPI cards, recent alerts, and active
 * flights table. Uses staggered fade-in animations for a premium feel.
 */

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
import './Dashboard.css';

/** Mock active-flight data */
const ACTIVE_FLIGHTS = [
  { id: 'f1', drone: 'Eagle-1', status: 'Active', altitude: '120m', speed: '45 km/h', battery: '78%' },
  { id: 'f2', drone: 'Hawk-3', status: 'Active', altitude: '85m', speed: '62 km/h', battery: '64%' },
  { id: 'f3', drone: 'Falcon-7', status: 'Warning', altitude: '200m', speed: '38 km/h', battery: '23%' },
];

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

/** Mock recent alerts */
const RECENT_ALERTS = [
  {
    id: 'a1',
    title: 'Battery critically low on Falcon-7',
    severity: 'Critical',
    time: '2 min ago',
  },
  {
    id: 'a2',
    title: 'Motor vibration anomaly on Hawk-3',
    severity: 'Warning',
    time: '18 min ago',
  },
  {
    id: 'a3',
    title: 'Geofence boundary approach — Eagle-1',
    severity: 'Warning',
    time: '34 min ago',
  },
];

/**
 * Dashboard — Overview page with KPIs, alerts, and active flights.
 *
 * @returns {JSX.Element}
 */
export default function Dashboard() {
  return (
    <div>
      {/* ---- KPI Cards ---- */}
      <div className="dashboard__kpi-grid stagger">
        <KPICard
          icon={Plane}
          label="Total Drones"
          value={12}
          trend="+8%"
          trendDirection="up"
          subtitle="vs. last month"
          color="blue"
        />
        <KPICard
          icon={Activity}
          label="Active Flights"
          value={3}
          trend="+15%"
          trendDirection="up"
          subtitle="currently airborne"
          color="green"
        />
        <KPICard
          icon={HeartPulse}
          label="Fleet Health"
          value="94.2%"
          trend="-1.2%"
          trendDirection="down"
          subtitle="avg. health score"
          color="purple"
        />
        <KPICard
          icon={AlertTriangle}
          label="Alerts"
          value={7}
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
          <div className="dashboard__alert-list">
            {RECENT_ALERTS.map((alert) => (
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
        </section>

        {/* Active Flights */}
        <section className="dashboard__flights-panel">
          <h3 className="dashboard__panel-title">Active Flights</h3>
          <DataTable columns={FLIGHT_COLUMNS} data={ACTIVE_FLIGHTS} />
        </section>
      </div>
    </div>
  );
}
