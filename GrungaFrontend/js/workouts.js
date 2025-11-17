import { apiGet, apiPost } from "./api.js";

document.addEventListener("DOMContentLoaded", async () => {
  const form = document.getElementById("workout-form");
  const typeSelect = document.getElementById("type");
  const durationSection = document.getElementById("duration-section");
  const repsSection = document.getElementById("reps-section");
  const list = document.querySelector("#workout-list ul");
  const username = "demo1";
  let userId = null;

  const cardio = new Set(["run","bike","walk","swim"]);
  const strength = new Set(["pushups","squats","lunges","crunches"]);

  function renderRows(rows) {
    list.innerHTML = "";

    (rows || []).forEach(r => {
      const d = typeof r.workoutDate === "string"
        ? r.workoutDate
        : new Date(r.workoutDate).toISOString().slice(0,10);

      const isCardio = cardio.has(r.workoutType);
      const txt = isCardio
        ? `${r.workoutType} — ${r.reps} min (${d})`
        : `${r.workoutType} — ${r.sets} x ${r.reps} (${d})`;

      const li = document.createElement("li");
      li.classList.add("workout-item");

      // TEXT SPAN
      const span = document.createElement("span");
      span.textContent = txt;

      // DELETE BUTTON
      const del = document.createElement("button");
      del.classList.add("delete-btn");
      del.innerHTML = "✖";

      del.addEventListener("click", async () => {
        if (!confirm("Delete this workout?")) return;

        await apiPost(`/users/${userId}/workouts/delete`, {
          workoutId: r.workoutId
        });

        await loadWorkouts();            // update workout list
        await refreshTotalsIfPresent();  // update points
      });

      li.appendChild(span);
      li.appendChild(del);
      list.appendChild(li);
    });
  }


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

  async function loadUser() {
    const u = await apiGet(`/users/${username}`);
    userId = u.userId;
  }

  async function loadWorkouts() {
    const rows = await apiGet(`/users/${userId}/workouts`);
    renderRows(rows);
  }

  async function refreshTotalsIfPresent() {
    const totalEl = document.getElementById("total-points");
    const weeklyEl = document.getElementById("weekly-points");
    const dailyEl = document.getElementById("daily-points");
    const streakEl = document.getElementById("streak-count");
    if (!totalEl && !weeklyEl && !dailyEl && !streakEl) return;
    const pts = await apiGet(`/users/${userId}/points`);
    if (totalEl) totalEl.textContent = pts.totalPoints ?? 0;
    if (weeklyEl) weeklyEl.textContent = pts.weeklyPoints ?? 0;
    if (dailyEl) dailyEl.textContent = pts.dailyPoints ?? 0;
    if (streakEl) streakEl.textContent = pts.streak ?? 0;
  }

  async function createWorkout(e) {
    e.preventDefault();
    const t = typeSelect.value;
    if (!t) { alert("Select a workout type."); return; }

    let sets = 1;
    let reps = 0;

    if (cardio.has(t)) {
      const duration = parseInt(document.getElementById("duration").value, 10);
      if (!Number.isFinite(duration) || duration <= 0) { alert("Enter duration in minutes."); return; }
      reps = duration;
    } else if (strength.has(t)) {
      const s = parseInt(document.getElementById("sets").value, 10);
      const r = parseInt(document.getElementById("reps").value, 10);
      if (!Number.isFinite(s) || s <= 0) { alert("Enter sets."); return; }
      if (!Number.isFinite(r) || r <= 0) { alert("Enter reps."); return; }
      sets = s;
      reps = r;
    } else {
      alert("Unsupported workout type.");
      return;
    }

    await apiPost(`/users/${userId}/workouts`, {
      workoutDate: new Date().toISOString().slice(0,10),
      workoutType: t,
      sets,
      reps
    });

    await loadWorkouts();
    await refreshTotalsIfPresent();
    form.reset();
    durationSection.style.display = "none";
    repsSection.style.display = "none";
  }

  await loadUser();
  await loadWorkouts();
  form.addEventListener("submit", createWorkout);
});
