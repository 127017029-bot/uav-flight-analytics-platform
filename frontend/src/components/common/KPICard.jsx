/**
 * @file KPICard.jsx
 * @description Glassmorphism KPI stat card with icon, large value display,
 * trend indicator (up/down), and subtitle. Supports custom accent colour.
 */

import { TrendingUp, TrendingDown } from 'lucide-react';
import './KPICard.css';

/**
 * Map colour prop to CSS custom-property overrides applied via inline style.
 * @param {string} color
 * @returns {Object} CSS custom properties object
 */
function accentVars(color) {
  const palette = {
    blue: {
      '--kpi-accent': 'linear-gradient(135deg, #38bdf8, #7dd3fc)',
      '--kpi-accent-glow': 'rgba(56,189,248,0.25)',
      '--kpi-accent-bg': 'rgba(56,189,248,0.1)',
      '--kpi-accent-color': '#38bdf8',
    },
    purple: {
      '--kpi-accent': 'linear-gradient(135deg, #a78bfa, #c4b5fd)',
      '--kpi-accent-glow': 'rgba(167,139,250,0.25)',
      '--kpi-accent-bg': 'rgba(167,139,250,0.1)',
      '--kpi-accent-color': '#a78bfa',
    },
    green: {
      '--kpi-accent': 'linear-gradient(135deg, #34d399, #6ee7b7)',
      '--kpi-accent-glow': 'rgba(52,211,153,0.25)',
      '--kpi-accent-bg': 'rgba(52,211,153,0.1)',
      '--kpi-accent-color': '#34d399',
    },
    amber: {
      '--kpi-accent': 'linear-gradient(135deg, #fbbf24, #fde68a)',
      '--kpi-accent-glow': 'rgba(251,191,36,0.25)',
      '--kpi-accent-bg': 'rgba(251,191,36,0.1)',
      '--kpi-accent-color': '#fbbf24',
    },
    red: {
      '--kpi-accent': 'linear-gradient(135deg, #f87171, #fca5a5)',
      '--kpi-accent-glow': 'rgba(248,113,113,0.25)',
      '--kpi-accent-bg': 'rgba(248,113,113,0.1)',
      '--kpi-accent-color': '#f87171',
    },
  };
  return palette[color] || palette.blue;
}

/**
 * KPICard — Key Performance Indicator display.
 *
 * @param {Object} props
 * @param {React.ElementType} props.icon – Lucide icon component
 * @param {string} props.label – Short KPI label (e.g. "Total Drones")
 * @param {string|number} props.value – Main display value
 * @param {string} props.trend – Trend text (e.g. "+8%")
 * @param {'up'|'down'} props.trendDirection – Trend direction
 * @param {string} [props.subtitle] – Optional subtitle text
 * @param {'blue'|'purple'|'green'|'amber'|'red'} [props.color='blue'] – Accent colour
 * @returns {JSX.Element}
 */
export default function KPICard({
  icon: Icon,
  label,
  value,
  trend,
  trendDirection = 'up',
  subtitle,
  color = 'blue',
}) {
  return (
    <div className="kpi-card" style={accentVars(color)}>
      <div className="kpi-card__header">
        <div className="kpi-card__icon">
          <Icon size={20} />
        </div>
        <span className="kpi-card__label">{label}</span>
      </div>

      <div className="kpi-card__value-row">
        <span className="kpi-card__value">{value}</span>
        {trend && (
          <span
            className={`kpi-card__trend kpi-card__trend--${trendDirection}`}
          >
            {trendDirection === 'up' ? (
              <TrendingUp size={14} />
            ) : (
              <TrendingDown size={14} />
            )}
            {trend}
          </span>
        )}
      </div>

      {subtitle && <p className="kpi-card__subtitle">{subtitle}</p>}
    </div>
  );
}
