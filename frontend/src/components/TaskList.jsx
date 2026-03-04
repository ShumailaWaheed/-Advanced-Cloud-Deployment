import { useState, useEffect, useCallback } from 'react';
import { getTasks, deleteTask, updateTask } from '../services/taskApi';

const STATUS_LABELS = { TO_DO: 'To Do', IN_PROGRESS: 'In Progress', DONE: 'Done' };
const PRIORITY_COLORS = { HIGH: '#e74c3c', MEDIUM: '#f39c12', LOW: '#27ae60' };

export default function TaskList({ refreshTrigger, onSelectTask }) {
  const [tasks, setTasks] = useState([]);
  const [pagination, setPagination] = useState({ page: 1, limit: 20, total: 0, totalPages: 0 });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const fetchTasks = useCallback(async (page = 1) => {
    setLoading(true);
    setError('');
    try {
      const data = await getTasks({ page, limit: 20 });
      setTasks(data.tasks || []);
      setPagination(data.pagination || { page, limit: 20, total: 0, totalPages: 0 });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchTasks();
  }, [fetchTasks, refreshTrigger]);

  async function handleDelete(taskId) {
    if (!confirm('Delete this task?')) return;
    try {
      await deleteTask(taskId);
      fetchTasks(pagination.page);
    } catch (err) {
      setError(err.message);
    }
  }

  async function handleComplete(taskId) {
    try {
      await updateTask(taskId, { status: 'DONE' });
      fetchTasks(pagination.page);
    } catch (err) {
      setError(err.message);
    }
  }

  if (loading) return <div className="loading">Loading tasks...</div>;
  if (error) return <div className="error-message">{error}</div>;

  return (
    <div className="task-list">
      <h3>Your Tasks ({pagination.total})</h3>

      {tasks.length === 0 ? (
        <p className="empty-state">No tasks yet. Create one above!</p>
      ) : (
        <>
          <ul>
            {tasks.map(task => (
              <li key={task.taskId} className={`task-item status-${task.status.toLowerCase().replace('_', '-')}`}>
                <div className="task-header">
                  <span
                    className="priority-badge"
                    style={{ backgroundColor: PRIORITY_COLORS[task.priority] || '#999' }}
                  >
                    {task.priority}
                  </span>
                  <span className="task-title" onClick={() => onSelectTask && onSelectTask(task)}>
                    {task.title}
                  </span>
                  <span className="task-status">{STATUS_LABELS[task.status] || task.status}</span>
                </div>

                {task.tags && task.tags.length > 0 && (
                  <div className="task-tags">
                    {task.tags.map((tag, i) => (
                      <span key={i} className="tag">{tag}</span>
                    ))}
                  </div>
                )}

                {task.dueDate && (
                  <div className="task-due">Due: {new Date(task.dueDate).toLocaleString()}</div>
                )}

                <div className="task-actions">
                  {task.status !== 'DONE' && (
                    <button className="btn-complete" onClick={() => handleComplete(task.taskId)}>
                      Complete
                    </button>
                  )}
                  <button className="btn-delete" onClick={() => handleDelete(task.taskId)}>
                    Delete
                  </button>
                </div>
              </li>
            ))}
          </ul>

          {pagination.totalPages > 1 && (
            <div className="pagination">
              <button
                disabled={pagination.page <= 1}
                onClick={() => fetchTasks(pagination.page - 1)}
              >
                Previous
              </button>
              <span>Page {pagination.page} of {pagination.totalPages}</span>
              <button
                disabled={pagination.page >= pagination.totalPages}
                onClick={() => fetchTasks(pagination.page + 1)}
              >
                Next
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
}
