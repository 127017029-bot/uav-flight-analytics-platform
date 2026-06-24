/**
 * @file StatusBadge.jsx
 * @description Coloured status badge with glowing dot indicator.
 * Supports many status variants (active, maintenance, warning, critical, etc.).
 */

import './StatusBadge.css';

/**
 * StatusBadge — Displays a coloured dot + text label.
 *
 * @param {Object} props
 * @param {string} props.status – Status key (e.g. 'active', 'warning', 'critical')
 * @param {'sm'|'md'|'lg'} [props.size='md'] – Badge size variant
 * @returns {JSX.Element}
 */
export default function StatusBadge({ status, size = 'md' }) {
  const slug = status.toLowerCase().replace(/\s+/g, '-');
  const sizeClass = size !== 'md' ? ` status-badge--${size}` : '';

  return (
    <span className={`status-badge status-badge--${slug}${sizeClass}`}>
      <span className="status-badge__dot" />
      {status}
    </span>
  );
}
