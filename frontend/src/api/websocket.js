import useTelemetryStore from '../stores/useTelemetryStore';

let socket = null;
let reconnectTimer = null;
let reconnectDelay = 1000;
const MAX_RECONNECT_DELAY = 16000;

/**
 * Establish a live WebSocket connection to stream drone telemetry.
 *
 * @param {string} droneId
 */
export const connectWebSocket = (droneId) => {
  if (socket) {
    socket.close();
  }

  const getWsURL = () => {
    const envUrl = import.meta.env.VITE_WS_URL;
    if (envUrl) {
      return `${envUrl}/telemetry/${droneId}/`;
    }
    // Local development check
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
      return `ws://localhost:8000/ws/telemetry/${droneId}/`;
    }
    return `wss://uav-flight-analytics-platform-production.up.railway.app/ws/telemetry/${droneId}/`;
  };

  const wsUrl = getWsURL();

  const { setWsStatus, setStreaming, updateTelemetry, appendChartData } = useTelemetryStore.getState();

  console.log(`[WS] Connecting to ${wsUrl}`);
  setWsStatus('connecting');

  socket = new WebSocket(wsUrl);

  socket.onopen = () => {
    console.log(`[WS] Connected successfully to telemetry for drone ${droneId}`);
    setWsStatus('connected');
    setStreaming(true);
    reconnectDelay = 1000;
    if (reconnectTimer) {
      clearTimeout(reconnectTimer);
      reconnectTimer = null;
    }
  };

  socket.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      updateTelemetry(droneId, data);
      
      const timestamp = data.timestamp;
      appendChartData('altitude', { timestamp, value: data.altitude_msl });
      appendChartData('speed', { timestamp, value: data.ground_speed });
      appendChartData('battery', { timestamp, value: data.battery_percentage });
      appendChartData('motor_rpm_1', { timestamp, value: data.motor_rpm_1 });
      appendChartData('motor_rpm_2', { timestamp, value: data.motor_rpm_2 });
      appendChartData('motor_rpm_3', { timestamp, value: data.motor_rpm_3 });
      appendChartData('motor_rpm_4', { timestamp, value: data.motor_rpm_4 });
      appendChartData('vibration_x', { timestamp, value: data.vibration_x });
      appendChartData('vibration_y', { timestamp, value: data.vibration_y });
      appendChartData('vibration_z', { timestamp, value: data.vibration_z });
    } catch (err) {
      console.error('[WS] Error parsing websocket message:', err);
    }
  };

  socket.onclose = (event) => {
    console.log('[WS] Closed:', event.reason);
    setWsStatus('disconnected');
    setStreaming(false);
    
    // Auto-reconnect if it wasn't an intentional disconnect
    if (event.code !== 1000) {
      scheduleReconnect(droneId);
    }
  };

  socket.onerror = (error) => {
    console.error('[WS] Error:', error);
    setWsStatus('error');
    socket.close();
  };
};

const scheduleReconnect = (droneId) => {
  if (reconnectTimer) return;
  console.log(`[WS] Scheduling reconnect in ${reconnectDelay}ms`);
  reconnectTimer = setTimeout(() => {
    reconnectTimer = null;
    reconnectDelay = Math.min(reconnectDelay * 2, MAX_RECONNECT_DELAY);
    connectWebSocket(droneId);
  }, reconnectDelay);
};

/**
 * Disconnect the active WebSocket connection.
 */
export const disconnectWebSocket = () => {
  if (reconnectTimer) {
    clearTimeout(reconnectTimer);
    reconnectTimer = null;
  }
  if (socket) {
    socket.close(1000, 'User disconnected');
    socket = null;
  }
  const { setWsStatus, setStreaming } = useTelemetryStore.getState();
  setWsStatus('disconnected');
  setStreaming(false);
};
