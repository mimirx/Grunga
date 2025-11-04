const apiBase = 'http://127.0.0.1:5000/api';

async function apiGet(path) {
  const r = await fetch(`${apiBase}${path}`);
  if (!r.ok) throw new Error('request failed');
  return r.json();
}

async function apiPost(path, body) {
  const r = await fetch(`${apiBase}${path}`, {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify(body)
  });
  if (!r.ok) throw new Error('request failed');
  return r.json();
}
