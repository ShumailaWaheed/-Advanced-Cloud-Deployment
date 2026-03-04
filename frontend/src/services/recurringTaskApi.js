/**
 * Recurring Task API client for the todo chatbot frontend.
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || '';

async function request(path, options = {}) {
  const token = typeof window !== 'undefined' ? localStorage.getItem('accessToken') : null;
  const headers = {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...options.headers,
  };

  const res = await fetch(`${API_BASE}${path}`, { ...options, headers });
  if (res.status === 204) return null;
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || 'Request failed');
  return data;
}

export async function getRecurringTasks() {
  return request('/api/v1/recurring-tasks');
}

export async function createRecurringTask(taskData) {
  return request('/api/v1/recurring-tasks', {
    method: 'POST',
    body: JSON.stringify(taskData),
  });
}

export async function updateRecurringTask(taskId, updateData) {
  return request(`/api/v1/recurring-tasks/${taskId}`, {
    method: 'PUT',
    body: JSON.stringify(updateData),
  });
}

export async function deleteRecurringTask(taskId) {
  return request(`/api/v1/recurring-tasks/${taskId}`, { method: 'DELETE' });
}
