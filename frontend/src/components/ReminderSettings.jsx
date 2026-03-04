import { useState } from 'react';

export default function ReminderSettings({ task, onClose }) {
  const [scheduledTime, setScheduledTime] = useState('');
  const [method, setMethod] = useState('CHAT');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  async function handleSubmit(e) {
    e.preventDefault();
    setError('');
    setSuccess('');
    setLoading(true);

    try {
      const token = typeof window !== 'undefined' ? localStorage.getItem('accessToken') : null;
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || ''}/api/v1/chat/process`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({
          message: `schedule reminder for task ${task.taskId} at ${scheduledTime}`,
        }),
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Failed to schedule reminder');

      setSuccess('Reminder scheduled successfully.');
      setScheduledTime('');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="task-detail">
      <div className="detail-header">
        <h3>Schedule Reminder</h3>
        <button className="btn-close" onClick={onClose}>Close</button>
      </div>
      <p>Task: {task.title}</p>
      {error && <div className="error-message">{error}</div>}
      {success && <div className="success-message">{success}</div>}
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Reminder Time</label>
          <input type="datetime-local" value={scheduledTime} onChange={e => setScheduledTime(e.target.value)} required />
        </div>
        <div className="form-group">
          <label>Method</label>
          <select value={method} onChange={e => setMethod(e.target.value)}>
            <option value="CHAT">Chat</option>
            <option value="EMAIL">Email</option>
            <option value="PUSH">Push Notification</option>
          </select>
        </div>
        <button type="submit" disabled={loading}>{loading ? 'Scheduling...' : 'Schedule Reminder'}</button>
      </form>
    </div>
  );
}
