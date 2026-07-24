import React, { useState, useEffect } from 'react';
import DataTable from '../components/common/DataTable';
import StatusBadge from '../components/common/StatusBadge';
import LoadingSpinner from '../components/common/LoadingSpinner';
import { AlertTriangle } from 'lucide-react';
import { listFlights } from '../api/endpoints';
import './Flights.css';

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

/** Helper to format seconds into readable h/min duration */
const formatDuration = (seconds) => {
  if (!seconds) return '0 min';
  const totalMins = Math.round(seconds / 60);
  if (totalMins < 60) return `${totalMins} min`;
  const hrs = Math.floor(totalMins / 60);
  const mins = totalMins % 60;
  return mins > 0 ? `${hrs}h ${mins}min` : `${hrs}h`;
};

/**
 * Flights — Flight history page.
 *
 * @returns {JSX.Element}
 */
export default function Flights() {
  const [flightsList, setFlightsList] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadFlightsData = async () => {
    setLoading(true);
    setError(null);
    try {
      const { data } = await listFlights();
      const flightItems = Array.isArray(data)
        ? data
        : data?.results || [];

      const mappedFlights = flightItems.map((flight) => {
        const dateStr = flight.start_time || flight.created_at || '';
        return {
          id: flight.flight_number,
          drone: flight.drone_name || `Drone ${flight.drone}`,
          date: dateStr ? dateStr.split('T')[0] : 'N/A',
          duration: formatDuration(flight.duration_seconds),
          distance: flight.distance_km ? `${flight.distance_km.toFixed(1)} km` : '0.0 km',
          maxAlt: flight.max_altitude_m ? `${Math.round(flight.max_altitude_m)}m` : '0m',
          batteryUsed: `${Math.round(flight.start_battery_pct - flight.end_battery_pct)}%`,
          status: flight.status === 'in_progress' ? 'Active' : (flight.status_display || (flight.status.charAt(0).toUpperCase() + flight.status.slice(1))),
          risk: Math.round(flight.risk_score || 0),
        };
      });
      setFlightsList(mappedFlights);
    } catch (err) {
      console.error('Failed to load flights:', err);
      setError(err.message || 'Failed to fetch flight records.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadFlightsData();
  }, []);

  if (loading) {
    return (
      <div className="page-loading" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: '400px', gap: 'var(--space-4)' }}>
        <LoadingSpinner size={40} />
        <span style={{ color: 'var(--color-text-secondary)', fontSize: 'var(--text-base)' }}>Loading flight logs database...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="page-error card" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: '350px', gap: 'var(--space-4)', padding: 'var(--space-8)', textAlign: 'center', border: '1px solid var(--color-danger-border)', background: 'var(--color-danger-bg)' }}>
        <AlertTriangle size={48} style={{ color: 'var(--color-danger)' }} />
        <h3 style={{ color: 'var(--color-text-primary)' }}>Failed to Load Flight Logs</h3>
        <p style={{ color: 'var(--color-text-secondary)', maxWidth: '450px' }}>{error}</p>
        <button className="btn btn-primary" onClick={loadFlightsData} style={{ marginTop: 'var(--space-2)' }}>Retry Connection</button>
      </div>
    );
  }

  return (
    <div className="page-enter">
      <div className="flights__header">
        <h2 className="flights__title">Flight History</h2>
      </div>

      {flightsList.length === 0 ? (
        <div className="page-empty card" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: '250px', gap: 'var(--space-2)', padding: 'var(--space-8)', textAlign: 'center' }}>
          <span style={{ fontSize: '36px' }}>🗺️</span>
          <h3 style={{ color: 'var(--color-text-primary)', marginTop: 'var(--space-2)' }}>No Flights Logged</h3>
          <p style={{ color: 'var(--color-text-secondary)', maxWidth: '400px' }}>No flight sorties have been registered yet.</p>
        </div>
      ) : (
        <DataTable columns={COLUMNS} data={flightsList} />
      )}
    </div>
  );
}
