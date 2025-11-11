import { apiGet } from "./api.js";

const greeting = document.getElementById("greeting");
const totalPointsEl = document.getElementById("total-points");
const weeklyPointsEl = document.getElementById("weekly-points");
const dailyPointsEl = document.getElementById("daily-points");
const streakEl = document.getElementById("streak-count");
const bossArt = document.getElementById("boss-art");
const hpBar = document.getElementById("hp-bar");

// SAFE canvas access
const canvas = document.getElementById("weeklyChart");
const ctx = canvas && canvas.getContext ? canvas.getContext("2d") : null;

function setGreeting(name) {
  const h = new Date().getHours();
  let msg = "Welcome back";
  if (h < 12) msg = "Good morning";
  else if (h < 18) msg = "Good afternoon";
  else msg = "Good evening";
  if (greeting) greeting.textContent = `${msg}, ${name}!`;
}

function animateValue(el, start, end, ms = 1000) {
  if (!el) return;
  const d = end - start;
  let t0;
  function step(ts) {
    if (!t0) t0 = ts;
    const p = Math.min((ts - t0) / ms, 1);
    el.textContent = Math.floor(start + d * p);
    if (p < 1) requestAnimationFrame(step);
  }
  requestAnimationFrame(step);
}

function drawWeeklyChart(bins) {
  if (!ctx || !canvas) return; // guard
  const labels = ["M","T","W","T","F","S","S"];
  const max = Math.max(...bins, 1) * 1.2;
  const barWidth = canvas.width / bins.length - 20;

  ctx.clearRect(0, 0, canvas.width, canvas.height);
  bins.forEach((val, i) => {
    const x = i * (barWidth + 20) + 30;
    const barHeight = (val / max) * (canvas.height - 40);
    const y = canvas.height - barHeight - 30;

    const g = ctx.createLinearGradient(x, y, x, y + barHeight);
    g.addColorStop(0, "#00d38a");
    g.addColorStop(1, "#00ffae");

    ctx.fillStyle = g;
    ctx.shadowColor = "#00ffae";
    ctx.shadowBlur = 10;
    ctx.fillRect(x, y, barWidth, barHeight);

    ctx.shadowBlur = 0;
    ctx.fillStyle = "#f3f4f6";
    ctx.textAlign = "center";
    ctx.font = "14px Segoe UI";
    ctx.fillText(labels[i], x + barWidth / 2, canvas.height - 10);
  });
}

function updateBossHp(boss) {
  if (!hpBar || !boss) return;
  const pct = Math.round((1 - boss.hp / boss.maxHp) * 100);
  hpBar.value = pct;
  hpBar.max = 100;
  hpBar.title = `Boss HP: ${boss.hp}/${boss.maxHp}`;
  if (boss.hp <= 0) {
    hpBar.style.setProperty("--accent", "#ff4d88");
    const status = document.getElementById("battle-status");
    if (status) status.textContent = "Boss defeated! 🎉";
  }
}

async function loadHome() {
  try {
    const u = await apiGet(`/users/demo1`);
    const pts = await apiGet(`/users/${u.userId}/points`);

    setGreeting(u.displayName || "Demo User");

    animateValue(totalPointsEl, 0, pts.totalPoints ?? 0, 1200);
    animateValue(weeklyPointsEl, 0, pts.weeklyPoints ?? 0, 1200);
    animateValue(dailyPointsEl, 0, pts.dailyPoints ?? 0, 1200);
    animateValue(streakEl, 0, pts.streak ?? 0, 1200);

    drawWeeklyChart(Array.isArray(pts.hist) ? pts.hist : [0,0,0,0,0,0,0]);
    updateBossHp(pts.boss);
  } catch (err) {
    console.error("loadHome failed:", err);
  }
}

if (bossArt) {
  bossArt.addEventListener("mouseenter", () => {
    bossArt.style.filter = "drop-shadow(0 0 20px var(--accent-glow))";
  });
  bossArt.addEventListener("mouseleave", () => {
    bossArt.style.filter = "none";
  });
}

window.addEventListener("DOMContentLoaded", loadHome);
