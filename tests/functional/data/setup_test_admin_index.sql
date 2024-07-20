DELETE FROM users;

-- password: "qwe123!@#"
INSERT INTO users (id, first, last, email, role, password_hash, properties, added, updated, last_login) VALUES
  ('4d7993aa-d897-4647-994b-e0625c88f349', 'first', 'last', 'admin@test.com', 'super-admin', '2c835ba8966d902120fb4504037fad34effa4b9461e988e4c4da073ad50dae82', '{"nativeLang": "uk", "challenges": {"dailyTraining": {"learnListSize": 50, "practiceCountThreshold": 50, "knowledgeLevelThreshold": 0.9, "learning_list": []}}}', '2023-04-09 10:34:42', '2023-04-09 10:34:42', '2023-04-09 10:34:42');
