import React, { useRef } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, PerspectiveCamera } from '@react-three/drei';

/**
 * Propeller Component - Renders a spinning blade.
 */
const Propeller = ({ rpm = 0 }) => {
  const ref = useRef();
  
  // Rotate propeller based on simulated RPM (scaled down for visual comfort)
  useFrame((state, delta) => {
    if (ref.current) {
      const speed = (rpm / 60) * Math.PI * 2 * delta * 0.1;
      ref.current.rotation.y += Math.max(0.1, speed);
    }
  });

  return (
    <mesh ref={ref} position={[0, 0.1, 0]}>
      <boxGeometry args={[0.8, 0.01, 0.05]} />
      <meshStandardMaterial color="#cbd5e1" roughness={0.1} metalness={0.9} />
    </mesh>
  );
};

/**
 * Quadcopter 3D model assembled from primitive geometries.
 * Dynamic coloring maps to component health thresholds.
 */
const DroneModel = ({ roll = 0, pitch = 0, heading = 0, rpms = [0, 0, 0, 0], healths = {} }) => {
  const groupRef = useRef();

  // Convert degree orientations to radians for 3D rotations
  const rollRad = (roll * Math.PI) / 180;
  const pitchRad = (pitch * Math.PI) / 180;
  const headingRad = (heading * Math.PI) / 180;

  // Resolve health display colors per component
  const getHealthColor = (health = 100) => {
    if (health > 80) return '#10b981'; // Green (healthy)
    if (health > 60) return '#f59e0b'; // Amber (warning)
    return '#ef4444'; // Red (critical)
  };

  return (
    <group
      ref={groupRef}
      rotation={[pitchRad, headingRad, rollRad]}
      position={[0, 0, 0]}
    >
      {/* 1. Central Avionics Hub */}
      <mesh position={[0, 0, 0]}>
        <cylinderGeometry args={[0.4, 0.4, 0.2, 16]} />
        <meshStandardMaterial color="#1e293b" roughness={0.5} metalness={0.8} />
      </mesh>
      
      {/* Status LED Indicator */}
      <mesh position={[0, 0.11, 0]}>
        <sphereGeometry args={[0.08, 16, 16]} />
        <meshStandardMaterial 
          color={getHealthColor(healths.battery || 100)} 
          emissive={getHealthColor(healths.battery || 100)} 
          emissiveIntensity={1.5}
        />
      </mesh>

      {/* 2. Structural Diagonal Carbon-fiber Arms */}
      {/* Front-Right to Back-Left Arm */}
      <mesh rotation={[0, 0, Math.PI / 4]} position={[0, 0, 0]}>
        <cylinderGeometry args={[0.04, 0.04, 1.8, 8]} />
        <meshStandardMaterial color="#0f172a" roughness={0.8} metalness={0.9} />
      </mesh>
      
      {/* Front-Left to Back-Right Arm */}
      <mesh rotation={[0, 0, -Math.PI / 4]} position={[0, 0, 0]}>
        <cylinderGeometry args={[0.04, 0.04, 1.8, 8]} />
        <meshStandardMaterial color="#0f172a" roughness={0.8} metalness={0.9} />
      </mesh>

      {/* 3. Motor Pods & Propellers */}
      {/* Motor 1 (Front Right: positive X, positive Y in rotation offset) */}
      <group position={[0.63, 0.63, 0]}>
        <mesh>
          <cylinderGeometry args={[0.08, 0.08, 0.15, 12]} />
          <meshStandardMaterial color={getHealthColor(healths.motor_1 || 100)} roughness={0.3} metalness={0.8} />
        </mesh>
        <Propeller rpm={rpms[0]} />
      </group>

      {/* Motor 2 (Front Left: negative X, positive Y in rotation offset) */}
      <group position={[-0.63, 0.63, 0]}>
        <mesh>
          <cylinderGeometry args={[0.08, 0.08, 0.15, 12]} />
          <meshStandardMaterial color={getHealthColor(healths.motor_2 || 100)} roughness={0.3} metalness={0.8} />
        </mesh>
        <Propeller rpm={rpms[1]} />
      </group>

      {/* Motor 3 (Back Left: negative X, negative Y in rotation offset) */}
      <group position={[-0.63, -0.63, 0]}>
        <mesh>
          <cylinderGeometry args={[0.08, 0.08, 0.15, 12]} />
          <meshStandardMaterial color={getHealthColor(healths.motor_3 || 100)} roughness={0.3} metalness={0.8} />
        </mesh>
        <Propeller rpm={rpms[2]} />
      </group>

      {/* Motor 4 (Back Right: positive X, negative Y in rotation offset) */}
      <group position={[0.63, -0.63, 0]}>
        <mesh>
          <cylinderGeometry args={[0.08, 0.08, 0.15, 12]} />
          <meshStandardMaterial color={getHealthColor(healths.motor_4 || 100)} roughness={0.3} metalness={0.8} />
        </mesh>
        <Propeller rpm={rpms[3]} />
      </group>
    </group>
  );
};

/**
 * 3D Scene Viewport containing cameras, lights, and orbit controls.
 */
const DroneScene = ({ roll = 0, pitch = 0, heading = 0, rpms = [0, 0, 0, 0], healths = {} }) => {
  return (
    <div style={{ width: '100%', height: '100%', minHeight: '380px', position: 'relative' }}>
      <Canvas style={{ background: '#0b0f19' }}>
        <PerspectiveCamera makeDefault position={[0, 2.5, 3.5]} fov={50} />
        <OrbitControls enableZoom={true} maxPolarAngle={Math.PI / 2.1} />
        
        {/* Lights */}
        <ambientLight intensity={0.5} />
        <directionalLight position={[5, 10, 5]} intensity={1.0} castShadow />
        <pointLight position={[-5, 5, -5]} intensity={0.5} />

        {/* Rotated coordinate floor grid */}
        <gridHelper args={[20, 20, '#38bdf8', '#1e293b']} rotation={[Math.PI / 2, 0, 0]} position={[0, -0.2, 0]} />

        {/* Drone model */}
        <DroneModel 
          roll={roll} 
          pitch={pitch} 
          heading={heading} 
          rpms={rpms} 
          healths={healths} 
        />
      </Canvas>
    </div>
  );
};

export default DroneScene;
