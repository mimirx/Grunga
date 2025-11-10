export const API_BASE = (window.API_BASE || 'http://127.0.0.1:5000/api');

export async function apiGet(path) {
  const r = await fetch(API_BASE + path, { credentials: 'omit' });
  if (!r.ok) throw new Error(`GET ${path} -> ${r.status}`);
  return r.json();
}

export async function apiPost(path, body) {
  const r = await fetch(API_BASE + path, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body || {})
  });
  if (!r.ok) throw new Error(`POST ${path} -> ${r.status}`);
  return r.json();
}

export async function apiPatch(path, body) {
  const r = await fetch(API_BASE + path, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body || {})
  });
  if (!r.ok) throw new Error(`PATCH ${path} -> ${r.status}`);
  return r.json();
}

export async function apiDelete(path) {
  const r = await fetch(API_BASE + path, { method: 'DELETE' });
  if (!r.ok) throw new Error(`DELETE ${path} -> ${r.status}`);
  return r.json();
}
