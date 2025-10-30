CREATE DATABASE IF NOT EXISTS grunga CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE grunga;

CREATE TABLE users (
  userId INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(40) NOT NULL UNIQUE,
  displayName VARCHAR(60) NOT NULL DEFAULT 'User',
  email VARCHAR(120) UNIQUE,
  createdAt TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

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
  CONSTRAINT chk_points_nonneg CHECK (points >= 0),
  INDEX idx_ledger_user_time (userId, occurredAt)
) ENGINE=InnoDB;

-- Optional cached totals to speed up /stats; keep in sync in app code
CREATE TABLE pointsTotals (
  userId INT PRIMARY KEY,
  dailyPoints INT NOT NULL DEFAULT 0,
  weeklyPoints INT NOT NULL DEFAULT 0,
  totalPoints INT NOT NULL DEFAULT 0,
  updatedAt TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_totals_user FOREIGN KEY (userId) REFERENCES users(userId) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE friends (
  id INT AUTO_INCREMENT PRIMARY KEY,
  userId INT NOT NULL,
  friendUserId INT NOT NULL,
  createdAt TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_friends_user FOREIGN KEY (userId) REFERENCES users(userId) ON DELETE CASCADE,
  CONSTRAINT fk_friends_friend FOREIGN KEY (friendUserId) REFERENCES users(userId) ON DELETE CASCADE,
  CONSTRAINT chk_not_self CHECK (userId <> friendUserId),
  -- prevent (A,B) and (B,A) duplicates via ordered pair
  pairA INT AS (LEAST(userId, friendUserId)) STORED,
  pairB INT AS (GREATEST(userId, friendUserId)) STORED,
  UNIQUE KEY uq_pair (pairA, pairB)
) ENGINE=InnoDB;

CREATE TABLE challenges (
  challengeId INT AUTO_INCREMENT PRIMARY KEY,
  senderUserId INT NOT NULL,
  receiverUserId INT NOT NULL,
  status ENUM('Pending','Accepted','Completed','Expired') NOT NULL DEFAULT 'Pending',
  createdAt TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  expiresAt TIMESTAMP NULL,
  CONSTRAINT fk_ch_sender FOREIGN KEY (senderUserId) REFERENCES users(userId) ON DELETE CASCADE,
  CONSTRAINT fk_ch_receiver FOREIGN KEY (receiverUserId) REFERENCES users(userId) ON DELETE CASCADE,
  CONSTRAINT chk_not_self_challenge CHECK (senderUserId <> receiverUserId),
  INDEX idx_ch_receiver_status (receiverUserId, status),
  INDEX idx_ch_expires (expiresAt)
) ENGINE=InnoDB;

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

-- Seed demo users
INSERT INTO users (username, displayName) VALUES
  ('demo1','Demo One'),
  ('demo2','Demo Two')
ON DUPLICATE KEY UPDATE displayName = VALUES(displayName);

-- Seed totals rows to match users
INSERT INTO pointsTotals (userId)
SELECT u.userId FROM users u
LEFT JOIN pointsTotals t ON t.userId = u.userId
WHERE t.userId IS NULL;
