document.addEventListener("DOMContentLoaded", async () => {
  const form = document.getElementById("workout-form");
  const typeSelect = document.getElementById("type");
  const durationSection = document.getElementById("duration-section");
  const repsSection = document.getElementById("reps-section");
  const list = document.querySelector("#workout-list ul");
  const username = "demo1";
  let userId = null;
  let apiOk = false;

  async function pingApi() {
    try {
      const res = await apiGet("/health");
      return !!(res && res.ok);
    } catch {
      return false;
    }
  }

  async function loadUser() {
    const u = await apiGet(`/users/${username}`);
    if (!u || !u.userId) throw new Error("User not found in API");
    userId = u.userId;
  }

  async function loadWorkoutsApi() {
    const rows = await apiGet(`/users/${userId}/workouts`);
    renderRows(rows || []);
  }

  async function createWorkoutApi(e) {
    e.preventDefault();

    const type = typeSelect.value;
    let sets = 1;
    let reps = 0;

    if (["run", "bike", "walk", "swim"].includes(type)) {
      const duration = parseInt(document.getElementById("duration").value);
      if (!duration || duration <= 0) return alert("Enter workout duration!");
      reps = duration;
    } else {
      const repCount = parseInt(document.getElementById("reps").value);
      if (!repCount || repCount <= 0) return alert("Enter number of reps!");
      reps = repCount;
    }

    await apiPost(`/users/${userId}/workouts`, {
      workoutDate: new Date().toISOString().slice(0, 10),
      workoutType: type,
      sets,
      reps
    });

    await loadWorkoutsApi(); // refresh list
    form.reset();
    durationSection.style.display = "none";
    repsSection.style.display = "none";
  }

  function renderRows(rows) {
    list.innerHTML = "";
    rows.forEach(r => {
      const li = document.createElement("li");
      li.textContent = `${r.workoutType} — ${r.reps} reps (on ${r.workoutDate})`;
      list.appendChild(li);
    });
  }

  typeSelect.addEventListener("change", () => {
    const type = typeSelect.value;
    if (["run", "bike", "walk", "swim"].includes(type)) {
      durationSection.style.display = "block";
      repsSection.style.display = "none";
    } else if (["pushups", "squats", "lunges", "crunches"].includes(type)) {
      repsSection.style.display = "block";
      durationSection.style.display = "none";
    } else {
      repsSection.style.display = "none";
      durationSection.style.display = "none";
    }
  });

  apiOk = await pingApi();
  if (apiOk) {
    try {
      await loadUser();
      await loadWorkoutsApi();
      form.addEventListener("submit", createWorkoutApi);
      console.log("[Grunga] Using backend API mode.");
    } catch (err) {
      console.warn("[Grunga] API mode failed.", err);
    }
  } else {
    console.warn("[Grunga] Backend unreachable.");
  }
});
