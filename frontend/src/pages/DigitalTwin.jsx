import React, { useState, useEffect } from 'react';
import useTelemetryStore from '../stores/useTelemetryStore';
import useFleetStore from '../stores/useFleetStore';
import { connectWebSocket, disconnectWebSocket } from '../api/websocket';
import { predictMaintenance } from '../api/endpoints';
import DroneScene from '../components/digital-twin/DroneScene';
import './DigitalTwin.css';

/**
 * DigitalTwin - 3D quadcopter rendering page with real-time attitude sync.
 */
const DigitalTwin = () => {
  const { drones, fetchDrones } = useFleetStore();
  const [selectedDroneId, setSelectedDroneId] = useState('');
  const { latestTelemetry, isStreaming, wsStatus } = useTelemetryStore();
  const [healthIndex, setHealthIndex] = useState({
    motor_1: 95, motor_2: 92, motor_3: 94, motor_4: 91,
    battery: 98, gps: 99, imu: 97, overall: 96.0
  });

  useEffect(() => {
    fetchDrones();
    return () => {
      disconnectWebSocket();
    };
  }, [fetchDrones]);

  useEffect(() => {
    if (drones && drones.length > 0 && !selectedDroneId) {
      setSelectedDroneId(drones[0].id.toString());
    }
  }, [drones, selectedDroneId]);

  // Fetch component maintenance scores when drone is selected or streaming starts
  useEffect(() => {
    if (selectedDroneId) {
      fetchMaintenanceHealth(selectedDroneId);
    }
  }, [selectedDroneId, isStreaming]);

  const fetchMaintenanceHealth = async (droneId) => {
    try {
      const { data } = await predictMaintenance(droneId);
      if (data && data.components) {
        const healths = {};
        data.components.forEach(c => {
          // map classification to a visual health score
          const scoreMap = { low: 95, medium: 78, high: 62, critical: 42 };
          healths[c.component] = scoreMap[c.urgency] || 95;
        });
        healths['overall'] = data.overall_health_score;
        setHealthIndex(healths);
      }
    } catch (err) {
      console.warn('Failed to load predictive maintenance scores, using defaults:', err);
    }
  };

  const handleConnectToggle = () => {
    if (isStreaming) {
      disconnectWebSocket();
    } else if (selectedDroneId) {
      connectWebSocket(selectedDroneId);
    }
  };

  // Get active telemetry for selected drone, fallback to defaults
  const telemetry = latestTelemetry[selectedDroneId] || {
    altitude_msl: 0.0,
    ground_speed: 0.0,
    battery_percentage: 100,
    signal_strength: 0,
    heading: 0,
    roll: 0.0,
    pitch: 0.0,
    motor_rpm_1: 0,
    motor_rpm_2: 0,
    motor_rpm_3: 0,
    motor_rpm_4: 0,
    flight_time: 0,
  };

  const formatFlightTime = (seconds) => {
    const min = Math.floor(seconds / 60);
    const sec = Math.floor(seconds % 60);
    return `${min.toString().padStart(2, '0')}:${sec.toString().padStart(2, '0')}`;
  };

  return (
    <div className="digital-twin-page">
      <div className="page-header">
        <div>
          <h1>Digital Twin</h1>
          <p className="page-subtitle">3D real-time drone visualization and telemetry overlay</p>
        </div>
        <div className="twin-controls">
          <select
            className="drone-select"
            value={selectedDroneId}
            onChange={(e) => {
              setSelectedDroneId(e.target.value);
              if (isStreaming) {
                disconnectWebSocket();
                connectWebSocket(e.target.value);
              }
            }}
          >
            {drones && drones.length > 0 ? (
              drones.map(d => (
                <option key={d.id} value={d.id.toString()}>{d.name} ({d.model})</option>
              ))
            ) : (
              <option value="">No drones found</option>
            )}
          </select>
          <button className="btn-primary" onClick={handleConnectToggle}>
            {isStreaming ? 'Disconnect Stream' : 'Connect WebSocket'}
          </button>
        </div>
      </div>

      <div className="twin-layout">
        {/* WebGL Viewport */}
        <div className="twin-viewport card" style={{ padding: 0, overflow: 'hidden' }}>
          <DroneScene
            roll={telemetry.roll}
            pitch={telemetry.pitch}
            heading={telemetry.heading}
            rpms={[telemetry.motor_rpm_1, telemetry.motor_rpm_2, telemetry.motor_rpm_3, telemetry.motor_rpm_4]}
            healths={{
              motor_1: healthIndex.motor_1,
              motor_2: healthIndex.motor_2,
              motor_3: healthIndex.motor_3,
              motor_4: healthIndex.motor_4,
              battery: healthIndex.battery
            }}
          />
          <div className="scene-label">
            <span>WebGL 3D digital twin viewport</span>
            <span className="scene-hint" style={{ color: isStreaming ? 'var(--color-success)' : 'var(--color-text-muted)' }}>
              {isStreaming ? `Streaming active (${wsStatus.toUpperCase()})` : 'WebSocket disconnected'}
            </span>
          </div>
        </div>

        <div className="twin-sidebar">
          {/* Dynamic Telemetry Stats */}
          <div className="twin-info card">
            <h3>Drone State</h3>
            <div className="twin-data-list">
              {[
                { label: 'Status', value: isStreaming ? 'In Flight' : 'Offline', color: isStreaming ? 'var(--color-success)' : 'var(--color-text-muted)' },
                { label: 'Altitude AGL', value: `${(telemetry.altitude_agl || telemetry.altitude_msl).toFixed(1)} m` },
                { label: 'Speed', value: `${telemetry.ground_speed.toFixed(1)} m/s` },
                { label: 'Heading', value: `${Math.round(telemetry.heading)}°` },
                { label: 'Roll', value: `${telemetry.roll.toFixed(1)}°` },
                { label: 'Pitch', value: `${telemetry.pitch.toFixed(1)}°` },
                { label: 'Battery Capacity', value: `${Math.round(telemetry.battery_percentage)}%`, color: telemetry.battery_percentage > 50 ? 'var(--color-success)' : 'var(--color-warning)' },
                { label: 'Operational Duration', value: formatFlightTime(telemetry.flight_time || 0) },
              ].map((d, i) => (
                <div key={i} className="twin-data-row">
                  <span className="twin-data-label">{d.label}</span>
                  <span className="twin-data-value" style={d.color ? { color: d.color } : {}}>{d.value}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Component healths from RF maintenance classifier */}
          <div className="twin-info card">
            <h3>Predicted Component Health</h3>
            <div className="component-bars">
              {[
                { name: 'Motor 1', health: healthIndex.motor_1 || 95 },
                { name: 'Motor 2', health: healthIndex.motor_2 || 92 },
                { name: 'Motor 3', health: healthIndex.motor_3 || 94 },
                { name: 'Motor 4', health: healthIndex.motor_4 || 91 },
                { name: 'LiPo Battery', health: healthIndex.battery || 98 },
                { name: 'GPS Module', health: healthIndex.gps || 99 },
                { name: 'IMU / Gyro', health: healthIndex.imu || 97 },
              ].map((c, i) => (
                <div key={i} className="comp-bar-item">
                  <div className="comp-bar-header">
                    <span>{c.name}</span>
                    <span className="comp-health-val">{c.health}%</span>
                  </div>
                  <div className="comp-bar-track">
                    <div
                      className="comp-bar-fill"
                      style={{
                        width: `${c.health}%`,
                        background: c.health > 80 ? 'var(--color-success)' : c.health > 50 ? 'var(--color-warning)' : 'var(--color-danger)',
                      }}
                    ></div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DigitalTwin;
