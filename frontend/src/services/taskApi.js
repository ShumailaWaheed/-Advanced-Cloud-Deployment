/**
 * Task Management API client for the todo chatbot frontend.
 * Communicates with the backend via Dapr service invocation.
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || '';

async function request(path, options = {}) {
  const token = typeof window !== 'undefined' ? localStorage.getItem('accessToken') : null;
  const headers = {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...options.headers,
  };

  let res;
  try {
    res = await fetch(`${API_BASE}${path}`, { ...options, headers });
  } catch (err) {
    throw new Error('Network error: backend is not reachable');
  }

  if (res.status === 401) {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('accessToken');
      localStorage.removeItem('refreshToken');
      window.location.href = '/login';
    }
    throw new Error('Unauthorized');
  }

  if (res.status === 204) return null;

  const text = await res.text();
  let data;
  try {
    data = JSON.parse(text);
  } catch {
    throw new Error(`Server error: ${text.slice(0, 100)}`);
  }
  if (!res.ok) throw new Error(data.detail || 'Request failed');
  return data;
}

// --- Task API ---

export async function getTasks({ page = 1, limit = 20, status, priority, search, sortBy, sortOrder } = {}) {
  const params = new URLSearchParams({ page: String(page), limit: String(limit) });
  if (status) params.set('status', status);
  if (priority) params.set('priority', priority);
  if (search) params.set('search', search);
  if (sortBy) params.set('sortBy', sortBy);
  if (sortOrder) params.set('sortOrder', sortOrder);

  return request(`/api/v1/tasks?${params}`);
}

export async function getTask(taskId) {
  return request(`/api/v1/tasks/${taskId}`);
}

export async function createTask(taskData) {
  return request('/api/v1/tasks', {
    method: 'POST',
    body: JSON.stringify(taskData),
  });
}

export async function updateTask(taskId, updateData) {
  return request(`/api/v1/tasks/${taskId}`, {
    method: 'PUT',
    body: JSON.stringify(updateData),
  });
}

export async function deleteTask(taskId) {
  return request(`/api/v1/tasks/${taskId}`, { method: 'DELETE' });
}

// --- Chat API ---

export async function sendChatMessage(message) {
  return request('/api/v1/chat/process', {
    method: 'POST',
    body: JSON.stringify({ message }),
  });
}
