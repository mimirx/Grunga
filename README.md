# Grunga

![Python](https://img.shields.io/badge/Python-3.x-blue) ![Flask](https://img.shields.io/badge/Flask-Backend-black) ![MySQL](https://img.shields.io/badge/MySQL-Database-orange) ![APScheduler](https://img.shields.io/badge/APScheduler-Scheduler-green) ![Frontend](https://img.shields.io/badge/Frontend-HTML%20CSS%20JavaScript-blueviolet) ![Project](https://img.shields.io/badge/Project-Full%20Stack%20Application-success)

**Grunga** is a full-stack gamified workout tracking application that motivates users to stay consistent with exercise through points, streaks, boss battles, badges, and social challenges.

The project was developed as a **software engineering capstone project** and demonstrates backend architecture design, REST API development, relational database modeling, and gamification systems.

---

## Project Goal

Many people begin exercising with motivation but struggle to maintain long-term consistency. Traditional fitness apps simply log workouts, which can feel repetitive and unrewarding.

Grunga introduces **game-style progression mechanics** that reward activity and encourage consistency.

Instead of simply logging workouts, users can:

- Earn points from workouts
- Maintain activity streaks
- Defeat weekly bosses
- Unlock achievement badges
- Challenge friends to competitions

These mechanics create motivation through progression and friendly competition.

---

## Key Features

### Workout Logging

Users can log workouts including:

- Exercise type
- Sets and repetitions
- Duration (for cardio exercises)
- Workout date

Points are automatically calculated based on workout activity.

---

### Points System

Workout activity generates points which contribute to three totals:

- Daily points
- Weekly points
- Total lifetime points

Points are stored in a ledger system and recalculated dynamically.

---

### Streak System

Users maintain daily streaks by staying active.

If a user logs workouts on consecutive days, their streak increases.

---

### Weekly Boss Battles

Each week features a **boss with 500 HP**.

Users deal damage to the boss by earning workout points.

When the boss reaches **0 HP**, users unlock a special badge.

The boss resets at the start of every week.

---

### Friend System

Users can interact socially within the app by:

- Searching for other users
- Sending friend requests
- Accepting or declining requests
- Viewing friend profiles
- Comparing activity

---

### Challenges

Friends can send workout challenges to each other.

Challenge flow:

1. Send challenge
2. Accept challenge
3. Complete challenge
4. Earn bonus points

Rewards:

- Challenge completer receives **double points**
- Challenge sender receives **base points**

---

### Badge System

Badges reward users for reaching milestones.

Examples include:

- First workout logged
- Maintaining streaks
- Defeating weekly bosses
- Completing challenges

Badges remain locked until the required conditions are met.

---

## System Architecture

The application follows a layered architecture separating the frontend, backend API, service logic, and database.

```text
┌──────────────────────┐
│      Frontend        │
│  HTML / CSS / JS     │
│  (GrungaFrontend)    │
└───────────┬──────────┘
            │
            │ HTTP Requests
            ▼
┌──────────────────────┐
│      Flask API       │
│       app.py         │
│   (Blueprint Routes) │
└───────────┬──────────┘
            │
            ▼
┌──────────────────────┐
│     Service Layer    │
│  points_service      │
│  challenges_service  │
│  badges_service      │
│  friends_service     │
│  scheduler_service   │
└───────────┬──────────┘
            │
            ▼
┌──────────────────────┐
│       MySQL DB       │
│      schema.sql      │
│ users, workouts,     │
│ challenges, badges   │
└──────────────────────┘
```

---

## Backend Architecture

The backend is built using **Python Flask** and organized into modular components.

### Routes

Flask Blueprints define API endpoints for different features:

- users
- workouts
- challenges
- friends
- badges
- streaks

These endpoints allow the frontend to communicate with the backend.

---

### Service Layer

The service layer contains the core application logic such as:

- workout point calculations
- streak tracking
- challenge processing
- badge unlocking
- boss battle logic

This separation keeps route handlers clean and maintainable.

---

### Scheduler

The backend includes a background scheduler using **APScheduler**.

Scheduled tasks include:

- Expiring old challenges
- Running daily maintenance tasks

This allows the application to automatically handle time-based mechanics.

---

## Database Design

Grunga uses a **MySQL relational database**.

Core tables include:

- `users`
- `workouts`
- `challenges`
- `friends`
- `badges`
- `userBadges`
- `pointsLedger`
- `pointsTotals`

Foreign keys and constraints maintain relational integrity.

---

## Tech Stack

### Backend

- Python
- Flask
- APScheduler

### Database

- MySQL

### Frontend

- HTML
- CSS
- JavaScript

### Development Tools

- Python Virtual Environment
- MySQL Workbench
- VS Code

---

## Running the Project

### 1 Install dependencies
pip install -r requirements.txt

---

### 2 Create the database

Create a MySQL database named:
grunga

Import the provided SQL schema.

---

### 3 Configure database connection

Edit the database configuration file:
GrungaBackend/config.py

Update credentials:
DB_CONFIG = {
"user": "root",
"password": "YOUR_PASSWORD",
"host": "127.0.0.1",
"database": "grunga"
}

---

### 4 Run the backend server
python app.py

The API will run on:
http://127.0.0.1:5000

---

### 5 Run the frontend

Open the frontend in your browser:
GrungaFrontend/index.html
Or use **Live Server** in VS Code.

---

## Team

### Miro Marinov
Backend Developer

Responsible for:

- backend architecture
- Flask API design
- MySQL database schema
- points system
- streak logic
- boss battle system
- challenge system
- scheduler

### Serhii Polishchuk
Frontend Developer

Responsible for:

- HTML/CSS/JavaScript interface
- UI layout and design
- charts and visualizations
- frontend integration

---

## Future Improvements

Potential improvements include:

- user authentication system
- cloud deployment
- push notifications
- expanded exercise library
- analytics dashboards
- messaging between friends

---

## Summary

Grunga demonstrates the design and development of a complete full-stack application combining backend services, database modeling, and frontend interfaces.

The project explores how gamification techniques can improve motivation and consistency in fitness tracking applications.
