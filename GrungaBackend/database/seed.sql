INSERT INTO users (username, displayName) VALUES
('demo1','Demo One'),
('demo2','Demo Two')
ON DUPLICATE KEY UPDATE displayName = VALUES(displayName);

INSERT IGNORE INTO badges(code, name, description) VALUES
('BOSS_SLAYER','Boss Slayer','Defeat a weekly boss'),
('STREAK_7','Streak Master','Complete a 7-day streak');
