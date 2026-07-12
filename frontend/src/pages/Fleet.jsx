import React, { useState, useEffect } from 'react';
import { Plus, AlertTriangle } from 'lucide-react';
import DataTable from '../components/common/DataTable';
import StatusBadge from '../components/common/StatusBadge';
import LoadingSpinner from '../components/common/LoadingSpinner';
import { listDrones, getDroneHealth } from '../api/endpoints';
import './Fleet.css';

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
  const [dronesList, setDronesList] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadFleetData = async () => {
    setLoading(true);
    setError(null);
    try {
      const { data: dronesData } = await listDrones();
      
      // Fetch health details in parallel for all drones
      const dronesWithHealth = await Promise.all(
        dronesData.map(async (drone) => {
          try {
            const healthRes = await getDroneHealth(drone.id);
            const components = healthRes.data.components || [];
            const avgHealth = components.length > 0
              ? Math.round(components.reduce((sum, c) => sum + c.health_score, 0) / components.length)
              : 100;
            return {
              id: drone.id,
              name: drone.name,
              serial: drone.serial_number,
              type: drone.type_display || drone.drone_type,
              status: drone.status_display || (drone.status.charAt(0).toUpperCase() + drone.status.slice(1)),
              flightHours: Math.round(drone.total_flight_hours),
              health: avgHealth,
              lastMaint: drone.last_maintenance_date ? drone.last_maintenance_date.split('T')[0] : 'N/A',
            };
          } catch (err) {
            console.warn(`Failed to fetch health for drone ${drone.id}:`, err);
            return {
              id: drone.id,
              name: drone.name,
              serial: drone.serial_number,
              type: drone.type_display || drone.drone_type,
              status: drone.status_display || (drone.status.charAt(0).toUpperCase() + drone.status.slice(1)),
              flightHours: Math.round(drone.total_flight_hours),
              health: 95, // default fallback
              lastMaint: drone.last_maintenance_date ? drone.last_maintenance_date.split('T')[0] : 'N/A',
            };
          }
        })
      );
      setDronesList(dronesWithHealth);
    } catch (err) {
      console.error('Failed to load fleet:', err);
      setError(err.message || 'Failed to fetch fleet overview.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadFleetData();
  }, []);

  if (loading) {
    return (
      <div className="page-loading" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: '400px', gap: 'var(--space-4)' }}>
        <LoadingSpinner size={40} />
        <span style={{ color: 'var(--color-text-secondary)', fontSize: 'var(--text-base)' }}>Loading fleet list and component status...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="page-error card" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: '350px', gap: 'var(--space-4)', padding: 'var(--space-8)', textAlign: 'center', border: '1px solid var(--color-danger-border)', background: 'var(--color-danger-bg)' }}>
        <AlertTriangle size={48} style={{ color: 'var(--color-danger)' }} />
        <h3 style={{ color: 'var(--color-text-primary)' }}>Failed to Load Fleet</h3>
        <p style={{ color: 'var(--color-text-secondary)', maxWidth: '450px' }}>{error}</p>
        <button className="btn btn-primary" onClick={loadFleetData} style={{ marginTop: 'var(--space-2)' }}>Retry Connection</button>
      </div>
    );
  }

  return (
    <div className="page-enter">
      <div className="fleet__header">
        <h2 className="fleet__title">Fleet Overview</h2>
        <button className="btn btn-primary">
          <Plus size={16} />
          Add Drone
        </button>
      </div>

      {dronesList.length === 0 ? (
        <div className="page-empty card" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: '250px', gap: 'var(--space-2)', padding: 'var(--space-8)', textAlign: 'center' }}>
          <span style={{ fontSize: '36px' }}>🛸</span>
          <h3 style={{ color: 'var(--color-text-primary)', marginTop: 'var(--space-2)' }}>No Drones Found</h3>
          <p style={{ color: 'var(--color-text-secondary)', maxWidth: '400px' }}>There are currently no drone assets registered in your fleet database.</p>
        </div>
      ) : (
        <DataTable columns={COLUMNS} data={dronesList} />
      )}
    </div>
  );
}
