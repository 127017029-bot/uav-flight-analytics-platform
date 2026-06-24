/**
 * @file GaugeWidget.jsx
 * @description SVG circular gauge with animated arc fill and centered value
 * display. Great for telemetry metrics like altitude, speed, battery.
 */

import './GaugeWidget.css';

/**
 * GaugeWidget — Circular progress gauge.
 *
 * @param {Object} props
 * @param {number} props.value – Current value
 * @param {number} props.max – Maximum value (100% = full arc)
 * @param {string} props.label – Metric label (e.g. "Altitude")
 * @param {string} [props.unit] – Unit suffix (e.g. "m", "%")
 * @param {string} [props.color='#38bdf8'] – Stroke colour
 * @param {number} [props.size=120] – SVG diameter in px
 * @param {number} [props.strokeWidth=8] – Stroke width in px
 * @returns {JSX.Element}
 */
export default function GaugeWidget({
  value,
  max,
  label,
  unit = '',
  color = '#38bdf8',
  size = 120,
  strokeWidth = 8,
}) {
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const pct = Math.min(value / max, 1);
  const offset = circumference * (1 - pct);
  const glowColor = color.replace(')', ',0.3)').replace('rgb', 'rgba');

  return (
    <div className="gauge-widget">
      <div style={{ position: 'relative', width: size, height: size }}>
        <svg
          className="gauge-widget__svg"
          width={size}
          height={size}
          style={{ '--gauge-glow': glowColor }}
        >
          {/* Background track */}
          <circle
            className="gauge-widget__track"
            cx={size / 2}
            cy={size / 2}
            r={radius}
            strokeWidth={strokeWidth}
          />
          {/* Filled arc */}
          <circle
            className="gauge-widget__fill"
            cx={size / 2}
            cy={size / 2}
            r={radius}
            strokeWidth={strokeWidth}
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            style={{ '--gauge-color': color }}
          />
        </svg>

        {/* Center text */}
        <div className="gauge-widget__center">
          <div className="gauge-widget__value">{value}</div>
          {unit && <div className="gauge-widget__unit">{unit}</div>}
        </div>
      </div>

      <span className="gauge-widget__label">{label}</span>
    </div>
  );
}
