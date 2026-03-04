import { useState } from 'react';
import { searchTasks } from '../services/searchApi';

export default function AdvancedFilters({ onResults }) {
  const [query, setQuery] = useState('');
  const [tag, setTag] = useState('');
  const [priority, setPriority] = useState('');
  const [status, setStatus] = useState('');
  const [sortBy, setSortBy] = useState('createdAt');
  const [sortOrder, setSortOrder] = useState('desc');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  async function handleSearch() {
    setError('');
    setLoading(true);
    try {
      const results = await searchTasks({
        q: query || undefined,
        tag: tag || undefined,
        priority: priority || undefined,
        status: status || undefined,
        sortBy,
        sortOrder,
      });
      if (onResults) onResults(results);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="search-filter">
      <h4>Advanced Search</h4>
      {error && <div className="error-message">{error}</div>}
      <div className="form-row">
        <div className="form-group">
          <label>Text Search</label>
          <input value={query} onChange={e => setQuery(e.target.value)} placeholder="Search text..." />
        </div>
        <div className="form-group">
          <label>Tag</label>
          <input value={tag} onChange={e => setTag(e.target.value)} placeholder="Filter by tag" />
        </div>
      </div>
      <div className="form-row">
        <div className="form-group">
          <label>Priority</label>
          <select value={priority} onChange={e => setPriority(e.target.value)}>
            <option value="">All</option>
            <option value="HIGH">High</option>
            <option value="MEDIUM">Medium</option>
            <option value="LOW">Low</option>
          </select>
        </div>
        <div className="form-group">
          <label>Status</label>
          <select value={status} onChange={e => setStatus(e.target.value)}>
            <option value="">All</option>
            <option value="TO_DO">To Do</option>
            <option value="IN_PROGRESS">In Progress</option>
            <option value="DONE">Done</option>
          </select>
        </div>
        <div className="form-group">
          <label>Sort By</label>
          <select value={sortBy} onChange={e => setSortBy(e.target.value)}>
            <option value="createdAt">Created</option>
            <option value="dueDate">Due Date</option>
            <option value="priority">Priority</option>
            <option value="title">Title</option>
          </select>
        </div>
        <div className="form-group">
          <label>Order</label>
          <select value={sortOrder} onChange={e => setSortOrder(e.target.value)}>
            <option value="asc">Asc</option>
            <option value="desc">Desc</option>
          </select>
        </div>
      </div>
      <button onClick={handleSearch} disabled={loading}>{loading ? 'Searching...' : 'Search'}</button>
    </div>
  );
}
