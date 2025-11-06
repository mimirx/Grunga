document.addEventListener('DOMContentLoaded', async () => {
  const username = 'demo1';
  
  const els = {
    total:  document.getElementById('total-points'),
    weekly: document.getElementById('weekly-points'),
    daily:  document.getElementById('daily-points'),
    streak: document.getElementById('streak-count'),
  };

  // default fallback so the page shows something if API fails
  function setDemo() {
    const demo = { total: 2500, weekly: 320, daily: 50, streak: 5 };
    els.total.textContent  = demo.total;
    els.weekly.textContent = demo.weekly;
    els.daily.textContent  = demo.daily;
    els.streak.textContent = demo.streak;
  }

  try {
    const u = await apiGet(`/users/${username}`); // {userId, username, displayName}
    const userId = u.userId;

    const pts = await apiGet(`/users/${userId}/points`); // {dailyPoints, weeklyPoints, totalPoints}

    els.total.textContent  = pts.totalPoints ?? 0;
    els.weekly.textContent = pts.weeklyPoints ?? 0;
    els.daily.textContent  = pts.dailyPoints ?? 0;

    // (optional) if you later store streak in DB, fetch & set it here.
    // For now we keep the old hard-coded 5 as a temporary placeholder:
    els.streak.textContent = 5;

  } catch (err) {
    console.warn('API failed on home page; showing demo numbers.', err);
    setDemo();
  }

  console.log('points response:', pts); // debug
});
