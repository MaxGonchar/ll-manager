DELETE FROM users;
DELETE FROM expressions;
DELETE FROM user_expression;
DELETE FROM tag_expression;
DELETE FROM tags;

INSERT INTO users (id, first, last, email, role, password_hash, properties, added, updated, last_login) VALUES -- psw: daily_training
  ('2f732f36-c0f4-430f-921d-b62877891c80', 'first', 'last', 'admin@test.com', 'super-admin', '2c835ba8966d902120fb4504037fad34effa4b9461e988e4c4da073ad50dae82', '{"nativeLang": "uk", "challenges": {"dailyTraining": {"learnListSize": 50, "practiceCountThreshold": 50, "knowledgeLevelThreshold": 0.9, "learning_list": []}}}', '2023-04-09 10:34:42', '2023-04-09 10:34:42', '2023-04-09 10:34:42');

INSERT INTO expressions (id, expression, definition, translations, added, updated, example) VALUES
  ('4d7993aa-d897-4647-994b-e0625c88f349', 'preceding', 'coming before something in order, position, or time', '{"uk": "попередній"}', '2016-06-22 19:10:25', '2016-06-22 19:10:25', 'preceding in sentence');


INSERT INTO tags (id, tag, added, updated) VALUES
  ('c70a5101-b51a-443a-8b93-33e37bbda653', 'phrase', '2016-06-22 19:10:25', '2016-06-22 19:10:25'),
  ('1db21e9d-007d-4f62-addf-962459980943', 'verb', '2016-06-22 19:10:25', '2016-06-22 19:10:25'),
  ('80aa3d03-8b94-47fe-8428-70a1a8d61fbf', 'adverb', '2016-06-22 19:10:25', '2016-06-22 19:10:25'),
  ('8b5e2c59-18a3-4502-8950-6bd57801fc15', 'noun', '2016-06-22 19:10:25', '2016-06-22 19:10:25');

INSERT INTO tag_expression (tag_id, expression_id) VALUES
  ('c70a5101-b51a-443a-8b93-33e37bbda653', '4d7993aa-d897-4647-994b-e0625c88f349'),
  ('8b5e2c59-18a3-4502-8950-6bd57801fc15', '4d7993aa-d897-4647-994b-e0625c88f349');
