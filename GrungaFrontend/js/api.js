export const API_BASE = (window.API_BASE || 'http://127.0.0.1:5000/api');

// ===== Demo user switcher =====
let currentUser = localStorage.getItem("grungaUser") || "demo1";

export function getCurrentUser() {
  return currentUser;
}

export function setCurrentUser(username) {
  currentUser = username || "demo1";
  localStorage.setItem("grungaUser", currentUser);

  // let all pages know the user changed
  window.dispatchEvent(new CustomEvent("user-changed", { detail: currentUser }));
}

// Optional init if you ever want to force-refresh from storage
export function initUserFromStorage() {
  const saved = localStorage.getItem("grungaUser");
  if (saved) {
    currentUser = saved;
  }
}
// run once on module load
initUserFromStorage();
// ==============================

function buildHeaders(hasBody = false) {
  const headers = {
    "X-Demo-User": currentUser
  };
  if (hasBody) {
    headers["Content-Type"] = "application/json";
  }
  return headers;
}

export async function apiGet(path) {
  const r = await fetch(API_BASE + path, {
    method: "GET",
    headers: buildHeaders(false),
    credentials: "omit"
  });
  if (!r.ok) throw new Error(`GET ${path} -> ${r.status}`);
  return r.json();
}

export async function apiPost(path, body) {
  const r = await fetch(API_BASE + path, {
    method: "POST",
    headers: buildHeaders(true),
    body: JSON.stringify(body || {}),
    credentials: "omit"
  });
  if (!r.ok) throw new Error(`POST ${path} -> ${r.status}`);
  return r.json();
}

export async function apiPatch(path, body) {
  const r = await fetch(API_BASE + path, {
    method: "PATCH",
    headers: buildHeaders(true),
    body: JSON.stringify(body || {}),
    credentials: "omit"
  });
  if (!r.ok) throw new Error(`PATCH ${path} -> ${r.status}`);
  return r.json();
}

export async function apiDelete(path) {
  const r = await fetch(API_BASE + path, {
    method: "DELETE",
    headers: buildHeaders(false),
    credentials: "omit"
  });
  if (!r.ok) throw new Error(`DELETE ${path} -> ${r.status}`);
  return r.json();
}
