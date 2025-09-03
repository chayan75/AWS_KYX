export async function apiFetch(url, options = {}) {
  const token = localStorage.getItem('authToken');
  const headers = {
    ...(options.headers || {}),
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
  const response = await fetch(url, { ...options, headers });
  if (!response.ok) {
    // Optionally handle 401/403 here (e.g., logout)
    throw new Error(`API error: ${response.status}`);
  }
  return response.json();
} 