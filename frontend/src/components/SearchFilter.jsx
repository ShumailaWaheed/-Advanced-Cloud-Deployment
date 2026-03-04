import { useState } from 'react';

const PRIORITIES = ['', 'LOW', 'MEDIUM', 'HIGH'];
const STATUSES = ['', 'TO_DO', 'IN_PROGRESS', 'DONE'];
const SORT_FIELDS = ['', 'dueDate', 'createdAt', 'priority', 'title'];
const STATUS_LABELS = { '': 'All', TO_DO: 'To Do', IN_PROGRESS: 'In Progress', DONE: 'Done' };

export default function SearchFilter({ onFilterChange }) {
  const [search, setSearch] = useState('');
  const [priority, setPriority] = useState('');
  const [status, setStatus] = useState('');
  const [sortBy, setSortBy] = useState('');
  const [sortOrder, setSortOrder] = useState('asc');

  function handleApply() {
    if (onFilterChange) {
      onFilterChange({
        search: search || undefined,
        priority: priority || undefined,
        status: status || undefined,
        sortBy: sortBy || undefined,
        sortOrder: sortBy ? sortOrder : undefined,
      });
    }
  }

  function handleReset() {
    setSearch('');
    setPriority('');
    setStatus('');
    setSortBy('');
    setSortOrder('asc');
    if (onFilterChange) onFilterChange({});
  }

  return (
    <div className="search-filter">
      <div className="form-row">
        <input
          type="text"
          placeholder="Search tasks..."
          value={search}
          onChange={e => setSearch(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && handleApply()}
        />
        <select value={priority} onChange={e => setPriority(e.target.value)}>
          <option value="">All Priorities</option>
          {PRIORITIES.filter(Boolean).map(p => <option key={p} value={p}>{p}</option>)}
        </select>
        <select value={status} onChange={e => setStatus(e.target.value)}>
          {STATUSES.map(s => <option key={s} value={s}>{STATUS_LABELS[s] || s}</option>)}
        </select>
      </div>
      <div className="form-row">
        <select value={sortBy} onChange={e => setSortBy(e.target.value)}>
          <option value="">No sorting</option>
          {SORT_FIELDS.filter(Boolean).map(f => <option key={f} value={f}>{f}</option>)}
        </select>
        <select value={sortOrder} onChange={e => setSortOrder(e.target.value)} disabled={!sortBy}>
          <option value="asc">Ascending</option>
          <option value="desc">Descending</option>
        </select>
        <button onClick={handleApply}>Apply</button>
        <button className="btn-secondary" onClick={handleReset}>Reset</button>
      </div>
    </div>
  );
}
