import React, { useState } from 'react';
import GaugeWidget from '../components/common/GaugeWidget';
import './LiveTelemetry.css';

/**
 * LiveTelemetry - Real-time drone telemetry monitoring page.
 * Displays live gauges, flight data, and streaming status.
 */
const LiveTelemetry = () => {
  const [selectedDrone, setSelectedDrone] = useState('1');
  const [isStreaming] = useState(false);

  const mockDrones = [
    { id: '1', name: 'Eagle-1' },
    { id: '2', name: 'Falcon-2' },
    { id: '3', name: 'Hawk-3' },
    { id: '4', name: 'Osprey-4' },
    { id: '5', name: 'Phoenix-5' },
  ];

  const mockTelemetry = {
    altitude: 47.3,
    speed: 12.8,
    battery: 73,
    signal: 92,
    heading: 247,
    roll: -2.3,
    pitch: 5.1,
    latitude: 10.7912,
    longitude: 78.7053,
    motor_rpm: [5230, 5180, 5290, 5210],
    motor_temp: [42.1, 43.5, 41.8, 44.2],
    vibration: { x: 0.32, y: 0.28, z: 0.41 },
    gps_satellites: 12,
    wind_speed: 3.2,
  };

  return (
    <div className="live-telemetry-page">
      <div className="telemetry-header">
        <div className="header-left">
          <h1>Live Telemetry</h1>
          <div className={`stream-status ${isStreaming ? 'streaming' : 'disconnected'}`}>
            <span className="status-dot"></span>
            {isStreaming ? 'Streaming' : 'Disconnected'}
          </div>
        </div>
        <div className="header-controls">
          <select
            className="drone-select"
            value={selectedDrone}
            onChange={(e) => setSelectedDrone(e.target.value)}
          >
            {mockDrones.map(d => (
              <option key={d.id} value={d.id}>{d.name}</option>
            ))}
          </select>
          <button className="btn-stream">
            {isStreaming ? 'Disconnect' : 'Connect'}
          </button>
        </div>
      </div>

      <div className="telemetry-grid">
        {/* Left: Gauges */}
        <div className="gauge-panel">
          <h3>Flight Instruments</h3>
          <div className="gauges-grid">
            <GaugeWidget value={mockTelemetry.altitude} max={150} label="Altitude" unit="m" color="var(--color-accent)" />
            <GaugeWidget value={mockTelemetry.speed} max={25} label="Speed" unit="m/s" color="var(--color-accent-3)" />
            <GaugeWidget value={mockTelemetry.battery} max={100} label="Battery" unit="%" color={mockTelemetry.battery > 50 ? 'var(--color-success)' : 'var(--color-warning)'} />
            <GaugeWidget value={mockTelemetry.signal} max={100} label="Signal" unit="%" color="var(--color-accent-2)" />
          </div>

          <h3 style={{ marginTop: 'var(--space-6)' }}>Attitude</h3>
          <div className="attitude-data">
            <div className="attitude-item">
              <span className="att-label">Heading</span>
              <span className="att-value">{mockTelemetry.heading}°</span>
            </div>
            <div className="attitude-item">
              <span className="att-label">Roll</span>
              <span className="att-value">{mockTelemetry.roll}°</span>
            </div>
            <div className="attitude-item">
              <span className="att-label">Pitch</span>
              <span className="att-value">{mockTelemetry.pitch}°</span>
            </div>
          </div>

          <h3 style={{ marginTop: 'var(--space-6)' }}>Motors</h3>
          <div className="motor-grid">
            {mockTelemetry.motor_rpm.map((rpm, i) => (
              <div key={i} className="motor-item">
                <span className="motor-label">M{i + 1}</span>
                <span className="motor-rpm">{rpm} RPM</span>
                <span className="motor-temp">{mockTelemetry.motor_temp[i]}°C</span>
              </div>
            ))}
          </div>
        </div>

        {/* Right: Chart Area */}
        <div className="chart-panel">
          <h3>Telemetry Charts</h3>
          <div className="chart-placeholder">
            <div className="placeholder-icon">📡</div>
            <p>Connect to a drone to view live telemetry data</p>
            <span className="placeholder-sub">Real-time altitude, speed, and battery charts will appear here</span>
          </div>

          <div className="position-info card">
            <h4>Position</h4>
            <div className="pos-grid">
              <div className="pos-item">
                <span className="pos-label">Latitude</span>
                <span className="pos-value">{mockTelemetry.latitude.toFixed(6)}°</span>
              </div>
              <div className="pos-item">
                <span className="pos-label">Longitude</span>
                <span className="pos-value">{mockTelemetry.longitude.toFixed(6)}°</span>
              </div>
              <div className="pos-item">
                <span className="pos-label">GPS Sats</span>
                <span className="pos-value">{mockTelemetry.gps_satellites}</span>
              </div>
              <div className="pos-item">
                <span className="pos-label">Wind</span>
                <span className="pos-value">{mockTelemetry.wind_speed} m/s</span>
              </div>
            </div>
          </div>

          <div className="vibration-info card">
            <h4>Vibration (g)</h4>
            <div className="vib-grid">
              <div className="vib-item">
                <span className="vib-axis">X</span>
                <div className="vib-bar" style={{ width: `${Math.abs(mockTelemetry.vibration.x) * 100}%` }}></div>
                <span>{mockTelemetry.vibration.x}</span>
              </div>
              <div className="vib-item">
                <span className="vib-axis">Y</span>
                <div className="vib-bar" style={{ width: `${Math.abs(mockTelemetry.vibration.y) * 100}%` }}></div>
                <span>{mockTelemetry.vibration.y}</span>
              </div>
              <div className="vib-item">
                <span className="vib-axis">Z</span>
                <div className="vib-bar" style={{ width: `${Math.abs(mockTelemetry.vibration.z) * 100}%` }}></div>
                <span>{mockTelemetry.vibration.z}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LiveTelemetry;
