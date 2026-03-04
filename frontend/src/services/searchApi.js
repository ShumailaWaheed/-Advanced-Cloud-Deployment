/**
 * Search API client for the todo chatbot frontend.
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
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || 'Request failed');
  return data;
}

export async function searchTasks({ q, tag, priority, status, sortBy, sortOrder, page = 1, limit = 20 } = {}) {
  const params = new URLSearchParams({ page: String(page), limit: String(limit) });
  if (q) params.set('q', q);
  if (tag) params.set('tag', tag);
  if (priority) params.set('priority', priority);
  if (status) params.set('status', status);
  if (sortBy) params.set('sortBy', sortBy);
  if (sortOrder) params.set('sortOrder', sortOrder);

  return request(`/api/v1/tasks/search?${params}`);
}
