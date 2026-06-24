/**
 * @file Fleet.jsx
 * @description Fleet management page showing a data table of all drones
 * with status badges, health bars, and an "Add Drone" action button.
 */

import { Plus } from 'lucide-react';
import DataTable from '../components/common/DataTable';
import StatusBadge from '../components/common/StatusBadge';
import './Fleet.css';

/** Mock fleet data */
const MOCK_DRONES = [
  { id: 'd1', name: 'Eagle-1', serial: 'UAV-2024-001', type: 'Quadcopter', status: 'Active', flightHours: 342, health: 96, lastMaint: '2026-06-01' },
  { id: 'd2', name: 'Hawk-3', serial: 'UAV-2024-003', type: 'Hexacopter', status: 'Active', flightHours: 518, health: 91, lastMaint: '2026-05-22' },
  { id: 'd3', name: 'Falcon-7', serial: 'UAV-2024-007', type: 'Quadcopter', status: 'Warning', flightHours: 276, health: 74, lastMaint: '2026-04-15' },
  { id: 'd4', name: 'Osprey-2', serial: 'UAV-2024-002', type: 'Fixed-Wing', status: 'Maintenance', flightHours: 890, health: 62, lastMaint: '2026-06-10' },
  { id: 'd5', name: 'Condor-9', serial: 'UAV-2024-009', type: 'VTOL', status: 'Offline', flightHours: 45, health: 100, lastMaint: '2026-06-15' },
];

/**
 * HealthBar — Inline progress bar for health %.
 * @param {{ value: number }} props
 */
function HealthBar({ value }) {
  const color =
    value >= 85
      ? 'var(--color-success)'
      : value >= 60
        ? 'var(--color-warning)'
        : 'var(--color-danger)';

  return (
    <span style={{ display: 'inline-flex', alignItems: 'center', gap: 8 }}>
      <span className="fleet__health-bar">
        <span
          className="fleet__health-fill"
          style={{ width: `${value}%`, background: color }}
        />
      </span>
      <span style={{ fontFamily: 'var(--font-mono)', fontSize: 'var(--text-xs)' }}>
        {value}%
      </span>
    </span>
  );
}

/** Column definitions */
const COLUMNS = [
  { key: 'name', label: 'Name' },
  { key: 'serial', label: 'Serial' },
  { key: 'type', label: 'Type' },
  {
    key: 'status',
    label: 'Status',
    render: (val) => <StatusBadge status={val} />,
  },
  {
    key: 'flightHours',
    label: 'Flight Hours',
    render: (val) => <span style={{ fontFamily: 'var(--font-mono)' }}>{val}h</span>,
  },
  {
    key: 'health',
    label: 'Health',
    render: (val) => <HealthBar value={val} />,
  },
  { key: 'lastMaint', label: 'Last Maintenance' },
];

/**
 * Fleet — Drone fleet management page.
 *
 * @returns {JSX.Element}
 */
export default function Fleet() {
  return (
    <div className="page-enter">
      <div className="fleet__header">
        <h2 className="fleet__title">Fleet Overview</h2>
        <button className="btn btn-primary">
          <Plus size={16} />
          Add Drone
        </button>
      </div>

      <DataTable columns={COLUMNS} data={MOCK_DRONES} />
    </div>
  );
}
