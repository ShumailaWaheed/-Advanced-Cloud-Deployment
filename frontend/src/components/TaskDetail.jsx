import { useState } from 'react';
import { updateTask } from '../services/taskApi';

const PRIORITIES = ['LOW', 'MEDIUM', 'HIGH'];
const STATUSES = ['TO_DO', 'IN_PROGRESS', 'DONE'];
const STATUS_LABELS = { TO_DO: 'To Do', IN_PROGRESS: 'In Progress', DONE: 'Done' };

export default function TaskDetail({ task, onClose, onUpdated }) {
  const [editing, setEditing] = useState(false);
  const [title, setTitle] = useState(task.title);
  const [description, setDescription] = useState(task.description || '');
  const [priority, setPriority] = useState(task.priority);
  const [status, setStatus] = useState(task.status);
  const [dueDate, setDueDate] = useState(task.dueDate ? task.dueDate.slice(0, 16) : '');
  const [tags, setTags] = useState((task.tags || []).join(', '));
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  async function handleSave() {
    setError('');
    setLoading(true);
    try {
      const updateData = {
        title: title.trim(),
        description: description.trim() || undefined,
        priority,
        status,
        dueDate: dueDate || undefined,
        tags: tags ? tags.split(',').map(t => t.trim()).filter(Boolean) : [],
      };
      const updated = await updateTask(task.taskId, updateData);
      setEditing(false);
      if (onUpdated) onUpdated(updated);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="task-detail">
      <div className="detail-header">
        <h3>{editing ? 'Edit Task' : 'Task Details'}</h3>
        <button className="btn-close" onClick={onClose}>Close</button>
      </div>

      {error && <div className="error-message">{error}</div>}

      {editing ? (
        <div className="edit-form">
          <div className="form-group">
            <label>Title</label>
            <input value={title} onChange={e => setTitle(e.target.value)} maxLength={200} />
          </div>
          <div className="form-group">
            <label>Description</label>
            <textarea value={description} onChange={e => setDescription(e.target.value)} maxLength={2000} rows={3} />
          </div>
          <div className="form-row">
            <div className="form-group">
              <label>Priority</label>
              <select value={priority} onChange={e => setPriority(e.target.value)}>
                {PRIORITIES.map(p => <option key={p} value={p}>{p}</option>)}
              </select>
            </div>
            <div className="form-group">
              <label>Status</label>
              <select value={status} onChange={e => setStatus(e.target.value)}>
                {STATUSES.map(s => <option key={s} value={s}>{STATUS_LABELS[s]}</option>)}
              </select>
            </div>
          </div>
          <div className="form-group">
            <label>Due Date</label>
            <input type="datetime-local" value={dueDate} onChange={e => setDueDate(e.target.value)} />
          </div>
          <div className="form-group">
            <label>Tags (comma separated)</label>
            <input value={tags} onChange={e => setTags(e.target.value)} />
          </div>
          <div className="button-group">
            <button onClick={handleSave} disabled={loading}>{loading ? 'Saving...' : 'Save'}</button>
            <button className="btn-secondary" onClick={() => setEditing(false)}>Cancel</button>
          </div>
        </div>
      ) : (
        <div className="detail-view">
          <p><strong>Title:</strong> {task.title}</p>
          <p><strong>Status:</strong> {STATUS_LABELS[task.status] || task.status}</p>
          <p><strong>Priority:</strong> {task.priority}</p>
          {task.description && <p><strong>Description:</strong> {task.description}</p>}
          {task.dueDate && <p><strong>Due:</strong> {new Date(task.dueDate).toLocaleString()}</p>}
          {task.tags && task.tags.length > 0 && (
            <p><strong>Tags:</strong> {task.tags.join(', ')}</p>
          )}
          <p><strong>Created:</strong> {new Date(task.createdAt).toLocaleString()}</p>
          <p><strong>Updated:</strong> {new Date(task.updatedAt).toLocaleString()}</p>
          {task.completedAt && <p><strong>Completed:</strong> {new Date(task.completedAt).toLocaleString()}</p>}
          <p><strong>ID:</strong> {task.taskId}</p>
          <button onClick={() => setEditing(true)}>Edit Task</button>
        </div>
      )}
    </div>
  );
}
