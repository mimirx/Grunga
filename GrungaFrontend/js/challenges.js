import { apiGet, apiPost, getCurrentUser } from "./api.js";

let currentUserId = null;

const toSelect = document.getElementById("challenge-to");
const exerciseSelect = document.getElementById("exercise-type");
const setsInput = document.getElementById("challenge-sets");
const repsInput = document.getElementById("challenge-reps");
const sendBtn = document.getElementById("challenge-send-btn");
const sendMsg = document.getElementById("challenge-send-message");

const incomingListEl = document.getElementById("incoming-list");
const activeListEl = document.getElementById("active-list");
const doneListEl = document.getElementById("done-list");


// -------------------------------------------------------
// Helper
// -------------------------------------------------------
function formatDate(iso) {
  if (!iso) return "";
  const d = new Date(iso);
  return d.toLocaleString();
}

function buildEmpty(listEl, msg) {
  listEl.innerHTML = "";
  const p = document.createElement("p");
  p.className = "muted";
  p.textContent = msg;
  listEl.appendChild(p);
}


// -------------------------------------------------------
// Load Current User (from api.js which uses X-Demo-User)
// -------------------------------------------------------
async function loadCurrentUser() {
  const username = getCurrentUser();
  const user = await apiGet(`/users/${username}`);
  currentUserId = user.userId;
}


// -------------------------------------------------------
// Load FRIENDS for dropdown
// -------------------------------------------------------
async function loadFriendsDropdown() {
  toSelect.innerHTML = "";

  const placeholder = document.createElement("option");
  placeholder.value = "";
  placeholder.textContent = "-- Select friend --";
  toSelect.appendChild(placeholder);

  const friendsData = await apiGet("/friends/");
  const friends = friendsData.friends || [];

  friends.forEach((f) => {
    const opt = document.createElement("option");
    opt.value = f.userId;
    opt.textContent = f.displayName || f.username;
    toSelect.appendChild(opt);
  });
}

// -------------------------------------------------------
// RENDER CHALLENGE CARD
// -------------------------------------------------------
function renderChallengeCard(ch, mode) {
  const card = document.createElement("div");
  card.className = "challenge-card";

  const title = document.createElement("div");
  title.className = "challenge-title";

  const isSender = (ch.fromUserId === currentUserId);

  const direction = isSender
    ? `You → Friend`
    : `Friend → You`;

  title.textContent = `${direction} • ${ch.exerciseType} • ${ch.sets} × ${ch.reps} = ${ch.points} pts`;
  card.appendChild(title);

  const meta = document.createElement("div");
  meta.className = "challenge-meta";
  meta.textContent = `Status: ${ch.status} • Created: ${formatDate(ch.createdAt)} • Due: ${formatDate(ch.dueAt)}`;
  card.appendChild(meta);

  // ACTIONS
  const actions = document.createElement("div");
  actions.className = "challenge-actions";

  // Incoming → Accept / Decline
  if (mode === "incoming" && ch.toUserId === currentUserId) {
    const acceptBtn = document.createElement("button");
    acceptBtn.className = "secondary-btn";
    acceptBtn.textContent = "Accept";
    acceptBtn.onclick = async () => {
      await apiPost(`/challenges/${ch.challengeId}/accept`, {});
      await refreshAll();
    };

    const declineBtn = document.createElement("button");
    declineBtn.className = "danger-btn";
    declineBtn.textContent = "Decline";
    declineBtn.onclick = async () => {
      await apiPost(`/challenges/${ch.challengeId}/decline`, {});
      await refreshAll();
    };

    actions.appendChild(acceptBtn);
    actions.appendChild(declineBtn);
  }

  // Active → Only receiver can complete
  if (mode === "active" && ch.status === "ACTIVE" && ch.toUserId === currentUserId) {
    const completeBtn = document.createElement("button");
    completeBtn.className = "primary-btn";
    completeBtn.textContent = "Mark Complete";
    completeBtn.onclick = async () => {
      await apiPost(`/challenges/${ch.challengeId}/complete`, {});
      await refreshAll();
    };
    actions.appendChild(completeBtn);
  }

  if (actions.children.length > 0) {
    card.appendChild(actions);
  }

  return card;
}


// -------------------------------------------------------
// LOAD BOXES
// -------------------------------------------------------
async function loadIncoming() {
  const data = await apiGet("/challenges/incoming");
  incomingListEl.innerHTML = "";

  if (!data || data.length === 0) {
    buildEmpty(incomingListEl, "No incoming challenges.");
    return;
  }

  data.forEach((ch) => {
    incomingListEl.appendChild(renderChallengeCard(ch, "incoming"));
  });
}

async function loadActive() {
  const data = await apiGet("/challenges/active");
  activeListEl.innerHTML = "";

  if (!data || data.length === 0) {
    buildEmpty(activeListEl, "You have no active challenges.");
    return;
  }

  data.forEach((ch) => {
    activeListEl.appendChild(renderChallengeCard(ch, "active"));
  });
}

async function loadDone() {
  const data = await apiGet("/challenges/completed");
  doneListEl.innerHTML = "";

  if (!data || data.length === 0) {
    buildEmpty(doneListEl, "No completed challenges yet.");
    return;
  }

  data.forEach((ch) => {
    doneListEl.appendChild(renderChallengeCard(ch, "done"));
  });
}


async function refreshAll() {
  await Promise.all([
    loadIncoming(),
    loadActive(),
    loadDone(),
  ]);
}


// -------------------------------------------------------
// SEND CHALLENGE
// -------------------------------------------------------
async function onSendClick() {
  sendMsg.textContent = "";

  const toUserId = parseInt(toSelect.value);
  const exercise = exerciseSelect.value.trim();
  const sets = parseInt(setsInput.value);
  const reps = parseInt(repsInput.value);

  if (!toUserId) {
    sendMsg.textContent = "Select someone to challenge.";
    return;
  }
  if (!exercise) {
    sendMsg.textContent = "Select an exercise.";
    return;
  }
  if (sets <= 0 || reps <= 0) {
    sendMsg.textContent = "Sets/Reps must be positive numbers.";
    return;
  }

  try {
    const result = await apiPost("/challenges/send", {
      toUserId,
      exerciseType: exercise,
      sets,
      reps,
    });

    if (!result.ok) {
      sendMsg.textContent = result.error || "Failed to send challenge.";
      return;
    }

    sendMsg.textContent = "Challenge sent!";
    await refreshAll();

  } catch (err) {
    console.error("Error sending challenge:", err);
    sendMsg.textContent = "Error sending challenge.";
  }
}


// -------------------------------------------------------
// INIT
// -------------------------------------------------------
async function init() {
  try {
    await loadCurrentUser();
    await loadFriendsDropdown();
    await refreshAll();
  } catch (err) {
    console.error("Init failed:", err);
  }
}

document.addEventListener("DOMContentLoaded", () => {
  sendBtn.addEventListener("click", onSendClick);
  init();
});
