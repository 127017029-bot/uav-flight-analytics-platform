/**
 * @file Flights.jsx
 * @description Flight history page displaying a table of completed and
 * in-progress flights with metrics like duration, distance, and risk score.
 */

import DataTable from '../components/common/DataTable';
import StatusBadge from '../components/common/StatusBadge';
import './Flights.css';

/** Mock flight records */
const MOCK_FLIGHTS = [
  { id: 'FL-001', drone: 'Eagle-1', date: '2026-06-17', duration: '48 min', distance: '12.4 km', maxAlt: '150m', batteryUsed: '34%', status: 'Completed', risk: 12 },
  { id: 'FL-002', drone: 'Hawk-3', date: '2026-06-17', duration: '1h 12min', distance: '28.7 km', maxAlt: '220m', batteryUsed: '61%', status: 'Completed', risk: 28 },
  { id: 'FL-003', drone: 'Falcon-7', date: '2026-06-16', duration: '35 min', distance: '8.1 km', maxAlt: '95m', batteryUsed: '22%', status: 'Completed', risk: 8 },
  { id: 'FL-004', drone: 'Eagle-1', date: '2026-06-16', duration: '55 min', distance: '15.2 km', maxAlt: '180m', batteryUsed: '45%', status: 'Completed', risk: 45 },
  { id: 'FL-005', drone: 'Osprey-2', date: '2026-06-15', duration: '2h 5min', distance: '67.3 km', maxAlt: '310m', batteryUsed: '82%', status: 'Warning', risk: 72 },
];

/**
 * RiskScore — Coloured risk score badge.
 * @param {{ value: number }} props
 */
function RiskScore({ value }) {
  const level = value >= 60 ? 'high' : value >= 30 ? 'medium' : 'low';
  return <span className={`flights__risk flights__risk--${level}`}>{value}</span>;
}

/** Column definitions */
const COLUMNS = [
  { key: 'id', label: 'Flight #' },
  { key: 'drone', label: 'Drone' },
  { key: 'date', label: 'Date' },
  { key: 'duration', label: 'Duration' },
  { key: 'distance', label: 'Distance' },
  { key: 'maxAlt', label: 'Max Alt' },
  { key: 'batteryUsed', label: 'Battery Used' },
  {
    key: 'status',
    label: 'Status',
    render: (val) => <StatusBadge status={val} size="sm" />,
  },
  {
    key: 'risk',
    label: 'Risk Score',
    render: (val) => <RiskScore value={val} />,
  },
];

/**
 * Flights — Flight history page.
 *
 * @returns {JSX.Element}
 */
export default function Flights() {
  return (
    <div className="page-enter">
      <div className="flights__header">
        <h2 className="flights__title">Flight History</h2>
      </div>
      <DataTable columns={COLUMNS} data={MOCK_FLIGHTS} />
    </div>
  );
}
