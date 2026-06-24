/**
 * @file useTelemetryStore.js
 * @description Zustand store for real-time telemetry state.
 * Manages latest telemetry data, chart data, streaming status, and WS state.
 */

import { create } from 'zustand';

/**
 * @typedef {Object} TelemetryState
 * @property {Object} latestTelemetry – Most recent telemetry per drone
 * @property {Object} chartData – Time-series data keyed by metric
 * @property {Object} stats – Aggregated stat snapshots
 * @property {boolean} isStreaming – Whether data is streaming
 * @property {'disconnected'|'connecting'|'connected'|'error'} wsStatus
 */

const useTelemetryStore = create((set) => ({
  latestTelemetry: {},
  chartData: {},
  stats: {},
  isStreaming: false,
  wsStatus: 'disconnected',

  /**
   * Update the latest telemetry reading for a drone.
   * @param {string} droneId
   * @param {Object} data
   */
  updateTelemetry: (droneId, data) =>
    set((state) => ({
      latestTelemetry: { ...state.latestTelemetry, [droneId]: data },
    })),

  /**
   * Append a data point to the chart time-series.
   * @param {string} metric
   * @param {Object} point – { timestamp, value }
   */
  appendChartData: (metric, point) =>
    set((state) => {
      const existing = state.chartData[metric] || [];
      // Keep the last 100 data points per metric
      const updated = [...existing, point].slice(-100);
      return { chartData: { ...state.chartData, [metric]: updated } };
    }),

  /**
   * Set aggregated stats.
   * @param {Object} stats
   */
  setStats: (stats) => set({ stats }),

  /** Mark streaming on/off */
  setStreaming: (val) => set({ isStreaming: val }),

  /** Update WebSocket connection status */
  setWsStatus: (status) => set({ wsStatus: status }),
}));

export default useTelemetryStore;
