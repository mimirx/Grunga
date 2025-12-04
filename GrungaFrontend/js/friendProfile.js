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

/* Extract friendId from URL */
function getUserId() {
    const params = new URLSearchParams(window.location.search);
    return params.get("userId");
}

/* Render badges visually */
function renderBadges(badges) {
    const container = document.getElementById("friend-badges");
    if (container) container.innerHTML = '';

    if (!Array.isArray(badges) || badges.length === 0) {
        // Add placeholder like in badges.js for consistency
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
        img.src = config.img || 'assets/images/favicon.png'; // Fallback

        const label = document.createElement('p');
        label.textContent = config.label;

        div.appendChild(img);
        div.appendChild(label);
        container.appendChild(div);
    });
}

/* Load all friend's data */
async function initProfile() {
    const friendId = getUserId();
    if (!friendId) {
        document.getElementById("friend-name").textContent = "Invalid Friend";
        return;
    }
    try {
        // FIXED: correct user info endpoint
        // friendId is actually the USERNAME that we stored from friends.js
        const user = await apiGet(`/users/${friendId}`);
        const displayName =
            user.displayName?.trim() !== "" ? user.displayName : user.username;
        document.getElementById("friend-name").textContent = displayName;
        // FIXED: correct points/streak endpoint
        const points = await apiGet(`/users/${friendId}/points`);
        document.getElementById("streak").textContent = points.streak ?? 0;
        document.getElementById("total").textContent = points.total ?? 0;
        document.getElementById("weekly").textContent = points.weekly ?? 0;
        document.getElementById("daily").textContent = points.daily ?? 0;
        // workouts endpoint (yours is correct)
        const workouts = await apiGet(`/users/${friendId}/workouts`);
        document.getElementById("workouts").textContent = workouts.total ?? 0;
        // badges endpoint
        const badges = await apiGet(`/badges/user/${friendId}`);
        renderBadges(badges);
    } catch (err) {
        console.error("Profile load error:", err);
    }
}

/* Run profile loader */
document.addEventListener("DOMContentLoaded", () => {
    initProfile();
});