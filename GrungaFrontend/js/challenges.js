import { apiGet, apiPost } from "./api.js";

const me = "demo1"; // or await apiGet('/users/demo1') if you prefer

const el = (id) => document.getElementById(id);
const incomingList = el("incoming-list");
const activeList   = el("active-list");
const doneList     = el("done-list");

el("btn-create").addEventListener("click", async () => {
  const friend = el("friend-username").value.trim();
  const kind   = el("challenge-type").value;
  const target = Number(el("challenge-target").value);
  const msg    = el("create-msg");

  if (!friend || !target || target <= 0) {
    msg.textContent = "Please provide a friend and a positive target.";
    return;
  }
  try {
    // TODO: replace with your real endpoint
    // await apiPost(`/users/${me}/challenges`, { friend, kind, target });
    console.log("create challenge →", { friend, kind, target });
    msg.textContent = "Challenge sent!";
    msg.classList.add("success");
    await loadAll();
  } catch (e) {
    console.error(e);
    msg.textContent = "Could not create challenge.";
    msg.classList.remove("success");
  }
});

async function loadAll() {
  // TODO: swap console mocks for real calls
  // const incoming = await apiGet(`/users/${me}/challenges?box=incoming`);
  // const active   = await apiGet(`/users/${me}/challenges?box=active`);
  // const done     = await apiGet(`/users/${me}/challenges?box=done`);

  const incoming = [
    { id: 101, from: "serhii", kind: "pushups", target: 100 },
  ];
  const active = [
    { id: 201, with: "serhii", kind: "run", target: 60, progress: 25 },
  ];
  const done = [
    { id: 301, with: "alex", kind: "crunches", target: 200, result: "won" },
  ];

  renderIncoming(incoming);
  renderActive(active);
  renderDone(done);
}

function li(html) {
  const li = document.createElement("li");
  li.className = "list-item";
  li.innerHTML = html;
  return li;
}

function renderIncoming(items) {
  incomingList.innerHTML = "";
  items.forEach(c => {
    const item = li(`
      <div><b>${c.from}</b> challenged you: <i>${c.kind}</i> — target <b>${c.target}</b></div>
      <div class="row">
        <button class="btn btn-sm" data-accept="${c.id}">Accept</button>
        <button class="btn btn-sm btn-ghost" data-decline="${c.id}">Decline</button>
      </div>
    `);
    item.querySelector("[data-accept]").onclick  = () => accept(c.id);
    item.querySelector("[data-decline]").onclick = () => decline(c.id);
    incomingList.appendChild(item);
  });
}

function renderActive(items) {
  activeList.innerHTML = "";
  items.forEach(c => {
    const pct = Math.min(100, Math.round((c.progress || 0) / c.target * 100));
    const item = li(`
      <div><b>${c.with}</b> — ${c.kind} ${c.progress || 0}/${c.target}</div>
      <progress max="100" value="${pct}"></progress>
      <div class="row">
        <button class="btn btn-sm" data-nudge="${c.id}">Nudge</button>
        <button class="btn btn-sm btn-ghost" data-forfeit="${c.id}">Forfeit</button>
      </div>
    `);
    item.querySelector("[data-nudge]").onclick   = () => nudge(c.id);
    item.querySelector("[data-forfeit]").onclick = () => forfeit(c.id);
    activeList.appendChild(item);
  });
}

function renderDone(items) {
  doneList.innerHTML = "";
  items.forEach(c => {
    const item = li(`<div><b>${c.with}</b> — ${c.kind} (${c.result}) — target ${c.target}</div>`);
    doneList.appendChild(item);
  });
}

// TODO: wire to endpoints
async function accept(id){ console.log("accept", id); await loadAll(); }
async function decline(id){ console.log("decline", id); await loadAll(); }
async function nudge(id){ console.log("nudge", id); }
async function forfeit(id){ console.log("forfeit", id); await loadAll(); }

window.addEventListener("DOMContentLoaded", loadAll);
