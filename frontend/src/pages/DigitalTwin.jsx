import React from 'react';
import './DigitalTwin.css';

/** DigitalTwin - 3D drone visualization placeholder with animated CSS drone. */
const DigitalTwin = () => {
  return (
    <div className="digital-twin-page">
      <div className="page-header">
        <div>
          <h1>Digital Twin</h1>
          <p className="page-subtitle">3D real-time drone visualization and telemetry overlay</p>
        </div>
        <div className="twin-controls">
          <select className="drone-select">
            <option>Eagle-1</option>
            <option>Falcon-2</option>
            <option>Hawk-3</option>
          </select>
          <button className="btn-secondary">Reset View</button>
        </div>
      </div>

      <div className="twin-layout">
        <div className="twin-viewport card">
          <div className="drone-scene">
            <div className="grid-floor"></div>
            <div className="drone-3d">
              <div className="drone-body">
                <div className="drone-arm arm-fl">
                  <div className="prop-mount"><div className="propeller"></div></div>
                </div>
                <div className="drone-arm arm-fr">
                  <div className="prop-mount"><div className="propeller"></div></div>
                </div>
                <div className="drone-arm arm-bl">
                  <div className="prop-mount"><div className="propeller"></div></div>
                </div>
                <div className="drone-arm arm-br">
                  <div className="prop-mount"><div className="propeller"></div></div>
                </div>
                <div className="center-hub">
                  <div className="led-indicator"></div>
                </div>
              </div>
              <div className="drone-shadow"></div>
            </div>
            <div className="scene-label">
              <span>React Three Fiber / WebGL viewport</span>
              <span className="scene-hint">3D model renders in production build</span>
            </div>
          </div>
        </div>

        <div className="twin-sidebar">
          <div className="twin-info card">
            <h3>Drone State</h3>
            <div className="twin-data-list">
              {[
                { label: 'Status', value: 'In Flight', color: 'var(--color-success)' },
                { label: 'Altitude', value: '47.3 m' },
                { label: 'Speed', value: '12.8 m/s' },
                { label: 'Heading', value: '247°' },
                { label: 'Roll', value: '-2.3°' },
                { label: 'Pitch', value: '5.1°' },
                { label: 'Battery', value: '73%', color: 'var(--color-success)' },
                { label: 'Flight Time', value: '14:32' },
              ].map((d, i) => (
                <div key={i} className="twin-data-row">
                  <span className="twin-data-label">{d.label}</span>
                  <span className="twin-data-value" style={d.color ? { color: d.color } : {}}>{d.value}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="twin-info card">
            <h3>Component Health</h3>
            <div className="component-bars">
              {[
                { name: 'Motor 1', health: 95 },
                { name: 'Motor 2', health: 92 },
                { name: 'Motor 3', health: 68 },
                { name: 'Motor 4', health: 91 },
                { name: 'Battery', health: 73 },
                { name: 'GPS', health: 98 },
                { name: 'IMU', health: 96 },
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
