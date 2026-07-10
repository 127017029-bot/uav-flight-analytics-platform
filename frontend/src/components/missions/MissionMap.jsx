import React from 'react';
import { MapContainer, TileLayer, Marker, Polyline, Circle, useMapEvents } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

// Fix Leaflet default marker icon issues by defining custom styled divIcons
const createWaypointIcon = (index) => L.divIcon({
  className: 'custom-waypoint-icon',
  html: `<div style="
    background: var(--color-accent, #38bdf8);
    color: #000;
    width: 24px;
    height: 24px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 11px;
    font-weight: 700;
    border: 2px solid #fff;
    box-shadow: 0 2px 4px rgba(0,0,0,0.3);
  ">${index + 1}</div>`,
  iconSize: [24, 24],
  iconAnchor: [12, 12]
});

const homeIcon = L.divIcon({
  className: 'custom-home-icon',
  html: `<div style="
    background: #ef4444;
    color: #fff;
    width: 28px;
    height: 28px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 14px;
    border: 2px solid #fff;
    box-shadow: 0 2px 4px rgba(0,0,0,0.3);
  ">🏠</div>`,
  iconSize: [28, 28],
  iconAnchor: [14, 14]
});

/**
 * Click handler hook to add waypoints dynamically.
 */
const MapClickHandler = ({ onMapClick }) => {
  useMapEvents({
    click(e) {
      onMapClick([e.latlng.lat, e.latlng.lng]);
    }
  });
  return null;
};

/**
 * Interactive Leaflet Map for plotting waypoints and geofences.
 */
const MissionMap = ({ waypoints = [], homePosition = [12.9716, 77.5946], geofenceRadius = 1500, onAddWaypoint }) => {
  // Karnataka/Bengaluru coordinates as default center
  const center = homePosition;
  const polylineCoords = [homePosition, ...waypoints.map(w => [w.latitude, w.longitude])];

  return (
    <div style={{ width: '100%', height: '100%', minHeight: '420px', borderRadius: 'var(--radius-lg)', overflow: 'hidden' }}>
      <MapContainer 
        center={center} 
        zoom={14} 
        style={{ width: '100%', height: '100%' }}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
          url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
        />
        
        {/* Click mapping handler */}
        <MapClickHandler onMapClick={(coords) => onAddWaypoint({ latitude: coords[0], longitude: coords[1], altitude_m: 80 })} />

        {/* Home Base Marker */}
        <Marker position={homePosition} icon={homeIcon} />

        {/* Geofence Boundary ring */}
        <Circle
          center={homePosition}
          radius={geofenceRadius}
          pathOptions={{
            color: '#ef4444',
            fillColor: '#ef4444',
            fillOpacity: 0.08,
            dashArray: '5, 8'
          }}
        />

        {/* Waypoints markers */}
        {waypoints.map((wp, index) => (
          <Marker 
            key={index} 
            position={[wp.latitude, wp.longitude]} 
            icon={createWaypointIcon(index)}
          />
        ))}

        {/* Polyline flight paths */}
        {polylineCoords.length > 1 && (
          <Polyline 
            positions={polylineCoords} 
            pathOptions={{
              color: 'var(--color-accent, #38bdf8)',
              weight: 3,
              opacity: 0.8,
              dashArray: '3, 6'
            }}
          />
        )}
      </MapContainer>
    </div>
  );
};

export default MissionMap;
