CREATE DATABASE IF NOT EXISTS grunga CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE grunga;

CREATE TABLE users (
  userId INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(40) NOT NULL UNIQUE,
  displayName VARCHAR(60) NOT NULL DEFAULT 'User',
  email VARCHAR(120) UNIQUE,
  createdAt TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS challenges (
  challengeId   INT AUTO_INCREMENT PRIMARY KEY,
  createdAt     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  fromUserId    INT NOT NULL,
  toUserId      INT NOT NULL,
  kind          VARCHAR(40) NOT NULL,        -- e.g. 'WORKOUT'
  target        INT NOT NULL,                -- e.g. target points or reps
  progressFrom  INT NOT NULL DEFAULT 0,      -- optional, for sender
  progressTo    INT NOT NULL DEFAULT 0,      -- optional, for receiver
  status        ENUM('PENDING','ACTIVE','DECLINED','DONE')
                NOT NULL DEFAULT 'PENDING',
  dueAt         DATETIME NULL,
  CONSTRAINT fk_challenges_fromUser
    FOREIGN KEY (fromUserId) REFERENCES users(userId),
  CONSTRAINT fk_challenges_toUser
    FOREIGN KEY (toUserId) REFERENCES users(userId)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE workouts (
  workoutId INT AUTO_INCREMENT PRIMARY KEY,
  userId INT NOT NULL,
  workoutDate DATE NOT NULL,
  workoutType VARCHAR(40) NOT NULL,
  sets INT NOT NULL,
  reps INT NOT NULL,
  createdAt TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_workouts_user FOREIGN KEY (userId) REFERENCES users(userId) ON DELETE CASCADE,
  CONSTRAINT chk_workouts_positive CHECK (sets > 0 AND reps > 0),
  INDEX idx_workouts_user_date (userId, workoutDate)
) ENGINE=InnoDB;

CREATE TABLE pointsLedger (
  ledgerId INT AUTO_INCREMENT PRIMARY KEY,
  userId INT NOT NULL,
  points INT NOT NULL,
  reason VARCHAR(80) NOT NULL,
  refId VARCHAR(64),
  occurredAt TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_ledger_user FOREIGN KEY (userId) REFERENCES users(userId) ON DELETE CASCADE,
  INDEX idx_ledger_user_time (userId, occurredAt)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS friends (
  id INT AUTO_INCREMENT PRIMARY KEY,
  userId INT NOT NULL,
  friendId INT NOT NULL,
  initiatedBy INT DEFAULT NULL,
  status ENUM('pending', 'accepted', 'blocked') NOT NULL DEFAULT 'pending',
  createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_friends_user FOREIGN KEY (userId) REFERENCES users(userId) ON DELETE CASCADE,
  CONSTRAINT fk_friends_friend FOREIGN KEY (friendId) REFERENCES users(userId) ON DELETE CASCADE,
  CONSTRAINT fk_friends_initiatedBy FOREIGN KEY (initiatedBy) REFERENCES users(userId) ON DELETE CASCADE,
  CONSTRAINT uc_friend_pair UNIQUE (userId, friendId),
  CONSTRAINT chk_not_self CHECK (userId <> friendId)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE utf8mb4_unicode_ci;

CREATE TABLE badges (
  badgeId INT AUTO_INCREMENT PRIMARY KEY,
  code VARCHAR(40) NOT NULL UNIQUE,
  name VARCHAR(80) NOT NULL,
  description VARCHAR(200) NOT NULL
) ENGINE=InnoDB;

CREATE TABLE userBadges (
  id INT AUTO_INCREMENT PRIMARY KEY,
  userId INT NOT NULL,
  badgeId INT NOT NULL,
  unlockedAt TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_ub_user FOREIGN KEY (userId) REFERENCES users(userId) ON DELETE CASCADE,
  CONSTRAINT fk_ub_badge FOREIGN KEY (badgeId) REFERENCES badges(badgeId) ON DELETE CASCADE,
  UNIQUE KEY uq_user_badge (userId, badgeId)
) ENGINE=InnoDB;

CREATE TABLE pointsTotals (
  userId INT PRIMARY KEY,
  dailyPoints INT NOT NULL DEFAULT 0,
  weeklyPoints INT NOT NULL DEFAULT 0,
  totalPoints INT NOT NULL DEFAULT 0,
  updatedAt TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_totals_user FOREIGN KEY (userId) REFERENCES users(userId) ON DELETE CASCADE
) ENGINE=InnoDB;
