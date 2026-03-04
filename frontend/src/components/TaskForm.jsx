import { useState } from 'react';
import { createTask } from '../services/taskApi';

const PRIORITIES = ['LOW', 'MEDIUM', 'HIGH'];

export default function TaskForm({ onTaskCreated }) {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [priority, setPriority] = useState('MEDIUM');
  const [dueDate, setDueDate] = useState('');
  const [tags, setTags] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  async function handleSubmit(e) {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const taskData = {
        title: title.trim(),
        description: description.trim() || undefined,
        priority,
        dueDate: dueDate || undefined,
        tags: tags ? tags.split(',').map(t => t.trim()).filter(Boolean) : [],
      };

      const created = await createTask(taskData);
      setTitle('');
      setDescription('');
      setPriority('MEDIUM');
      setDueDate('');
      setTags('');
      if (onTaskCreated) onTaskCreated(created);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="task-form">
      <h3>Create Task</h3>

      {error && <div className="error-message">{error}</div>}

      <div className="form-group">
        <label htmlFor="title">Title *</label>
        <input
          id="title"
          type="text"
          value={title}
          onChange={e => setTitle(e.target.value)}
          placeholder="Task title"
          maxLength={200}
          required
        />
      </div>

      <div className="form-group">
        <label htmlFor="description">Description</label>
        <textarea
          id="description"
          value={description}
          onChange={e => setDescription(e.target.value)}
          placeholder="Task description (optional)"
          maxLength={2000}
          rows={3}
        />
      </div>

      <div className="form-row">
        <div className="form-group">
          <label htmlFor="priority">Priority</label>
          <select id="priority" value={priority} onChange={e => setPriority(e.target.value)}>
            {PRIORITIES.map(p => (
              <option key={p} value={p}>{p}</option>
            ))}
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="dueDate">Due Date</label>
          <input
            id="dueDate"
            type="datetime-local"
            value={dueDate}
            onChange={e => setDueDate(e.target.value)}
          />
        </div>
      </div>

      <div className="form-group">
        <label htmlFor="tags">Tags (comma separated)</label>
        <input
          id="tags"
          type="text"
          value={tags}
          onChange={e => setTags(e.target.value)}
          placeholder="work, urgent, personal"
        />
      </div>

      <button type="submit" disabled={loading || !title.trim()}>
        {loading ? 'Creating...' : 'Create Task'}
      </button>
    </form>
  );
}
