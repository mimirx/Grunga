document.addEventListener('DOMContentLoaded', () => {
  // Demo values (will be replaced by backend fetch later)
  const demo = { total: 2500, weekly: 320, daily: 50, streak: 5 };
  document.getElementById('total-points').textContent = demo.total;
  document.getElementById('weekly-points').textContent = demo.weekly;
  document.getElementById('daily-points').textContent = demo.daily;
  document.getElementById('streak-count').textContent = demo.streak;
});
