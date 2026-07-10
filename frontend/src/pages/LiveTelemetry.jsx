import React, { useState, useEffect } from 'react';
import useTelemetryStore from '../stores/useTelemetryStore';
import useFleetStore from '../stores/useFleetStore';
import { connectWebSocket, disconnectWebSocket } from '../api/websocket';
import GaugeWidget from '../components/common/GaugeWidget';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
} from 'recharts';
import './LiveTelemetry.css';

/**
 * LiveTelemetry - Real-time drone telemetry monitoring page.
 * Displays live gauges, flight data, and streaming status over WebSockets.
 */
const LiveTelemetry = () => {
  const { drones, fetchDrones } = useFleetStore();
  const [selectedDroneId, setSelectedDroneId] = useState('');
  const { latestTelemetry, chartData, isStreaming, wsStatus } = useTelemetryStore();

  useEffect(() => {
    fetchDrones();
    return () => {
      disconnectWebSocket();
    };
  }, [fetchDrones]);

  // Set the default selected drone when the list loads
  useEffect(() => {
    if (drones && drones.length > 0 && !selectedDroneId) {
      setSelectedDroneId(drones[0].id.toString());
    }
  }, [drones, selectedDroneId]);

  const handleConnectToggle = () => {
    if (isStreaming) {
      disconnectWebSocket();
    } else if (selectedDroneId) {
      connectWebSocket(selectedDroneId);
    }
  };

  // Get active telemetry for selected drone, fallback to defaults if none
  const telemetry = latestTelemetry[selectedDroneId] || {
    altitude_msl: 0.0,
    ground_speed: 0.0,
    battery_percentage: 0.0,
    signal_strength: 0,
    heading: 0,
    roll: 0.0,
    pitch: 0.0,
    latitude: 10.7905,
    longitude: 78.7047,
    motor_rpm_1: 0,
    motor_rpm_2: 0,
    motor_rpm_3: 0,
    motor_rpm_4: 0,
    motor_temp_1: 25.0,
    motor_temp_2: 25.0,
    motor_temp_3: 25.0,
    motor_temp_4: 25.0,
    vibration_x: 0.0,
    vibration_y: 0.0,
    vibration_z: 0.0,
    gps_satellites: 0,
    wind_speed_est: 0.0,
  };

  // Format real-time chart data from the store
  const altitudePoints = chartData['altitude'] || [];
  const speedPoints = chartData['speed'] || [];
  const batteryPoints = chartData['battery'] || [];

  const combinedData = altitudePoints.map((pt, index) => {
    const timeStr = pt.timestamp
      ? new Date(pt.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })
      : '';
    return {
      time: timeStr,
      altitude: pt.value,
      speed: speedPoints[index]?.value || 0,
      battery: batteryPoints[index]?.value || 0,
    };
  });

  return (
    <div className="live-telemetry-page">
      <div className="telemetry-header">
        <div className="header-left">
          <h1>Live Telemetry</h1>
          <div className={`stream-status ${isStreaming ? 'streaming' : 'disconnected'}`}>
            <span className="status-dot"></span>
            {isStreaming
              ? `Streaming (WS ${wsStatus.toUpperCase()})`
              : wsStatus === 'connecting'
              ? 'Connecting...'
              : 'Disconnected'}
          </div>
        </div>
        <div className="header-controls">
          <select
            className="drone-select"
            value={selectedDroneId}
            onChange={(e) => {
              setSelectedDroneId(e.target.value);
              if (isStreaming) {
                // Switch drone connection dynamically
                disconnectWebSocket();
                connectWebSocket(e.target.value);
              }
            }}
          >
            {drones && drones.length > 0 ? (
              drones.map((d) => (
                <option key={d.id} value={d.id.toString()}>
                  {d.name} ({d.model})
                </option>
              ))
            ) : (
              <option value="">No drones found</option>
            )}
          </select>
          <button className="btn-stream" onClick={handleConnectToggle} disabled={!selectedDroneId}>
            {isStreaming ? 'Disconnect' : 'Connect'}
          </button>
        </div>
      </div>

      <div className="telemetry-grid">
        {/* Left: Gauges */}
        <div className="gauge-panel">
          <h3>Flight Instruments</h3>
          <div className="gauges-grid">
            <GaugeWidget value={telemetry.altitude_msl} max={150} label="Altitude" unit="m" color="var(--color-accent)" />
            <GaugeWidget value={telemetry.ground_speed} max={25} label="Speed" unit="m/s" color="var(--color-accent-3)" />
            <GaugeWidget value={telemetry.battery_percentage} max={100} label="Battery" unit="%" color={telemetry.battery_percentage > 50 ? 'var(--color-success)' : 'var(--color-warning)'} />
            <GaugeWidget value={telemetry.signal_strength} max={100} label="Signal" unit="%" color="var(--color-accent-2)" />
          </div>

          <h3 style={{ marginTop: 'var(--space-6)' }}>Attitude</h3>
          <div className="attitude-data">
            <div className="attitude-item">
              <span className="att-label">Heading</span>
              <span className="att-value">{Math.round(telemetry.heading)}°</span>
            </div>
            <div className="attitude-item">
              <span className="att-label">Roll</span>
              <span className="att-value">{telemetry.roll ? telemetry.roll.toFixed(1) : 0}°</span>
            </div>
            <div className="attitude-item">
              <span className="att-label">Pitch</span>
              <span className="att-value">{telemetry.pitch ? telemetry.pitch.toFixed(1) : 0}°</span>
            </div>
          </div>

          <h3 style={{ marginTop: 'var(--space-6)' }}>Motors</h3>
          <div className="motor-grid">
            {[
              { rpm: telemetry.motor_rpm_1, temp: telemetry.motor_temp_1 },
              { rpm: telemetry.motor_rpm_2, temp: telemetry.motor_temp_2 },
              { rpm: telemetry.motor_rpm_3, temp: telemetry.motor_temp_3 },
              { rpm: telemetry.motor_rpm_4, temp: telemetry.motor_temp_4 },
            ].map((m, i) => (
              <div key={i} className="motor-item">
                <span className="motor-label">M{i + 1}</span>
                <span className="motor-rpm">{m.rpm ? Math.round(m.rpm) : 0} RPM</span>
                <span className="motor-temp">{m.temp ? m.temp.toFixed(1) : 25.0}°C</span>
              </div>
            ))}
          </div>
        </div>

        {/* Right: Chart Area */}
        <div className="chart-panel">
          <h3>Telemetry Charts</h3>
          {!isStreaming && combinedData.length === 0 ? (
            <div className="chart-placeholder">
              <div className="placeholder-icon">📡</div>
              <p>Connect to a drone to view live telemetry data</p>
              <span className="placeholder-sub">Real-time altitude, speed, and battery charts will appear here</span>
            </div>
          ) : (
            <div className="live-charts-container">
              <div className="chart-wrapper">
                <h4>Altitude (m)</h4>
                <ResponsiveContainer width="100%" height={150}>
                  <LineChart data={combinedData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#2a2f3a" />
                    <XAxis dataKey="time" stroke="#8e9bb0" fontSize={10} />
                    <YAxis stroke="#8e9bb0" fontSize={10} />
                    <Tooltip contentStyle={{ backgroundColor: '#1a1f2c', borderColor: '#2e374a', color: '#fff' }} />
                    <Line type="monotone" dataKey="altitude" stroke="var(--color-accent)" strokeWidth={2} dot={false} isAnimationActive={false} />
                  </LineChart>
                </ResponsiveContainer>
              </div>

              <div className="chart-wrapper">
                <h4>Speed (m/s)</h4>
                <ResponsiveContainer width="100%" height={150}>
                  <LineChart data={combinedData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#2a2f3a" />
                    <XAxis dataKey="time" stroke="#8e9bb0" fontSize={10} />
                    <YAxis stroke="#8e9bb0" fontSize={10} />
                    <Tooltip contentStyle={{ backgroundColor: '#1a1f2c', borderColor: '#2e374a', color: '#fff' }} />
                    <Line type="monotone" dataKey="speed" stroke="var(--color-accent-3)" strokeWidth={2} dot={false} isAnimationActive={false} />
                  </LineChart>
                </ResponsiveContainer>
              </div>

              <div className="chart-wrapper">
                <h4>Battery (%)</h4>
                <ResponsiveContainer width="100%" height={150}>
                  <LineChart data={combinedData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#2a2f3a" />
                    <XAxis dataKey="time" stroke="#8e9bb0" fontSize={10} />
                    <YAxis stroke="#8e9bb0" fontSize={10} domain={[0, 100]} />
                    <Tooltip contentStyle={{ backgroundColor: '#1a1f2c', borderColor: '#2e374a', color: '#fff' }} />
                    <Line type="monotone" dataKey="battery" stroke="var(--color-success)" strokeWidth={2} dot={false} isAnimationActive={false} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>
          )}

          <div className="position-info card">
            <h4>Position</h4>
            <div className="pos-grid">
              <div className="pos-item">
                <span className="pos-label">Latitude</span>
                <span className="pos-value">{telemetry.latitude ? telemetry.latitude.toFixed(6) : '0.000000'}°</span>
              </div>
              <div className="pos-item">
                <span className="pos-label">Longitude</span>
                <span className="pos-value">{telemetry.longitude ? telemetry.longitude.toFixed(6) : '0.000000'}°</span>
              </div>
              <div className="pos-item">
                <span className="pos-label">GPS Sats</span>
                <span className="pos-value">{telemetry.gps_satellites || 0}</span>
              </div>
              <div className="pos-item">
                <span className="pos-label">Wind</span>
                <span className="pos-value">{telemetry.wind_speed_est ? telemetry.wind_speed_est.toFixed(1) : '0.0'} m/s</span>
              </div>
            </div>
          </div>

          <div className="vibration-info card">
            <h4>Vibration (g)</h4>
            <div className="vib-grid">
              <div className="vib-item">
                <span className="vib-axis">X</span>
                <div className="vib-bar" style={{ width: `${Math.min(100, Math.abs(telemetry.vibration_x || 0) * 100)}%` }}></div>
                <span>{telemetry.vibration_x ? telemetry.vibration_x.toFixed(2) : '0.00'}</span>
              </div>
              <div className="vib-item">
                <span className="vib-axis">Y</span>
                <div className="vib-bar" style={{ width: `${Math.min(100, Math.abs(telemetry.vibration_y || 0) * 100)}%` }}></div>
                <span>{telemetry.vibration_y ? telemetry.vibration_y.toFixed(2) : '0.00'}</span>
              </div>
              <div className="vib-item">
                <span className="vib-axis">Z</span>
                <div className="vib-bar" style={{ width: `${Math.min(100, Math.abs(telemetry.vibration_z || 0) * 100)}%` }}></div>
                <span>{telemetry.vibration_z ? telemetry.vibration_z.toFixed(2) : '0.00'}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LiveTelemetry;
