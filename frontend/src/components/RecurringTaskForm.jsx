import { useState } from 'react';
import { createRecurringTask } from '../services/recurringTaskApi';

const RECURRENCE_TYPES = ['DAILY', 'WEEKLY', 'MONTHLY', 'YEARLY'];
const DAYS_OF_WEEK = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
const PRIORITIES = ['LOW', 'MEDIUM', 'HIGH'];

export default function RecurringTaskForm({ onCreated }) {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [priority, setPriority] = useState('MEDIUM');
  const [recurrenceType, setRecurrenceType] = useState('WEEKLY');
  const [interval, setInterval] = useState(1);
  const [daysOfWeek, setDaysOfWeek] = useState([]);
  const [startTime, setStartTime] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  function toggleDay(dayIndex) {
    setDaysOfWeek(prev =>
      prev.includes(dayIndex) ? prev.filter(d => d !== dayIndex) : [...prev, dayIndex]
    );
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const pattern = {
        type: recurrenceType,
        interval,
        ...(recurrenceType === 'WEEKLY' && daysOfWeek.length > 0 ? { daysOfWeek } : {}),
        ...(startTime ? { startTime } : {}),
      };
      await createRecurringTask({
        title: title.trim(),
        description: description.trim() || undefined,
        priority,
        pattern,
      });
      setTitle('');
      setDescription('');
      setPriority('MEDIUM');
      setRecurrenceType('WEEKLY');
      setInterval(1);
      setDaysOfWeek([]);
      setStartTime('');
      if (onCreated) onCreated();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="task-form">
      <h3>Create Recurring Task</h3>
      {error && <div className="error-message">{error}</div>}
      <div className="form-group">
        <label>Title *</label>
        <input value={title} onChange={e => setTitle(e.target.value)} maxLength={200} required />
      </div>
      <div className="form-group">
        <label>Description</label>
        <textarea value={description} onChange={e => setDescription(e.target.value)} maxLength={2000} rows={2} />
      </div>
      <div className="form-row">
        <div className="form-group">
          <label>Priority</label>
          <select value={priority} onChange={e => setPriority(e.target.value)}>
            {PRIORITIES.map(p => <option key={p} value={p}>{p}</option>)}
          </select>
        </div>
        <div className="form-group">
          <label>Recurrence</label>
          <select value={recurrenceType} onChange={e => setRecurrenceType(e.target.value)}>
            {RECURRENCE_TYPES.map(t => <option key={t} value={t}>{t}</option>)}
          </select>
        </div>
        <div className="form-group">
          <label>Every N</label>
          <input type="number" value={interval} onChange={e => setInterval(parseInt(e.target.value) || 1)} min={1} />
        </div>
      </div>
      {recurrenceType === 'WEEKLY' && (
        <div className="form-group">
          <label>Days of Week</label>
          <div className="form-row">
            {DAYS_OF_WEEK.map((day, i) => (
              <label key={i} style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                <input type="checkbox" checked={daysOfWeek.includes(i)} onChange={() => toggleDay(i)} />
                {day}
              </label>
            ))}
          </div>
        </div>
      )}
      <div className="form-group">
        <label>Start Time</label>
        <input type="time" value={startTime} onChange={e => setStartTime(e.target.value)} />
      </div>
      <button type="submit" disabled={loading || !title.trim()}>
        {loading ? 'Creating...' : 'Create Recurring Task'}
      </button>
    </form>
  );
}
