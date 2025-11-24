import { apiGet, apiPost, getCurrentUser, setCurrentUser } from "./api.js";

document.addEventListener("DOMContentLoaded", async () => {
  const form = document.getElementById("workout-form");
  const typeSelect = document.getElementById("type");
  const durationSection = document.getElementById("duration-section");
  const repsSection = document.getElementById("reps-section");
  const list = document.querySelector("#workout-list ul");

  let userId = null;

  const cardio = new Set(["run", "bike", "walk", "swim"]);
  const strength = new Set(["pushups", "squats", "lunges", "crunches"]);

  // ======================================================
  // ⭐ FIXED DATE FORMATTER (supports legacy + new dates)
  // ======================================================
  function formatDate(dateString) {
    if (!dateString) return "Unknown Date";

    // Case 1: New backend DATE format "YYYY-MM-DD"
    if (/^\d{4}-\d{2}-\d{2}$/.test(dateString)) {
      const [year, month, day] = dateString.split("-");
      const d = new Date(Number(year), Number(month) - 1, Number(day));

      return d.toLocaleDateString("en-US", {
        weekday: "short",
        month: "short",
        day: "numeric",
        year: "numeric"
      });
    }

    // Case 2: Old GMT-style dates "Mon, 24 Nov 2025 00:00:00 GMT"
    const legacyDate = new Date(dateString);
    if (!isNaN(legacyDate.getTime())) {
      return legacyDate.toLocaleDateString("en-US", {
        weekday: "short",
        month: "short",
        day: "numeric",
        year: "numeric"
      });
    }

    return "Unknown Date";
  }

  // --------------------------------------------------
  // User switcher (demo1 / demo2)
  // --------------------------------------------------
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
      await reloadAllForCurrentUser();
    });

    btn2.addEventListener("click", async () => {
      setCurrentUser("demo2");
      updateActiveButtons();
      await reloadAllForCurrentUser();
    });

    updateActiveButtons();
  }

  window.addEventListener("user-changed", () => reloadAllForCurrentUser());

  // ======================================================
  // ⭐ FIXED renderRows — now uses formatDate()
  // ======================================================
  function renderRows(rows) {
    list.innerHTML = "";

    (rows || []).forEach((r) => {
      const niceDate = formatDate(r.workoutDate);

      const isCardio = cardio.has(r.workoutType);
      const text = isCardio
        ? `${r.workoutType} — ${r.reps} min (${niceDate})`
        : `${r.workoutType} — ${r.sets} x ${r.reps} (${niceDate})`;

      const li = document.createElement("li");
      li.classList.add("workout-item");

      const span = document.createElement("span");
      span.textContent = text;

      const del = document.createElement("button");
      del.classList.add("delete-btn");
      del.innerHTML = "✖";

      del.addEventListener("click", async () => {
        if (!confirm("Delete this workout?")) return;
        if (!userId) await loadUser();

        await apiPost(`/users/${userId}/workouts/delete`, {
          workoutId: r.workoutId,
        });

        await loadWorkouts();
        await refreshTotalsIfPresent();
      });

      li.appendChild(span);
      li.appendChild(del);
      list.appendChild(li);
    });
  }

  // --------------------------------------------------
  // Workout type UI switching
  // --------------------------------------------------
  typeSelect.addEventListener("change", () => {
    const t = typeSelect.value;
    if (cardio.has(t)) {
      durationSection.style.display = "block";
      repsSection.style.display = "none";
    } else if (strength.has(t)) {
      repsSection.style.display = "block";
      durationSection.style.display = "none";
    } else {
      repsSection.style.display = "none";
      durationSection.style.display = "none";
    }
  });

  // --------------------------------------------------
  // Load User
  // --------------------------------------------------
  async function loadUser() {
    const username = getCurrentUser();
    const u = await apiGet(`/users/${username}`);
    userId = u.userId;
  }

  // --------------------------------------------------
  // Load workouts for user
  // --------------------------------------------------
  async function loadWorkouts() {
    if (!userId) await loadUser();
    const rows = await apiGet(`/users/${userId}/workouts`);
    renderRows(rows);
  }

  // --------------------------------------------------
  // Refresh totals
  // --------------------------------------------------
  async function refreshTotalsIfPresent() {
    const totalEl = document.getElementById("total-points");
    const weeklyEl = document.getElementById("weekly-points");
    const dailyEl = document.getElementById("daily-points");
    const streakEl = document.getElementById("streak-count");

    if (!totalEl && !weeklyEl && !dailyEl && !streakEl) return;

    if (!userId) await loadUser();
    const pts = await apiGet(`/users/${userId}/points`);

    if (totalEl) totalEl.textContent = pts.totalPoints ?? 0;
    if (weeklyEl) weeklyEl.textContent = pts.weeklyPoints ?? 0;
    if (dailyEl) dailyEl.textContent = pts.dailyPoints ?? 0;
    if (streakEl) streakEl.textContent = pts.streak ?? 0;
  }

  // --------------------------------------------------
  // Create Workout
  // --------------------------------------------------
  async function createWorkout(e) {
    e.preventDefault();

    const t = typeSelect.value;
    if (!t) {
      alert("Select a workout type.");
      return;
    }

    let sets = 1;
    let reps = 0;

    if (cardio.has(t)) {
      const duration = parseInt(document.getElementById("duration").value, 10);
      if (!Number.isFinite(duration) || duration <= 0) {
        alert("Enter duration in minutes.");
        return;
      }
      reps = duration;
    } else if (strength.has(t)) {
      const s = parseInt(document.getElementById("sets").value, 10);
      const r = parseInt(document.getElementById("reps").value, 10);

      if (!Number.isFinite(s) || s <= 0) {
        alert("Enter sets.");
        return;
      }
      if (!Number.isFinite(r) || r <= 0) {
        alert("Enter reps.");
        return;
      }

      sets = s;
      reps = r;
    }

    if (!userId) await loadUser();

    await apiPost(`/users/${userId}/workouts`, {
      workoutDate: new Date().toISOString().slice(0, 10),
      workoutType: t,
      sets,
      reps,
    });

    await loadWorkouts();
    await refreshTotalsIfPresent();
    form.reset();
    durationSection.style.display = "none";
    repsSection.style.display = "none";
  }

  // --------------------------------------------------
  async function reloadAllForCurrentUser() {
    userId = null;
    await loadUser();
    await loadWorkouts();
    await refreshTotalsIfPresent();
  }

  // Initialize
  setupUserSwitcher();
  await reloadAllForCurrentUser();
  form.addEventListener("submit", createWorkout);
});
