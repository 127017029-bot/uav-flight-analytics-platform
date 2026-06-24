/**
 * @file LoadingSpinner.jsx
 * @description CSS-animated loading spinner using the accent colour
 * from the design system. Optionally accepts a size prop.
 */

/**
 * LoadingSpinner — Circular spinner animation.
 *
 * @param {Object} [props]
 * @param {number} [props.size=32] – Diameter in pixels
 * @returns {JSX.Element}
 */
export default function LoadingSpinner({ size = 32 }) {
  const style = {
    width: size,
    height: size,
    border: `3px solid var(--color-border)`,
    borderTopColor: 'var(--color-accent)',
    borderRadius: '50%',
    animation: 'spin 0.8s linear infinite',
    flexShrink: 0,
  };

  return <div style={style} role="status" aria-label="Loading" />;
}
