/**
 * @file API endpoint functions for the UAV Digital Twin Platform.
 *
 * Every export is a thin wrapper around the shared Axios `client` instance.
 * Grouped by domain for easy discovery.
 */

import client from './client';

/* ================================================================== */
/*  Auth                                                              */
/* ================================================================== */

/** @param {{ email: string, password: string }} creds */
export const login = (creds) => client.post('/auth/login', creds);

/** @param {{ email: string, password: string, name: string }} data */
export const register = (data) => client.post('/auth/register', data);

export const refreshToken = () => client.post('/auth/refresh');

export const getProfile = () => client.get('/auth/profile');

/* ================================================================== */
/*  Drones                                                            */
/* ================================================================== */

/** @param {Object} [params] – query params such as { status, limit, offset } */
export const listDrones = (params) => client.get('/drones', { params });

/** @param {string} id */
export const getDrone = (id) => client.get(`/drones/${id}`);

/** @param {Object} data */
export const createDrone = (data) => client.post('/drones', data);

/** @param {string} id @param {Object} data */
export const updateDrone = (id, data) => client.put(`/drones/${id}`, data);

/** @param {string} id */
export const deleteDrone = (id) => client.delete(`/drones/${id}`);

/** @param {string} id */
export const getDroneHealth = (id) => client.get(`/drones/${id}/health`);

/** @param {string} id */
export const getDroneBattery = (id) => client.get(`/drones/${id}/battery`);

/* ================================================================== */
/*  Flights                                                           */
/* ================================================================== */

export const listFlights = (params) => client.get('/flights', { params });

export const getFlight = (id) => client.get(`/flights/${id}`);

export const createFlight = (data) => client.post('/flights', data);

/** @param {string} flightId */
export const getFlightTelemetry = (flightId) =>
  client.get(`/flights/${flightId}/telemetry`);

/** @param {string} flightId */
export const getFlightAnalytics = (flightId) =>
  client.get(`/flights/${flightId}/analytics`);

/* ================================================================== */
/*  Telemetry                                                         */
/* ================================================================== */

/** @param {Object} payload – raw telemetry packet */
export const ingestTelemetry = (payload) =>
  client.post('/telemetry/ingest', payload);

/** @param {string} droneId */
export const getLatestTelemetry = (droneId) =>
  client.get(`/telemetry/${droneId}/latest`);

/** @param {string} droneId @param {Object} [params] */
export const getTelemetryStats = (droneId, params) =>
  client.get(`/telemetry/${droneId}/stats`, { params });

/** @param {string} droneId @param {Object} [params] – { metric, from, to } */
export const getTelemetryChartData = (droneId, params) =>
  client.get(`/telemetry/${droneId}/chart`, { params });

/* ================================================================== */
/*  Missions                                                          */
/* ================================================================== */

export const listMissions = (params) => client.get('/missions', { params });

export const getMission = (id) => client.get(`/missions/${id}`);

export const createMission = (data) => client.post('/missions', data);

export const updateMission = (id, data) =>
  client.put(`/missions/${id}`, data);

export const getMissionWaypoints = (id) =>
  client.get(`/missions/${id}/waypoints`);

export const addMissionWaypoint = (id, data) =>
  client.post(`/missions/${id}/waypoints`, data);

/* ================================================================== */
/*  Maintenance                                                       */
/* ================================================================== */

export const listMaintenance = (params) =>
  client.get('/maintenance', { params });

export const getMaintenance = (id) => client.get(`/maintenance/${id}`);

export const createMaintenance = (data) =>
  client.post('/maintenance', data);

export const updateMaintenance = (id, data) =>
  client.put(`/maintenance/${id}`, data);

/* ================================================================== */
/*  Alerts                                                            */
/* ================================================================== */

export const listAlerts = (params) => client.get('/alerts', { params });

/** @param {string} id */
export const acknowledgeAlert = (id) =>
  client.put(`/alerts/${id}/acknowledge`);

/** @param {string} id */
export const resolveAlert = (id) => client.put(`/alerts/${id}/resolve`);

/* ================================================================== */
/*  Analytics                                                         */
/* ================================================================== */

export const getFlightSummary = (params) =>
  client.get('/analytics/flight-summary', { params });

export const getFleetDaily = (params) =>
  client.get('/analytics/fleet-daily', { params });

export const getFleetTrends = (params) =>
  client.get('/analytics/fleet-trends', { params });

export const getDroneEfficiency = (droneId, params) =>
  client.get(`/analytics/drone/${droneId}/efficiency`, { params });

export const getAnalyticsComparison = (params) =>
  client.get('/analytics/comparison', { params });

/* ================================================================== */
/*  Fleet                                                             */
/* ================================================================== */

export const getFleetOverview = () => client.get('/fleet/overview');

export const getFleetStatus = () => client.get('/fleet/status');

/* ================================================================== */
/*  ML / Predictions                                                  */
/* ================================================================== */

export const listMLModels = () => client.get('/ml/models');

export const listPredictions = (params) =>
  client.get('/ml/predictions', { params });

/** @param {string} droneId */
export const predictBatteryRUL = (droneId) =>
  client.post(`/ml/predict/battery-rul`, { drone_id: droneId });

/** @param {string} droneId */
export const predictMotorAnomaly = (droneId) =>
  client.post(`/ml/predict/motor-anomaly`, { drone_id: droneId });

/** @param {string} flightId */
export const predictFlightAnomaly = (flightId) =>
  client.post(`/ml/predict/flight-anomaly`, { flight_id: flightId });

/** @param {string} missionId */
export const predictMissionRisk = (missionId) =>
  client.post(`/ml/predict/mission-risk`, { mission_id: missionId });

/** @param {string} droneId */
export const predictMaintenance = (droneId) =>
  client.post(`/ml/predict/maintenance`, { drone_id: droneId });

/** @param {Object} payload – { drone_ids: string[] } */
export const batchAnalyze = (payload) =>
  client.post('/ml/batch-analyze', payload);
