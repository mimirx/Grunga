import { apiGet } from './api.js';

// ------------------------------
// USER SWITCH SETUP (SAME AS INDEX)
// ------------------------------

let currentUser = localStorage.getItem("currentUser") || "demo1";

// get all switch buttons
const userButtons = document.querySelectorAll("#user-switcher .user-btn");

// highlight active button
userButtons.forEach(btn => {
    if (btn.dataset.user === currentUser) {
        btn.classList.add("active");
    }

    btn.addEventListener("click", () => {
        localStorage.setItem("currentUser", btn.dataset.user);
        location.reload();   // reload badges page with selected user
    });
});

// convert username to userId
function usernameToId(name) {
    return name === "demo1" ? 1 : 2;
}

// ------------------------------
// PAGE LOAD
// ------------------------------

document.addEventListener('DOMContentLoaded', () => {
    initBadgesPage();
});

async function initBadgesPage() {
    const username = currentUser;
    const userId = usernameToId(username);

    try {
        const badges = await apiGet(`/badges/user/${userId}`);
        console.log("BADGES RECEIVED:", badges);
        renderBadges(badges);
    } catch (err) {
        console.error('Failed to load badges for user', err);
    }
}

// ------------------------------
// BADGE CONFIG
// ------------------------------

const BADGE_CONFIG = {
    // ---------------- BOSS BADGES ----------------
    BOSS_SLAYER: {
        sectionId: 'boss-badges',
        img: 'assets/images/GrogSlayer.png',
        label: 'Grog Slayer'
    },
    BOSS_PYRO: {
        sectionId: 'boss-badges',
        img: 'assets/images/PyroConqueror.png',
        label: 'Pyro Conqueror'
    },
    BOSS_NOVA: {
        sectionId: 'boss-badges',
        img: 'assets/images/NovaTimer.png',
        label: 'Nova Tamer'
    },
    BOSS_GRUNGA: {
        sectionId: 'boss-badges',
        img: 'assets/images/GrungaPrime.png',
        label: 'Grunga Prime'
    },

    // ---------------- STREAK BADGES ----------------
    STREAK_3: {
        sectionId: 'streak-badges',
        img: 'assets/images/3week.png',
        label: '3-Week Crusher'
    },
    STREAK_5: {
        sectionId: 'streak-badges',
        img: 'assets/images/5week.png',
        label: '5-Week Sentinel'
    },
    STREAK_7: {
        sectionId: 'streak-badges',
        img: 'assets/images/7week.png',
        label: '7-Week Dedication'
    },
    STREAK_10: {
        sectionId: 'streak-badges',
        img: 'assets/images/10week.png',
        label: '10-Week Master'
    },

    // ---------------- CHALLENGE BADGES ----------------
    FIRST_WORKOUT: {
        sectionId: 'challenge-badges',
        img: 'assets/images/1challenge.png',
        label: 'First Workout Logged'
    },
    CHALLENGE_3: {
        sectionId: 'challenge-badges',
        img: 'assets/images/3challenge.png',
        label: 'Challenge Contender'
    },
    CHALLENGE_5: {
        sectionId: 'challenge-badges',
        img: 'assets/images/5challenge.png',
        label: 'Challenge Rookie'
    },
    CHALLENGE_10: {
        sectionId: 'challenge-badges',
        img: 'assets/images/10challenge.png',
        label: 'Challenge Veteran'
    }
};


// ------------------------------
// RENDER BADGES
// ------------------------------

function renderBadges(badges) {
    ['boss-badges', 'streak-badges', 'challenge-badges'].forEach(id => {
        const el = document.getElementById(id);
        if (el) el.innerHTML = '';
    });

    if (!Array.isArray(badges)) return;

    badges.forEach(badge => {
        const config = BADGE_CONFIG[badge.code];
        if (!config) return;

        const container = document.getElementById(config.sectionId);
        if (!container) return;

        const div = document.createElement('div');
        div.classList.add('badge', badge.unlocked ? 'unlocked' : 'locked');

        const img = document.createElement('img');
        img.src = config.img;

        const label = document.createElement('p');
        label.textContent = config.label;

        div.appendChild(img);
        div.appendChild(label);
        container.appendChild(div);
    });

    addPlaceholderIfEmpty('boss-badges', 'This Boss is Locked');
    addPlaceholderIfEmpty('streak-badges', 'No streak badges yet');
    addPlaceholderIfEmpty('challenge-badges', 'No challenge / milestone badges yet');
}

function addPlaceholderIfEmpty(sectionId, text) {
    const container = document.getElementById(sectionId);
    if (!container || container.children.length > 0) return;

    const div = document.createElement('div');
    div.classList.add('badge', 'locked');

    const img = document.createElement('img');
    img.src = 'assets/images/locked.png';

    const label = document.createElement('p');
    label.textContent = text;

    div.appendChild(img);
    div.appendChild(label);

    container.appendChild(div);
}
