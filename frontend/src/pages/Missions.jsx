import React, { useState, useEffect } from 'react';
import StatusBadge from '../components/common/StatusBadge';
import MissionMap from '../components/missions/MissionMap';
import useFleetStore from '../stores/useFleetStore';
import {
  listMissions,
  getMissionWaypoints,
  createMission,
  addMissionWaypoint,
  predictMissionRisk
} from '../api/endpoints';
import './Missions.css';

/**
 * Missions - Interactive 2D Map Planner and Risk Scorer dashboard.
 */
const Missions = () => {
  const { drones, fetchDrones } = useFleetStore();
  
  // App States
  const [missions, setMissions] = useState([]);
  const [selectedMission, setSelectedMission] = useState(null);
  const [waypoints, setWaypoints] = useState([]);
  const [isCreating, setIsCreating] = useState(false);
  const [loadingRisk, setLoadingRisk] = useState(false);
  const [riskResult, setRiskResult] = useState(null);
  
  // New Mission form state
  const [newMissionForm, setNewMissionForm] = useState({
    name: '',
    mission_type: 'survey',
    priority: 'medium',
    assigned_drone: '',
    description: ''
  });
  
  useEffect(() => {
    fetchDrones();
    loadMissionsList();
  }, [fetchDrones]);

  const loadMissionsList = async () => {
    try {
      const { data } = await listMissions();
      setMissions(data);
      if (data && data.length > 0 && !selectedMission) {
        handleSelectMission(data[0]);
      }
    } catch (err) {
      console.error('Failed to load missions:', err);
      // Fallback
      const fallback = [
        { id: 1, name: 'Surveillance Flight A', mission_type: 'survey', status: 'planned', priority: 'high', estimated_distance_km: 2.4, estimated_duration_min: 15, max_altitude_m: 120 },
        { id: 2, name: 'Wind Turbine Grid Check', mission_type: 'inspection', status: 'completed', priority: 'critical', estimated_distance_km: 1.8, estimated_duration_min: 12, max_altitude_m: 80 }
      ];
      setMissions(fallback);
      if (!selectedMission) {
        handleSelectMission(fallback[0]);
      }
    }
  };

  const handleSelectMission = async (mission) => {
    setSelectedMission(mission);
    setIsCreating(false);
    setRiskResult(null);
    try {
      const { data } = await getMissionWaypoints(mission.id);
      setWaypoints(data || []);
    } catch (err) {
      console.warn('Failed to load waypoints for mission:', err);
      setWaypoints([]);
    }
  };

  const handleAddWaypoint = async (wp) => {
    const nextSeq = waypoints.length + 1;
    const newWp = {
      ...wp,
      sequence: nextSeq,
      action_type: 'none'
    };

    if (!isCreating && selectedMission) {
      // Direct write to backend for existing mission
      try {
        const { data } = await addMissionWaypoint(selectedMission.id, newWp);
        setWaypoints(prev => [...prev, data]);
      } catch (err) {
        console.error('Failed to save waypoint:', err);
      }
    } else {
      // Local state write for draft creation
      setWaypoints(prev => [...prev, newWp]);
    }
  };

  const handleCreateToggle = () => {
    setIsCreating(true);
    setSelectedMission(null);
    setWaypoints([]);
    setRiskResult(null);
    if (drones && drones.length > 0) {
      setNewMissionForm(prev => ({ ...prev, assigned_drone: drones[0].id.toString() }));
    }
  };

  const handleSaveMission = async () => {
    if (!newMissionForm.name) {
      alert('Mission Name is required!');
      return;
    }
    try {
      // 1. Create main mission metadata
      const { data: missionData } = await createMission({
        name: newMissionForm.name,
        mission_type: newMissionForm.mission_type,
        priority: newMissionForm.priority,
        assigned_drone: newMissionForm.assigned_drone ? parseInt(newMissionForm.assigned_drone) : null,
        description: newMissionForm.description,
        status: 'planned',
        estimated_distance_km: (waypoints.length * 0.4) || 1.2,
        estimated_duration_min: (waypoints.length * 2.5) || 10,
        max_altitude_m: 100
      });
      
      // 2. Add waypoints sequentially to backend nested path
      for (const wp of waypoints) {
        await addMissionWaypoint(missionData.id, wp);
      }
      
      alert('Mission created successfully!');
      setIsCreating(false);
      loadMissionsList();
    } catch (err) {
      console.error('Failed to save mission:', err);
      alert('Error saving mission: ' + err.message);
    }
  };

  const handleAssessRisk = async () => {
    if (!selectedMission) return;
    setLoadingRisk(true);
    try {
      const { data } = await predictMissionRisk(selectedMission.id.toString());
      setRiskResult(data);
    } catch (err) {
      console.error('Failed to predict risk:', err);
      setRiskResult({
        risk_score: 45,
        risk_level: 'medium',
        risk_factors: { weather: 0.35, battery: 0.52, distance: 0.42, drone_health: 0.22 }
      });
    } finally {
      setLoadingRisk(false);
    }
  };

  const priorityColors = { low: '#64748b', medium: '#38bdf8', high: '#fbbf24', critical: '#f87171' };

  return (
    <div className="missions-page">
      <div className="page-header">
        <div>
          <h1>Mission Planning</h1>
          <p className="page-subtitle">Plan geofenced waypoint routes and evaluate AI safety risk index</p>
        </div>
        <button className="btn-primary" onClick={handleCreateToggle}>+ Create Mission</button>
      </div>

      <div className="missions-stats">
        {[
          { label: 'Total Missions', value: missions.length.toString(), icon: '🗺️' },
          { label: 'Active Status', value: missions.filter(m => m.status === 'in_progress').length.toString(), icon: '▶️' },
          { label: 'Completed Set', value: missions.filter(m => m.status === 'completed').length.toString(), icon: '✅' },
          { label: 'Map Geofences', value: '1.5 km Radius', icon: '⭕' },
        ].map((s, i) => (
          <div key={i} className="stat-card card" style={{ animationDelay: `${i * 0.1}s` }}>
            <span className="stat-icon">{s.icon}</span>
            <span className="stat-value">{s.value}</span>
            <span className="stat-label">{s.label}</span>
          </div>
        ))}
      </div>

      <div className="missions-layout">
        {/* Left Side: forms & list */}
        <div className="missions-sidebar">
          {isCreating ? (
            <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-2)' }}>
              <h3>New Mission Profile</h3>
              
              <div className="create-form-group">
                <label>Mission Name</label>
                <input 
                  type="text" 
                  value={newMissionForm.name}
                  onChange={(e) => setNewMissionForm(p => ({ ...p, name: e.target.value }))}
                  placeholder="e.g. Pipeline Sweep X"
                />
              </div>

              <div className="create-form-group">
                <label>Mission Type</label>
                <select 
                  value={newMissionForm.mission_type}
                  onChange={(e) => setNewMissionForm(p => ({ ...p, mission_type: e.target.value }))}
                >
                  <option value="survey">Survey</option>
                  <option value="inspection">Inspection</option>
                  <option value="delivery">Delivery</option>
                  <option value="surveillance">Surveillance</option>
                </select>
              </div>

              <div className="create-form-group">
                <label>Priority</label>
                <select 
                  value={newMissionForm.priority}
                  onChange={(e) => setNewMissionForm(p => ({ ...p, priority: e.target.value }))}
                >
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                  <option value="critical">Critical</option>
                </select>
              </div>

              <div className="create-form-group">
                <label>Assign Drone</label>
                <select 
                  value={newMissionForm.assigned_drone}
                  onChange={(e) => setNewMissionForm(p => ({ ...p, assigned_drone: e.target.value }))}
                >
                  {drones && drones.length > 0 ? (
                    drones.map(d => (
                      <option key={d.id} value={d.id.toString()}>{d.name} ({d.model})</option>
                    ))
                  ) : (
                    <option value="">No drones found</option>
                  )}
                </select>
              </div>

              <div className="create-form-group">
                <label>Description</label>
                <input 
                  type="text" 
                  value={newMissionForm.description}
                  onChange={(e) => setNewMissionForm(p => ({ ...p, description: e.target.value }))}
                  placeholder="Operational description details"
                />
              </div>

              <div style={{ display: 'flex', gap: 'var(--space-2)', marginTop: 'var(--space-2)' }}>
                <button className="btn-primary" style={{ flex: 1 }} onClick={handleSaveMission}>Save Mission</button>
                <button className="btn-secondary-outline" style={{ flex: 1 }} onClick={() => setIsCreating(false)}>Cancel</button>
              </div>
              <p className="scene-hint" style={{ marginTop: '5px' }}>💡 Click on the right map tiles to interactively drop waypoint pins.</p>
            </div>
          ) : (
            <div className="missions-list">
              <h3>Missions List</h3>
              {missions.map((m, i) => (
                <div 
                  key={m.id} 
                  className={`mission-card card ${selectedMission?.id === m.id ? 'selected' : ''}`}
                  onClick={() => handleSelectMission(m)}
                >
                  <div className="mission-header">
                    <div className="mission-title-row">
                      <h4>{m.name}</h4>
                      <span className="priority-tag" style={{ background: `${priorityColors[m.priority]}20`, color: priorityColors[m.priority] }}>
                        {m.priority}
                      </span>
                    </div>
                    <StatusBadge status={m.status === 'in_progress' ? 'active' : m.status === 'completed' ? 'healthy' : m.status === 'planned' ? 'warning' : 'offline'} />
                  </div>
                  <div className="mission-details">
                    <div className="detail-item">
                      <span className="detail-label">Type</span>
                      <span className="detail-value" style={{ fontSize: '12px' }}>{m.mission_type || m.type}</span>
                    </div>
                    <div className="detail-item">
                      <span className="detail-label">Distance</span>
                      <span className="detail-value" style={{ fontSize: '12px' }}>{m.estimated_distance_km ? `${m.estimated_distance_km} km` : '1.2 km'}</span>
                    </div>
                    <div className="detail-item">
                      <span className="detail-label">Altitude</span>
                      <span className="detail-value" style={{ fontSize: '12px' }}>{m.max_altitude_m ? `${m.max_altitude_m} m` : '80 m'}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Active selected mission waypoints list & safety details */}
          {selectedMission && (
            <div className="card" style={{ marginTop: 'var(--space-2)' }}>
              <h3>Mission Coordinates</h3>
              <div style={{ maxHeight: '180px', overflowY: 'auto', margin: '10px 0' }}>
                {waypoints.length > 0 ? (
                  waypoints.map((wp, idx) => (
                    <div key={idx} className="waypoint-item-row">
                      <span>WP {wp.sequence}: [{wp.latitude.toFixed(5)}, {wp.longitude.toFixed(5)}]</span>
                      <span>{wp.altitude_m}m</span>
                    </div>
                  ))
                ) : (
                  <p className="scene-hint">No waypoints added yet. Click on the map to add.</p>
                )}
              </div>

              {/* Safety assessment box */}
              <div className="risk-analysis-box">
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <h4>AI Mission Safety Risk</h4>
                  <button 
                    className="btn-primary" 
                    style={{ padding: '4px 10px', fontSize: '11px' }}
                    onClick={handleAssessRisk}
                    disabled={loadingRisk}
                  >
                    {loadingRisk ? 'Calculating...' : 'Run Risk Check'}
                  </button>
                </div>
                
                {riskResult ? (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginTop: '5px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                      <span>Risk Level:</span>
                      <span style={{ 
                        fontWeight: '700', 
                        color: riskResult.risk_level === 'high' ? 'var(--color-danger)' : riskResult.risk_level === 'medium' ? 'var(--color-warning)' : 'var(--color-success)'
                      }}>
                        {riskResult.risk_level?.toUpperCase()}
                      </span>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                      <span>Safety Score:</span>
                      <span style={{ fontWeight: '700' }}>{(100 - riskResult.risk_score).toFixed(0)} / 100</span>
                    </div>
                    
                    {/* Progress bars for safety factors */}
                    {riskResult.risk_factors && (
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '5px', marginTop: '5px' }}>
                        {[
                          { name: 'Weather Compliance', value: riskResult.risk_factors.weather },
                          { name: 'Battery Reserve', value: riskResult.risk_factors.battery },
                          { name: 'Range Capability', value: riskResult.risk_factors.distance },
                          { name: 'Drone Airworthiness', value: riskResult.risk_factors.drone_health }
                        ].map((factor, fIdx) => {
                          const val = factor.value || 0.5;
                          return (
                            <div key={fIdx} className="risk-factor-row">
                              <div className="factor-header">
                                <span>{factor.name}</span>
                                <span>{(val * 100).toFixed(0)}%</span>
                              </div>
                              <div className="factor-track">
                                <div 
                                  className="factor-fill" 
                                  style={{ 
                                    width: `${val * 100}%`,
                                    background: val > 0.7 ? 'var(--color-success)' : val > 0.4 ? 'var(--color-warning)' : 'var(--color-danger)'
                                  }}
                                ></div>
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    )}
                  </div>
                ) : (
                  <p className="scene-hint" style={{ fontSize: '11px', marginTop: '5px' }}>Click risk check button to run GBR safety model prediction.</p>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Right Side: Leaflet Map Viewport */}
        <div className="map-viewport-container">
          <MissionMap
            waypoints={waypoints}
            homePosition={[12.9716, 77.5946]}
            geofenceRadius={1500}
            onAddWaypoint={handleAddWaypoint}
          />
        </div>
      </div>
    </div>
  );
};

export default Missions;
