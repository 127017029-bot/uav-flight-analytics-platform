/**
 * @file useFleetStore.js
 * @description Zustand store for fleet / drone state management.
 * Manages the drone list, loading state, errors, and selected drone.
 */

import { create } from 'zustand';
import { listDrones, getDrone } from '../api/endpoints';

/**
 * @typedef {Object} FleetState
 * @property {Array<Object>} drones – List of drones
 * @property {boolean} loading – Whether a fetch is in progress
 * @property {string|null} error – Last error message
 * @property {Object|null} selectedDrone – Currently selected drone
 * @property {() => Promise<void>} fetchDrones – Fetch all drones
 * @property {(id: string) => Promise<void>} fetchDroneById – Fetch single drone
 */

const useFleetStore = create((set) => ({
  drones: [],
  loading: false,
  error: null,
  selectedDrone: null,

  /**
   * Fetch the full drone list from the API.
   */
  fetchDrones: async () => {
    set({ loading: true, error: null });
    try {
      const { data } = await listDrones();
      const drones = Array.isArray(data)
        ? data
        : data?.results || [];
      set({ drones, loading: false });
    } catch (err) {
      set({ error: err.message || 'Failed to fetch drones', loading: false });
    }
  },

  /**
   * Fetch a single drone by ID.
   * @param {string} id
   */
  fetchDroneById: async (id) => {
    set({ loading: true, error: null });
    try {
      const { data } = await getDrone(id);
      set({ selectedDrone: data, loading: false });
    } catch (err) {
      set({ error: err.message || 'Failed to fetch drone', loading: false });
    }
  },
}));

export default useFleetStore;
