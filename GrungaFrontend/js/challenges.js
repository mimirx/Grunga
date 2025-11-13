const username = 'demo1'; // current logged-in user (change to 'demo2' to test other side)
const knownUsernames = ['demo1', 'demo2'];

let usersByName = {};
let usersById = {};
let currentUser = null;

const toSelect = document.getElementById('challenge-to');
const targetInput = document.getElementById('challenge-target');
const sendBtn = document.getElementById('challenge-send-btn');
const sendMessage = document.getElementById('challenge-send-message');

const incomingListEl = document.getElementById('incoming-list');
const activeListEl = document.getElementById('active-list');
const doneListEl = document.getElementById('done-list');

function formatDate(iso) {
  if (!iso) return '';
  const d = new Date(iso);
  return d.toLocaleString();
}

function otherUserName(ch) {
  if (!currentUser) return '';
  const otherId = (ch.fromUserId === currentUser.userId) ? ch.toUserId : ch.fromUserId;
  const other = usersById[otherId];
  return other ? other.displayName || other.username : `User #${otherId}`;
}

async function loadUsers() {
  for (const name of knownUsernames) {
    try {
      const u = await apiGet(`/users/${name}`);
      usersByName[name] = u;
      usersById[u.userId] = u;
    } catch (err) {
      console.error('Failed to load user', name, err);
    }
  }
  currentUser = usersByName[username];
}

function populateToDropdown() {
  toSelect.innerHTML = '';
  const placeholder = document.createElement('option');
  placeholder.value = '';
  placeholder.textContent = '-- Select friend --';
  toSelect.appendChild(placeholder);

  for (const name of knownUsernames) {
    const u = usersByName[name];
    if (!u || u.username === username) continue;

    const opt = document.createElement('option');
    opt.value = u.userId;
    opt.textContent = u.displayName || u.username;
    toSelect.appendChild(opt);
  }
}

function setListEmpty(listEl, message) {
  listEl.innerHTML = '';
  const p = document.createElement('p');
  p.className = 'muted';
  p.textContent = message;
  listEl.appendChild(p);
}

function renderChallengeCard(challenge, box) {
  const card = document.createElement('div');
  card.className = 'challenge-card';

  const title = document.createElement('div');
  title.className = 'challenge-title';

  const youAreSender = challenge.fromUserId === currentUser.userId;
  const otherName = otherUserName(challenge);
  const direction = youAreSender ? `You → ${otherName}` : `${otherName} → You`;

  title.textContent = `${direction} • ${challenge.target} pts`;
  card.appendChild(title);

  const meta = document.createElement('div');
  meta.className = 'challenge-meta';
  meta.textContent = `Status: ${challenge.status} • Created: ${formatDate(challenge.createdAt)}`;
  card.appendChild(meta);

  const actions = document.createElement('div');
  actions.className = 'challenge-actions';

  // Incoming (PENDING, to current user)
  if (box === 'incoming' && challenge.status === 'PENDING' && challenge.toUserId === currentUser.userId) {
    const acceptBtn = document.createElement('button');
    acceptBtn.className = 'secondary-btn';
    acceptBtn.textContent = 'Accept';
    acceptBtn.onclick = async () => {
      await apiPost(`/challenges/${challenge.challengeId}/accept`, { userId: currentUser.userId });
      await refreshAll();
    };

    const declineBtn = document.createElement('button');
    declineBtn.className = 'danger-btn';
    declineBtn.textContent = 'Decline';
    declineBtn.onclick = async () => {
      await apiPost(`/challenges/${challenge.challengeId}/decline`, { userId: currentUser.userId });
      await refreshAll();
    };

    actions.appendChild(acceptBtn);
    actions.appendChild(declineBtn);
  }

  // Active: either side can complete for now
  if (box === 'active' && challenge.status === 'ACTIVE') {
    const completeBtn = document.createElement('button');
    completeBtn.className = 'primary-btn';
    completeBtn.textContent = 'Mark Complete';
    completeBtn.onclick = async () => {
      await apiPost(`/challenges/${challenge.challengeId}/complete`, { userId: currentUser.userId });
      await refreshAll();
    };
    actions.appendChild(completeBtn);
  }

  if (actions.children.length > 0) {
    card.appendChild(actions);
  }

  return card;
}

async function loadIncoming() {
  const data = await apiGet(`/users/${currentUser.userId}/challenges?box=incoming`);
  incomingListEl.innerHTML = '';

  if (!data || data.length === 0) {
    setListEmpty(incomingListEl, 'No incoming challenges right now.');
    return;
  }

  data.forEach(ch => {
    const card = renderChallengeCard(ch, 'incoming');
    incomingListEl.appendChild(card);
  });
}

async function loadActive() {
  const data = await apiGet(`/users/${currentUser.userId}/challenges?box=active`);
  activeListEl.innerHTML = '';

  if (!data || data.length === 0) {
    setListEmpty(activeListEl, 'You have no active challenges.');
    return;
  }

  data.forEach(ch => {
    const card = renderChallengeCard(ch, 'active');
    activeListEl.appendChild(card);
  });
}

async function loadDone() {
  const data = await apiGet(`/users/${currentUser.userId}/challenges?box=done`);
  doneListEl.innerHTML = '';

  if (!data || data.length === 0) {
    setListEmpty(doneListEl, 'No completed challenges yet.');
    return;
  }

  data.forEach(ch => {
    const card = renderChallengeCard(ch, 'done');
    doneListEl.appendChild(card);
  });
}

async function refreshAll() {
  await Promise.all([loadIncoming(), loadActive(), loadDone()]);
}

async function handleSendClick() {
  sendMessage.textContent = '';
  const toIdRaw = toSelect.value;
  const targetRaw = targetInput.value;

  if (!toIdRaw) {
    sendMessage.textContent = 'Please pick who you want to challenge.';
    return;
  }
  const toUserId = parseInt(toIdRaw, 10);
  const target = parseInt(targetRaw, 10);

  if (Number.isNaN(target) || target <= 0) {
    sendMessage.textContent = 'Please enter a positive target.';
    return;
  }

  try {
    await apiPost(`/users/${currentUser.userId}/challenges`, {
      toUserId,
      kind: 'WORKOUT',
      target
    });
    sendMessage.textContent = 'Challenge sent!';
    await refreshAll();
  } catch (err) {
    console.error('Error sending challenge', err);
    sendMessage.textContent = 'Failed to send challenge.';
  }
}

async function init() {
  try {
    await loadUsers();
    if (!currentUser) {
      console.error('Current user not found; check username in challenges.js');
      return;
    }
    populateToDropdown();
    await refreshAll();
  } catch (err) {
    console.error('Failed to init challenges page', err);
  }
}

document.addEventListener('DOMContentLoaded', () => {
  sendBtn.addEventListener('click', handleSendClick);
  init();
});
