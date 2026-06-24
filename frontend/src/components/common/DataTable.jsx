/**
 * @file DataTable.jsx
 * @description Reusable sortable data table with loading skeleton and empty
 * state. Accepts a column definition array and data rows.
 */

import { useState, useMemo } from 'react';
import { ChevronUp, ChevronDown, Inbox } from 'lucide-react';
import './DataTable.css';

/**
 * DataTable — Reusable table component.
 *
 * @param {Object} props
 * @param {Array<{key: string, label: string, render?: (value: any, row: Object) => JSX.Element}>} props.columns
 * @param {Array<Object>} props.data
 * @param {(row: Object) => void} [props.onRowClick]
 * @param {boolean} [props.loading=false]
 * @returns {JSX.Element}
 */
export default function DataTable({ columns, data = [], onRowClick, loading = false }) {
  const [sortKey, setSortKey] = useState(null);
  const [sortDir, setSortDir] = useState('asc');

  /** Toggle sort or flip direction */
  const handleSort = (key) => {
    if (sortKey === key) {
      setSortDir((d) => (d === 'asc' ? 'desc' : 'asc'));
    } else {
      setSortKey(key);
      setSortDir('asc');
    }
  };

  /** Sorted data */
  const sorted = useMemo(() => {
    if (!sortKey) return data;
    return [...data].sort((a, b) => {
      const aVal = a[sortKey];
      const bVal = b[sortKey];
      if (aVal == null) return 1;
      if (bVal == null) return -1;
      const cmp = typeof aVal === 'number' ? aVal - bVal : String(aVal).localeCompare(String(bVal));
      return sortDir === 'asc' ? cmp : -cmp;
    });
  }, [data, sortKey, sortDir]);

  /* ---- Loading state ---- */
  if (loading) {
    return (
      <div className="data-table-wrap">
        <div className="data-table__skeleton">
          {Array.from({ length: 5 }).map((_, i) => (
            <div key={i} className="data-table__skeleton-row" style={{ width: `${80 - i * 5}%` }} />
          ))}
        </div>
      </div>
    );
  }

  /* ---- Empty state ---- */
  if (!data.length) {
    return (
      <div className="data-table-wrap">
        <div className="data-table__empty">
          <Inbox size={48} className="data-table__empty-icon" />
          <p className="data-table__empty-text">No data available</p>
        </div>
      </div>
    );
  }

  return (
    <div className="data-table-wrap">
      <table className="data-table">
        <thead>
          <tr>
            {columns.map((col) => (
              <th key={col.key} onClick={() => handleSort(col.key)}>
                {col.label}
                {sortKey === col.key && (
                  <span className="data-table__sort-icon">
                    {sortDir === 'asc' ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
                  </span>
                )}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {sorted.map((row, idx) => (
            <tr
              key={row.id ?? idx}
              className={onRowClick ? 'clickable' : ''}
              onClick={() => onRowClick?.(row)}
            >
              {columns.map((col) => (
                <td key={col.key}>
                  {col.render ? col.render(row[col.key], row) : row[col.key]}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
