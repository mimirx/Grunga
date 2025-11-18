import { apiGet, apiPost, getCurrentUser, setCurrentUser } from "./api.js";

const searchInput = document.getElementById("friend-search");
const searchResults = document.getElementById("friend-search-results");
const messageEl = document.getElementById("friend-message");

const incomingList = document.getElementById("incoming-list");
const outgoingList = document.getElementById("outgoing-list");
const friendsList = document.getElementById("friends-list");

function setMessage(text, isError = false) {
  if (!messageEl) return;
  messageEl.textContent = text || "";
  messageEl.style.color = isError ? "#ff6b6b" : "#00ffae";
}

function clearSearchResults() {
  if (searchResults) searchResults.innerHTML = "";
  setMessage("");
}

function makeButton(label, handler, extraClass = "") {
  const btn = document.createElement("button");
  btn.textContent = label;
  btn.className = `btn-small ${extraClass}`.trim();
  btn.addEventListener("click", handler);
  return btn;
}

// ---------- USER SWITCHER ----------
function setupUserSwitcher() {
  const btn1 = document.querySelector("[data-user='demo1']");
  const btn2 = document.querySelector("[data-user='demo2']");
  if (!btn1 || !btn2) return;

  function updateActiveButtons() {
    const u = getCurrentUser();
    btn1.classList.toggle("active", u === "demo1");
    btn2.classList.toggle("active", u === "demo2");
  }

  btn1.addEventListener("click", async () => {
    setCurrentUser("demo1");
    updateActiveButtons();
    await loadFriendsData();
  });

  btn2.addEventListener("click", async () => {
    setCurrentUser("demo2");
    updateActiveButtons();
    await loadFriendsData();
  });

  updateActiveButtons();
}

// react if another page changed the user
window.addEventListener("user-changed", () => {
  loadFriendsData();
});
// -----------------------------------

async function handleSearchInput(e) {
  const q = e.target.value.trim();
  clearSearchResults();

  if (q.length < 2) {
    return; // don’t spam API on 1-letter searches
  }

  try {
    setMessage("Searching…");
    const results = await apiGet(
      `/friends/users/search?q=${encodeURIComponent(q)}`
    );

    if (!results || results.length === 0) {
      setMessage("No users found.");
      return;
    }

    setMessage("");
    results.forEach((user) => {
      const row = document.createElement("div");
      row.className = "friend-search-row";

      const nameSpan = document.createElement("span");
      nameSpan.textContent = user.displayName
        ? `${user.displayName} (@${user.username})`
        : user.username;

      const addBtn = makeButton(
        "Add",
        () => sendFriendRequest(user.userId),
        "btn-primary"
      );

      row.appendChild(nameSpan);
      row.appendChild(addBtn);
      searchResults.appendChild(row);
    });
  } catch (err) {
    console.error("Search failed:", err);
    setMessage("Error while searching. Check console.", true);
  }
}

async function sendFriendRequest(friendId) {
  try {
    const res = await apiPost("/friends/requests", { friendId });
    console.log("sendFriendRequest result:", res);
    if (!res.ok) {
      setMessage(res.error || "Could not send request.", true);
    } else {
      setMessage("Friend request sent!");
    }
    clearSearchResults();
    await loadFriendsData();
  } catch (err) {
    console.error("sendFriendRequest failed:", err);
    setMessage("Could not send request.", true);
  }
}

function renderList(listEl, items, buildRow) {
  if (!listEl) return;
  listEl.innerHTML = "";
  if (!items || items.length === 0) {
    const li = document.createElement("li");
    li.className = "empty-row";
    li.textContent = "Nothing here yet.";
    listEl.appendChild(li);
    return;
  }
  items.forEach((item) => listEl.appendChild(buildRow(item)));
}

async function respondToRequest(otherUserId, action) {
  try {
    const res = await apiPost("/friends/requests/respond", {
      otherUserId,
      action, // "accept" or "decline"
    });
    console.log("respondToRequest result:", res);
    if (!res.ok) {
      setMessage(res.error || "Could not update request.", true);
    } else {
      setMessage(
        action === "accept" ? "Friend request accepted." : "Request declined."
      );
    }
    await loadFriendsData();
  } catch (err) {
    console.error("respondToRequest failed:", err);
    setMessage("Could not update request.", true);
  }
}

async function loadFriendsData() {
  try {
    console.log("Loading friends data…");
    const data = await apiGet("/friends");
    console.log("Friends payload:", data);

    const { incoming, outgoing, friends } = data;

    // incoming: [{ otherUserId, username, displayName }]
    renderList(incomingList, incoming, (req) => {
      const li = document.createElement("li");
      li.className = "friend-row";

      const span = document.createElement("span");
      span.textContent = req.displayName
        ? `${req.displayName} (@${req.username})`
        : req.username;

      const acceptBtn = makeButton(
        "✓",
        () => respondToRequest(req.otherUserId, "accept"),
        "btn-accept"
      );
      const denyBtn = makeButton(
        "✕",
        () => respondToRequest(req.otherUserId, "decline"),
        "btn-deny"
      );

      li.appendChild(span);
      li.appendChild(acceptBtn);
      li.appendChild(denyBtn);
      return li;
    });

    // outgoing: [{ otherUserId, username, displayName }]
    renderList(outgoingList, outgoing, (req) => {
      const li = document.createElement("li");
      li.className = "friend-row";

      const span = document.createElement("span");
      span.textContent = req.displayName
        ? `${req.displayName} (@${req.username})`
        : req.username;

      const status = document.createElement("span");
      status.textContent = "Pending";
      status.className = "friend-status";

      li.appendChild(span);
      li.appendChild(status);
      return li;
    });

    // friends: [{ userId, username, displayName }]
    renderList(friendsList, friends, (f) => {
      const li = document.createElement("li");
      li.className = "friend-row";

      const span = document.createElement("span");
      span.textContent = f.displayName
        ? `${f.displayName} (@${f.username})`
        : f.username;

      li.appendChild(span);
      return li;
    });
  } catch (err) {
    console.error("loadFriendsData failed:", err);
    setMessage("Could not load friends data.", true);
  }
}

window.addEventListener("DOMContentLoaded", () => {
  console.log("Friends page loaded");
  setupUserSwitcher();

  if (searchInput) {
    searchInput.addEventListener("input", handleSearchInput);
  }

  loadFriendsData();
});
