/**
 * @file useAlertStore.js
 * @description Zustand store for alert state management.
 * Manages alert list, unread count, and alert actions.
 */

import { create } from 'zustand';
import { listAlerts, acknowledgeAlert as ackAlertApi } from '../api/endpoints';

/**
 * @typedef {Object} AlertState
 * @property {Array<Object>} alerts – Alert list
 * @property {number} unreadCount – Unacknowledged alert count
 * @property {() => Promise<void>} fetchAlerts – Fetch alerts from API
 * @property {(id: string) => Promise<void>} acknowledgeAlert – Acknowledge an alert
 */

const useAlertStore = create((set, get) => ({
  alerts: [],
  unreadCount: 0,

  /**
   * Fetch alerts from the API and compute unread count.
   */
  fetchAlerts: async () => {
    try {
      const { data } = await listAlerts();
      const unread = data.filter((a) => !a.acknowledged).length;
      set({ alerts: data, unreadCount: unread });
    } catch (err) {
      console.error('Failed to fetch alerts:', err);
    }
  },

  /**
   * Acknowledge a single alert by ID.
   * @param {string} id
   */
  acknowledgeAlert: async (id) => {
    try {
      await ackAlertApi(id);
      const alerts = get().alerts.map((a) =>
        a.id === id ? { ...a, acknowledged: true } : a
      );
      const unread = alerts.filter((a) => !a.acknowledged).length;
      set({ alerts, unreadCount: unread });
    } catch (err) {
      console.error('Failed to acknowledge alert:', err);
    }
  },
}));

export default useAlertStore;
