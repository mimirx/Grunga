import { apiGet } from './api.js';

// SAME BADGE CONFIG AS badges.js (sectionId ignored here)
const BADGE_CONFIG = {
    BOSS_SLAYER:  { sectionId: "friend-boss", img: "assets/images/GrogSlayer.png", label: "Grog Slayer" },
    BOSS_PYRO:    { sectionId: "friend-boss", img: "assets/images/PyroConqueror.png", label: "Pyro Conqueror" },
    BOSS_NOVA:    { sectionId: "friend-boss", img: "assets/images/NovaTimer.png", label: "Nova Tamer" },
    BOSS_GRUNGA:  { sectionId: "friend-boss", img: "assets/images/GrungaPrime.png", label: "Grunga Prime" },
    STREAK_3:     { sectionId: "friend-streak", img: "assets/images/3week.png", label: "3-Week Crusher" },
    STREAK_5:     { sectionId: "friend-streak", img: "assets/images/5week.png", label: "5-Week Sentinel" },
    STREAK_7:     { sectionId: "friend-streak", img: "assets/images/7week.png", label: "7-Week Dedication" },
    STREAK_10:    { sectionId: "friend-streak", img: "assets/images/10week.png", label: "10-Week Master" },
    FIRST_WORKOUT:{ sectionId: "friend-challenge", img: "assets/images/1challenge.png", label: "First Workout Logged" },
    CHALLENGE_3:  { sectionId: "friend-challenge", img: "assets/images/3challenge.png", label: "Challenge Contender" },
    CHALLENGE_5:  { sectionId: "friend-challenge", img: "assets/images/5challenge.png", label: "Challenge Rookie" },
    CHALLENGE_10: { sectionId: "friend-challenge", img: "assets/images/10challenge.png", label: "Challenge Veteran" }
};

function getUserParam() {
    const params = new URLSearchParams(window.location.search);
    return params.get("userId");
}

/* Render badges visually */
function renderBadges(badges) {
    const container = document.getElementById("friend-badges");
    if (container) container.innerHTML = '';

    if (!Array.isArray(badges) || badges.length === 0) {
        const div = document.createElement('div');
        div.classList.add('badge', 'locked');
        const img = document.createElement('img');
        img.src = 'assets/images/locked.png';
        const label = document.createElement('p');
        label.textContent = 'No badges yet';
        div.appendChild(img);
        div.appendChild(label);
        container.appendChild(div);
        return;
    }

    badges.forEach(badge => {
        const config = BADGE_CONFIG[badge.code];
        if (!config) return;

        const div = document.createElement('div');
        div.classList.add('badge', badge.unlocked ? 'unlocked' : 'locked');

        const img = document.createElement('img');
        img.src = config.img || 'assets/images/favicon.png';

        const label = document.createElement('p');
        label.textContent = config.label;

        div.appendChild(img);
        div.appendChild(label);
        container.appendChild(div);
    });
}

/* Load all friend's data */
async function initProfile() {
    const rawParam = getUserParam();
    const nameEl = document.getElementById("friend-name");

    if (!rawParam) {
        if (nameEl) nameEl.textContent = "Invalid Friend";
        return;
    }

    try {
        // 1️⃣ Normalize whatever we got in ?userId= (username or numeric id)
        //    by asking /users/<...> and reading user.userId
        const user = await apiGet(`/users/${rawParam}`);
        const friendId = user.userId;   // numeric database id

        const displayName =
            user.displayName && user.displayName.trim() !== ""
                ? user.displayName
                : user.username;

        if (nameEl) {
            nameEl.textContent = displayName;
        }

        // 2️⃣ Get stats from the new backend route
        const summary = await apiGet(`/friends/profile/${friendId}`);
        const pts = summary.points || {};

        document.getElementById("streak").textContent = pts.streak ?? 0;
        document.getElementById("total").textContent  = pts.total  ?? 0;
        document.getElementById("weekly").textContent = pts.weekly ?? 0;
        document.getElementById("daily").textContent  = pts.daily  ?? 0;

        // Total workouts now comes from backend, no more .total on an array
        document.getElementById("workouts").textContent =
            summary.totalWorkouts ?? 0;

        // 3️⃣ Badges endpoint is already working for friends
        const badges = await apiGet(`/badges/user/${friendId}`);
        renderBadges(badges);

        // (Optional) you now ALSO have summary.weeklyHistogram if you
        // want to draw a chart for the friend's points.
    } catch (err) {
        console.error("Profile load error:", err);
        if (nameEl) {
            nameEl.textContent = "Error loading friend profile";
        }
    }
}

/* Run profile loader */
document.addEventListener("DOMContentLoaded", () => {
    initProfile();
});
