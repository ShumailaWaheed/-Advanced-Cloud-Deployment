/**
 * Authentication API client for the todo chatbot frontend.
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || '';

async function authRequest(path, options = {}) {
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

export async function register(username, email, password) {
  return authRequest('/api/v1/auth/register', {
    method: 'POST',
    body: JSON.stringify({ username, email, password }),
  });
}

export async function login(email, password) {
  const data = await authRequest('/api/v1/auth/login', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  });

  if (typeof window !== 'undefined' && data.accessToken) {
    localStorage.setItem('accessToken', data.accessToken);
    localStorage.setItem('refreshToken', data.refreshToken);
  }

  return data;
}

export async function getProfile() {
  return authRequest('/api/v1/auth/profile');
}

export async function updateProfile(updateData) {
  return authRequest('/api/v1/auth/profile', {
    method: 'PUT',
    body: JSON.stringify(updateData),
  });
}

export function logout() {
  if (typeof window !== 'undefined') {
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    window.location.href = '/login';
  }
}

export function isAuthenticated() {
  if (typeof window === 'undefined') return false;
  return !!localStorage.getItem('accessToken');
}
