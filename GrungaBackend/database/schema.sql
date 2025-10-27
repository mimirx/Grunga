CREATE DATABASE IF NOT EXISTS grunga;
USE grunga;

CREATE TABLE IF NOT EXISTS users (
  user_id INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(50) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NULL,
  email VARCHAR(100) NULL,
  date_joined DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS workouts (
  workout_id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  workout_type VARCHAR(50) NOT NULL,
  sets INT NOT NULL,
  reps INT NOT NULL,
  points INT NOT NULL,
  date_logged DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE IF NOT EXISTS points_totals (
  user_id INT PRIMARY KEY,
  daily_points INT DEFAULT 0,
  weekly_points INT DEFAULT 0,
  total_points INT DEFAULT 0,
  last_update DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- seed demo users and totals rows
INSERT INTO users (username) VALUES ('demo1'), ('demo2')
ON DUPLICATE KEY UPDATE username = VALUES(username);

INSERT IGNORE INTO points_totals (user_id)
SELECT user_id FROM users;
