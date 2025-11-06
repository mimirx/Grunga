INSERT INTO users (username, displayName) VALUES
('demo1', 'Demo One'),
('demo2', 'Demo Two')
ON DUPLICATE KEY UPDATE displayName = VALUES(displayName);

INSERT IGNORE INTO badges (code, name, description) VALUES
('BOSS_SLAYER', 'Boss Slayer', 'Defeat a weekly boss'),
('STREAK_7', 'Streak Master', 'Complete a 7-day streak');

-- Add points for demo users
INSERT INTO pointsTotals (userId, dailyPoints, weeklyPoints, totalPoints)
SELECT userId, 50, 320, 2500 FROM users WHERE username = 'demo1'
ON DUPLICATE KEY UPDATE
  dailyPoints  = VALUES(dailyPoints),
  weeklyPoints = VALUES(weeklyPoints),
  totalPoints  = VALUES(totalPoints);

INSERT INTO pointsTotals (userId, dailyPoints, weeklyPoints, totalPoints)
SELECT userId, 20, 100, 800 FROM users WHERE username = 'demo2'
ON DUPLICATE KEY UPDATE
  dailyPoints  = VALUES(dailyPoints),
  weeklyPoints = VALUES(weeklyPoints),
  totalPoints  = VALUES(totalPoints);
