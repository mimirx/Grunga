document.addEventListener('DOMContentLoaded', async () => {
  const username = 'demo1';                  // adjust if you want a different user
  let userId = null;
  let apiOk = false;

  async function pingApi() {
    try {
      const r = await apiGet('/health');     // from api.js
      return !!(r && r.ok);
    } catch {
      return false;
    }
  }

  async function loadUser() {
    const u = await apiGet(`/users/${username}`);
    if (!u || !u.userId) throw new Error('User not found in API');
    userId = u.userId;
  }

  function tbody() {
    return document.getElementById('workout-rows');
  }

  function getEl(id) {
    return document.getElementById(id);
  }

  function ensureDom() {
    const need = [
      'workout-form',
      'workout-type',
      'workout-date',
      'workout-sets',
      'workout-reps',
      'workout-rows'
    ];
    const missing = need.filter(id => !getEl(id));
    if (missing.length) {
      console.warn('[workouts.js] Missing DOM ids:', missing.join(', '));
    }
  }

  async function loadWorkoutsApi() {
    const rows = await apiGet(`/users/${userId}/workouts`);
    renderRows(rows || []);
  }

  async function createWorkoutApi(e) {
    e.preventDefault();
    const wDate = getEl('workout-date')?.value || new Date().toISOString().slice(0,10);
    const wType = getEl('workout-type')?.value || 'pushups';
    const sets  = Number(getEl('workout-sets')?.value || 0);
    const reps  = Number(getEl('workout-reps')?.value || 0);

    await apiPost(`/users/${userId}/workouts`, { workoutDate: wDate, workoutType: wType, sets, reps });
    await loadWorkoutsApi();
    getEl('workout-form')?.reset?.();
  }

  function loadWorkoutsDemo() {
    const demo = [
      { workoutDate: '2025-10-20', workoutType: 'pushups', sets: 3, reps: 15 },
      { workoutDate: '2025-10-21', workoutType: 'squats',  sets: 3, reps: 20 }
    ];
    renderRows(demo);
  }

  function createWorkoutDemo(e) {
    e.preventDefault();
    console.log('[workouts.js] Demo mode: workout would be created.');
  }

  function renderRows(rows) {
    const body = tbody();
    if (!body) return;
    body.innerHTML = '';
    rows.forEach(r => {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td>${r.workoutDate ?? ''}</td>
        <td>${r.workoutType ?? ''}</td>
        <td>${r.sets ?? ''}</td>
        <td>${r.reps ?? ''}</td>
      `;
      body.appendChild(tr);
    });
  }

  ensureDom();

  apiOk = await pingApi();
  if (apiOk) {
    try {
      await loadUser();
      await loadWorkoutsApi();
      getEl('workout-form')?.addEventListener('submit', createWorkoutApi);
      console.log('[workouts.js] Using BACKEND API mode.');
    } catch (err) {
      console.warn('[workouts.js] API mode failed, falling back to demo.', err);
      loadWorkoutsDemo();
      getEl('workout-form')?.addEventListener('submit', createWorkoutDemo);
    }
  } else {
    console.warn('[workouts.js] Backend not reachable. Using DEMO mode.');
    loadWorkoutsDemo();
    getEl('workout-form')?.addEventListener('submit', createWorkoutDemo);
  }
});
