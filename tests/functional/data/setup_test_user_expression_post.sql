DELETE FROM user_expression;
DELETE FROM tag_expression;
DELETE FROM users;
DELETE FROM expressions;
DELETE FROM tags;

INSERT INTO users (id, first, last, email, role, password_hash, properties, added, updated, last_login) VALUES -- psw: daily_training
  ('04aa4f4e-a53e-4b6c-96c5-3604e3fcc4ef', 'First', 'Last', 'daily_training@test.mail', 'self-educated', 'c1a4b7e252281a7649d17a0f9f1d5180d5b5b1783dca84e121bbfcadda4ecc12', '{"nativeLang": "uk", "challenges": {"dailyTraining": {"learnListSize": 50, "practiceCountThreshold": 50, "knowledgeLevelThreshold": 0.9, "learning_list": [{"expressionId": "4d7993aa-d897-4647-994b-e0625c88f349", "position": 0, "practiceCount": 1, "knowledgeLevel": 0}, {"expressionId": "542d93d5-6a38-4ce6-95ba-de942ad3b309", "position": 1, "practiceCount": 2, "knowledgeLevel": 0}]}}}', '2023-04-16 09:10:25', '2023-04-16 09:10:25', '2023-04-16 09:10:25');

INSERT INTO expressions (id, expression, definition, translations, added, updated) VALUES
  ('4d7993aa-d897-4647-994b-e0625c88f349', 'preceding'                    , 'coming before something in order, position, or time' , '{"uk": "попередній"}' , '2016-06-22 19:10:25', '2016-06-22 19:10:25'),
  ('542d93d5-6a38-4ce6-95ba-de942ad3b309', 'go away from terrible school' , 'go away from terrible school definition'             , '{}'                   , '2016-06-22 19:10:25', '2016-06-22 19:10:25');

INSERT INTO tags (id, tag, added, updated) VALUES
  ('2afc29d6-f87a-4fd3-9139-bdf5ceb3d8a3', 'grammar', '2016-06-22 19:10:25', '2016-06-22 19:10:25'),
  ('8b5e2c59-18a3-4502-8950-6bd57801fc15', 'noun', '2016-06-22 19:10:25', '2016-06-22 19:10:25'),
  ('b9a68301-bc1b-44f2-a5f8-6f5de86922c3', 'adjective', '2016-06-22 19:10:25', '2016-06-22 19:10:25');

INSERT INTO user_expression (user_id, expression_id, added, updated, properties) VALUES
  ('04aa4f4e-a53e-4b6c-96c5-3604e3fcc4ef', '4d7993aa-d897-4647-994b-e0625c88f349', '2023-04-12 10:10:25', '2023-04-16 10:10:25', '{}'),
  ('04aa4f4e-a53e-4b6c-96c5-3604e3fcc4ef', '542d93d5-6a38-4ce6-95ba-de942ad3b309', '2023-04-09 10:10:25', '2023-04-16 10:10:25', '{}');

INSERT INTO tag_expression (tag_id, expression_id) VALUES
  ('b9a68301-bc1b-44f2-a5f8-6f5de86922c3', '4d7993aa-d897-4647-994b-e0625c88f349'),
  ('8b5e2c59-18a3-4502-8950-6bd57801fc15', '542d93d5-6a38-4ce6-95ba-de942ad3b309');
