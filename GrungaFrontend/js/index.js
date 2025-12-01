import { apiGet, getCurrentUser, setCurrentUser } from "./api.js";

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

function setGreetingText(name) {
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
  const labels = ["M","Tu","W","Th","F","Sa","Su"];
  const max = Math.max(...bins, 1) * 1.2;
  const barWidth = canvas.width / bins.length - 20;

  ctx.clearRect(0, 0, canvas.width, canvas.height);

  // Set the bottom margin area for text
  const textMargin = 35; 
  const chartHeight = canvas.height - textMargin; // Height available for bars

  bins.forEach((val, i) => {
    const x = i * (barWidth + 20) + 30;
    const barHeight = (val / max) * chartHeight;
    const y = chartHeight - barHeight + 5; // +5 to give a small gap above the bars

    // Gradient remains correct
    const g = ctx.createLinearGradient(x, y, x, y + barHeight);
    g.addColorStop(0, "#00d38a");
    g.addColorStop(1, "#00ffae");

    ctx.fillStyle = g;
    ctx.shadowColor = "#00ffae";
    ctx.shadowBlur = 10;
    ctx.fillRect(x, y, barWidth, barHeight);

    // Reset shadow for text
    ctx.shadowBlur = 0;
    ctx.textAlign = "center";
    
    const centerX = x + barWidth / 2;

    // 1. Draw Day Label (M, T, W, etc.) - Positioned 15px from the canvas bottom
    ctx.fillStyle = "#f3f4f6"; // White/Light Text Color
    ctx.font = "14px Segoe UI"; 
    const dayLabelY = canvas.height - 15;
    ctx.fillText(labels[i], centerX, dayLabelY);

    // 2. Draw Daily Points Gained (Value) - Font set to BOLD and bright color
    ctx.font = "700 12px Segoe UI"; 
    ctx.fillStyle = "#00ffae"; // Bright Accent Color
    const pointValueY = dayLabelY + 15;
    ctx.fillText(val, centerX, pointValueY); 
  });
}

/**
 * Updates the boss's HP bar, status, and image (using boss.asset from API).
 * Max HP is enforced as 500 for display purposes.
 */
function updateBossHp(boss) {
  if (!hpBar || !boss) return;

  // 1. Update Boss Image (NEW)
  if (bossArt && boss.asset) {
    // Dynamically set the image source using the asset name from the backend
    bossArt.src = `assets/images/${boss.asset}`;
  }

  const displayMaxHp = 500;
  const currentHp = boss.hp;
  
  // 2. Calculate Percentage: (Current HP / Display Max HP) * 100
  let pct = Math.round((currentHp / displayMaxHp) * 100);
  
  // Clamp between 0 and 100 just to be safe
  pct = Math.max(0, Math.min(100, pct));

  hpBar.value = pct;
  hpBar.max = 100;
  // Use the actual current HP, but show the max as 500 in the title
  hpBar.title = `Boss HP: ${currentHp}/${displayMaxHp}`; 

  // 3. Determine Color based on Percentage
  let barColor = "#00d38a"; // Default Green (High HP)

  if (pct <= 20) {
    barColor = "#ef4444"; // Red (Critical)
  } else if (pct <= 50) {
    barColor = "#f59e0b"; // Orange (Mid)
  }

  // 4. Apply the color
  hpBar.style.accentColor = barColor;
  hpBar.style.setProperty("--accent", barColor);

  // 5. Handle Boss Defeated
  if (currentHp <= 0) {
    const status = document.getElementById("battle-status");
    if (status) status.textContent = "Boss defeated! 🎉";
  }
}

async function loadHome() {
  try {
    const username = getCurrentUser();    // NEW
    // 1) Load user
    const u = await apiGet(`/users/${username}`);
    // 2) Load points/stats
    const pts = await apiGet(`/users/${u.userId}/points`);

    setGreetingText(u.displayName || username);

    animateValue(totalPointsEl, 0, pts.totalPoints ?? 0, 1200);
    animateValue(weeklyPointsEl, 0, pts.weeklyPoints ?? 0, 1200);
    animateValue(dailyPointsEl, 0, pts.dailyPoints ?? 0, 1200);
    animateValue(streakEl, 0, pts.streak ?? 0, 1200);

    drawWeeklyChart(Array.isArray(pts.hist) ? pts.hist : [0,0,0,0,0,0,0]);
    updateBossHp(pts.boss); // This handles both HP and image asset
  } catch (err) {
    console.error("loadHome failed:", err);
  }
}


// ========== USER SWITCHER UI ==========
function setupUserSwitcher() {
  const btn1 = document.querySelector("[data-user='demo1']");
  const btn2 = document.querySelector("[data-user='demo2']");
  if (!btn1 || !btn2) return;

  function updateActiveButtons() {
    const u = getCurrentUser();
    btn1.classList.toggle("active", u === "demo1");
    btn2.classList.toggle("active", u === "demo2");
  }

  btn1.addEventListener("click", () => {
    setCurrentUser("demo1");
    updateActiveButtons();
    loadHome();  // refresh home data
  });

  btn2.addEventListener("click", () => {
    setCurrentUser("demo2");
    updateActiveButtons();
    loadHome();
  });

  updateActiveButtons();
}

// Whenever user changes on another page, update automatically
window.addEventListener("user-changed", () => {
  loadHome();
  setupUserSwitcher();
});
// =====================================

if (bossArt) {
  bossArt.addEventListener("mouseenter", () => {
    bossArt.style.filter = "drop-shadow(0 0 20px var(--accent-glow))";
  });
  bossArt.addEventListener("mouseleave", () => {
    bossArt.style.filter = "none";
  });
}

window.addEventListener("DOMContentLoaded", () => {
  setupUserSwitcher();
  loadHome();
});