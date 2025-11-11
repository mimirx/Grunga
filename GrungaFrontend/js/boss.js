import { apiGet } from "./api.js";

const hpBar = document.getElementById("hp-bar");
const statusEl = document.getElementById("battle-status");
const bossImg = document.getElementById("boss-image");

function updateBossHp(boss) {
  if (!boss || !hpBar) return;

  const pct = Math.max(0, Math.min(100, Math.round((1 - boss.hp / boss.maxHp) * 100)));
  hpBar.max = 100;
  hpBar.value = pct;
  hpBar.title = `Boss HP: ${boss.hp} / ${boss.maxHp}`;

  if (statusEl) {
    statusEl.textContent =
      boss.hp <= 0
        ? "Boss defeated! 🎉 Great work this week!"
        : `Keep going! Boss HP: ${boss.hp} / ${boss.maxHp}`;
  }

  if (bossImg) {
    if (boss.hp <= 0) {
      bossImg.style.filter = "drop-shadow(0 0 30px #ff4d88)";
      bossImg.style.transform = "scale(1.02)";
    } else {
      bossImg.style.filter = "drop-shadow(0 0 0 transparent)";
      bossImg.style.transform = "none";
    }
  }
}

async function loadBossPage() {
  try {
    const user = await apiGet(`/users/demo1`);
    const pts = await apiGet(`/users/${user.userId}/points`);
    updateBossHp(pts.boss);
  } catch (err) {
    console.error("Failed to load boss page:", err);
    if (statusEl) statusEl.textContent = "Could not load boss status. Try again.";
  }
}

// Refresh when page becomes visible (handy after logging workouts)
document.addEventListener("visibilitychange", () => {
  if (document.visibilityState === "visible") loadBossPage();
});

window.addEventListener("DOMContentLoaded", loadBossPage);
