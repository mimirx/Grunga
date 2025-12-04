import { apiGet } from './api.js';

// SAME BADGE CONFIG AS badges.js
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
    container.innerHTML = "";

    if (!badges || badges.length === 0) {
        container.innerHTML = "<p>No badges yet.</p>";
        return;
    }

    badges.forEach(b => {
        const item = document.createElement("div");
        item.classList.add("badge-item");

        // maps your badge codes to REAL filenames
        const BADGE_IMAGE_MAP = {
            // Boss badges
            BOSS_SLAYER:   "GrogSlayer.png",
            BOSS_PYRO:     "PyroConqueror.png",
            BOSS_NOVA:     "NovaTimer.png",
            BOSS_GRUNGA:   "GrungaPrime.png",

            // Streak milestone badges
            STREAK_3:      "3week.png",
            STREAK_5:      "5week.png",
            STREAK_7:      "7week.png",
            STREAK_10:     "10week.png",

            // Challenge milestone badges
            CHALLENGE_3:   "3challenge.png",
            CHALLENGE_5:   "5challenge.png",
            CHALLENGE_10:  "10challenge.png",

            // First workout badge (correct file)
            FIRST_WORKOUT: "1challenge.png"
        };



        // fallback if missing
        function getBadgeImage(code) {
            return BADGE_IMAGE_MAP[code] || "favicon.png";
        }
        
        item.innerHTML = `
            <img src="assets/images/${getBadgeImage(b.code)}"
                class="${b.unlocked ? '' : 'locked'}">
            <p>${b.name}</p>
        `;

        container.appendChild(item);
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
