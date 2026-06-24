import React from 'react';
import './AIInsights.css';

/** AIInsights - ML model dashboard with prediction capabilities. */
const AIInsights = () => {
  const models = [
    {
      name: 'Battery RUL Prediction',
      type: 'Gradient Boosting / LSTM',
      description: 'Predicts remaining useful life of LiPo batteries based on charge-discharge cycle telemetry features.',
      status: 'active',
      accuracy: '94.2%',
      metric: 'R² = 0.942',
      predictions: 1247,
      lastRun: '2 min ago',
      icon: '🔋',
      gradient: 'linear-gradient(135deg, #34d399 0%, #38bdf8 100%)',
    },
    {
      name: 'Motor Anomaly Detection',
      type: 'Isolation Forest',
      description: 'Detects anomalous motor behavior — bearing wear, prop imbalance, ESC faults, and overheating.',
      status: 'active',
      accuracy: '91.8%',
      metric: 'F1 = 0.918',
      predictions: 3891,
      lastRun: '30 sec ago',
      icon: '⚙️',
      gradient: 'linear-gradient(135deg, #f87171 0%, #fbbf24 100%)',
    },
    {
      name: 'Mission Risk Assessment',
      type: 'XGBoost Regressor',
      description: 'Scores mission risk 0-100 based on weather, battery health, drone hours, terrain, and payload factors.',
      status: 'active',
      accuracy: '89.5%',
      metric: 'R² = 0.895',
      predictions: 456,
      lastRun: '15 min ago',
      icon: '🎯',
      gradient: 'linear-gradient(135deg, #a78bfa 0%, #38bdf8 100%)',
    },
    {
      name: 'Predictive Maintenance',
      type: 'Random Forest Classifier',
      description: 'Classifies component maintenance urgency into low/medium/high/critical based on health metrics.',
      status: 'active',
      accuracy: '87.3%',
      metric: 'F1 = 0.873',
      predictions: 892,
      lastRun: '5 min ago',
      icon: '🔧',
      gradient: 'linear-gradient(135deg, #fbbf24 0%, #f87171 100%)',
    },
  ];

  return (
    <div className="ai-page">
      <div className="page-header">
        <div>
          <h1>AI Insights</h1>
          <p className="page-subtitle">Machine learning models and prediction dashboard</p>
        </div>
        <button className="btn-primary">Run Batch Analysis</button>
      </div>

      <div className="ai-overview">
        {[
          { label: 'Active Models', value: '4', icon: '🧠' },
          { label: 'Total Predictions', value: '6,486', icon: '📊' },
          { label: 'Avg Accuracy', value: '90.7%', icon: '🎯' },
          { label: 'Alerts Generated', value: '23', icon: '⚡' },
        ].map((s, i) => (
          <div key={i} className="ai-stat card" style={{ animationDelay: `${i * 0.1}s` }}>
            <span className="ai-stat-icon">{s.icon}</span>
            <span className="ai-stat-value">{s.value}</span>
            <span className="ai-stat-label">{s.label}</span>
          </div>
        ))}
      </div>

      <div className="model-grid">
        {models.map((m, i) => (
          <div key={i} className="model-card" style={{ animationDelay: `${(i + 4) * 0.1}s` }}>
            <div className="model-card-border" style={{ background: m.gradient }}></div>
            <div className="model-card-content">
              <div className="model-header">
                <span className="model-icon">{m.icon}</span>
                <div className="model-status">
                  <span className="status-dot active"></span>
                  <span>Active</span>
                </div>
              </div>
              <h3>{m.name}</h3>
              <p className="model-type">{m.type}</p>
              <p className="model-desc">{m.description}</p>
              <div className="model-metrics">
                <div className="metric-item">
                  <span className="metric-value">{m.accuracy}</span>
                  <span className="metric-label">Accuracy</span>
                </div>
                <div className="metric-item">
                  <span className="metric-value">{m.predictions.toLocaleString()}</span>
                  <span className="metric-label">Predictions</span>
                </div>
                <div className="metric-item">
                  <span className="metric-value">{m.lastRun}</span>
                  <span className="metric-label">Last Run</span>
                </div>
              </div>
              <div className="model-actions">
                <button className="btn-predict">Run Prediction</button>
                <button className="btn-details">View Details</button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default AIInsights;
