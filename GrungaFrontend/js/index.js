

const greeting = document.getElementById("greeting");
const totalPointsEl = document.getElementById("total-points");
const weeklyPointsEl = document.getElementById("weekly-points");
const dailyPointsEl = document.getElementById("daily-points");
const streakEl = document.getElementById("streak-count");
const bossArt = document.getElementById("boss-art");
const canvas = document.getElementById("weeklyChart");
const ctx = canvas.getContext("2d");

// demo user
const user = {
  name: "Demo User",
  totalPoints: 2640,
  weeklyPoints: 740,
  dailyPoints: 120,
  streak: 8,
  weeklyProgress: [80, 100, 60, 70, 90, 110, 120] // Mon–Sun
};

// --- Time-based greeting ---
function setGreeting() {
  const hour = new Date().getHours();
  let message = "Welcome back";
  if (hour < 12) message = "Good morning";
  else if (hour < 18) message = "Good afternoon";
  else message = "Good evening";
  greeting.textContent = `${message}, ${user.name}!`;
}


function animateValue(el, start, end, duration = 1000) {
  const range = end - start;
  let startTime;
  function step(timestamp) {
    if (!startTime) startTime = timestamp;
    const progress = Math.min((timestamp - startTime) / duration, 1);
    el.textContent = Math.floor(start + range * progress);
    if (progress < 1) requestAnimationFrame(step);
  }
  requestAnimationFrame(step);
}

// weekly chart
function drawWeeklyChart() {
  const labels = ["M", "T", "W", "T", "F", "S", "S"];
  const data = user.weeklyProgress;
  const max = Math.max(...data) * 1.2;
  const barWidth = canvas.width / data.length - 20;

  ctx.clearRect(0, 0, canvas.width, canvas.height);

  data.forEach((val, i) => {
    const x = i * (barWidth + 20) + 30;
    const barHeight = (val / max) * (canvas.height - 40);
    const y = canvas.height - barHeight - 30;

    const gradient = ctx.createLinearGradient(x, y, x, y + barHeight);
    gradient.addColorStop(0, "#00d38a");
    gradient.addColorStop(1, "#00ffae");

    ctx.fillStyle = gradient;
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

//Boss image hover animation
bossArt.addEventListener("mouseenter", () => {
  bossArt.style.filter = "drop-shadow(0 0 20px var(--accent-glow))";
});
bossArt.addEventListener("mouseleave", () => {
  bossArt.style.filter = "none";
});

window.addEventListener("DOMContentLoaded", () => {
  setGreeting();
  animateValue(totalPointsEl, 0, user.totalPoints, 1200);
  animateValue(weeklyPointsEl, 0, user.weeklyPoints, 1200);
  animateValue(dailyPointsEl, 0, user.dailyPoints, 1200);
  animateValue(streakEl, 0, user.streak, 1200);
  drawWeeklyChart();
});
