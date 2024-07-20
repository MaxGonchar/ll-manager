DELETE FROM users;
DELETE FROM expressions;
DELETE FROM user_expression;


INSERT INTO expressions (id, expression, definition, translations, added, updated) VALUES
  ('4d7993aa-d897-4647-994b-e0625c88f349', 'preceding'           , 'coming before something in order, position, or time' , '{"uk": "попередній"}' , '2016-06-22 19:10:25', '2016-06-22 19:10:25'),
  ('24d96f68-46e1-4fb3-b300-81cd89cea435', 'despair'             , 'the complete loss or absence of hope'                , '{"uk": "відчай"}'     , '2016-06-22 19:10:25', '2016-06-22 19:10:25'),
  ('d5c26549-74f7-4930-9c2c-16d10d46e55e', 'annual'              , 'occurring once every year'                           , '{"uk": "щорічний"}'   , '2016-06-22 19:10:25', '2016-06-22 19:10:25');


------------------------
-- test_get_challenge --
------------------------
INSERT INTO users (id, first, last, email, role, password_hash, properties, added, updated, last_login) VALUES -- psw: expression_recall_1
  ('04aa4f4e-a53e-4b6c-96c5-3604e3fcc4ef', 'First', 'Last', 'expression_recall_1@test.mail', 'self-educated', '82dc5fa2bcd2655ceed2aa9288f8b6a21da2ca7c3efe010b8973a3372a23a9c5', '{"nativeLang": "uk", "challenges": {"dailyTraining": {"learnListSize": 50, "practiceCountThreshold": 50, "knowledgeLevelThreshold": 0.9, "learning_list": [{"expressionId": "4d7993aa-d897-4647-994b-e0625c88f349", "position": 0, "practiceCount": 0, "knowledgeLevel": "0"}, {"expressionId": "24d96f68-46e1-4fb3-b300-81cd89cea435", "position": 0, "practiceCount": 0, "knowledgeLevel": "0"}, {"expressionId": "d5c26549-74f7-4930-9c2c-16d10d46e55e", "position": 0, "practiceCount": 0, "knowledgeLevel": "0"}]}}}', '2023-04-16 09:10:25', '2023-04-16 09:10:25', '2023-04-16 09:10:25');

INSERT INTO user_expression (user_id, expression_id, added, updated, last_practice_time, knowledge_level, practice_count, properties) VALUES
  ('04aa4f4e-a53e-4b6c-96c5-3604e3fcc4ef', '4d7993aa-d897-4647-994b-e0625c88f349', '2023-04-16 10:10:25', '2023-04-16 10:10:25', '2023-04-15 10:10:25', 0,   0, '{}'),
  ('04aa4f4e-a53e-4b6c-96c5-3604e3fcc4ef', '24d96f68-46e1-4fb3-b300-81cd89cea435', '2023-04-16 10:10:25', '2023-04-16 10:10:25', '2023-04-14 10:10:25', 0.5, 9, '{}'),
  ('04aa4f4e-a53e-4b6c-96c5-3604e3fcc4ef', 'd5c26549-74f7-4930-9c2c-16d10d46e55e', '2023-04-16 10:10:25', '2023-04-16 10:10:25', NULL,                  0,   0, '{}');


------------------------------------------
-- test_get_challenge_nothing_to_recall --
------------------------------------------
INSERT INTO users (id, first, last, email, role, password_hash, properties, added, updated, last_login) VALUES -- psw: expression_recall_2
  ('ad1a54e9-baa2-4dfc-8b9d-2a884306fa21', 'First', 'Last', 'expression_recall_2@test.mail', 'self-educated', 'cfda86f7cdcf09ed32a9d2f3c23c022a660432b9ac468d8bcd93b501fab3cf8f', '{"nativeLang": "uk", "challenges": {"dailyTraining": {"learnListSize": 50, "practiceCountThreshold": 50, "knowledgeLevelThreshold": 0.9, "learning_list": [{"expressionId": "4d7993aa-d897-4647-994b-e0625c88f349", "position": 0, "practiceCount": 0, "knowledgeLevel": "0"}, {"expressionId": "24d96f68-46e1-4fb3-b300-81cd89cea435", "position": 0, "practiceCount": 0, "knowledgeLevel": "0"}, {"expressionId": "d5c26549-74f7-4930-9c2c-16d10d46e55e", "position": 0, "practiceCount": 0, "knowledgeLevel": "0"}]}}}', '2023-04-16 09:10:25', '2023-04-16 09:10:25', '2023-04-16 09:10:25');

INSERT INTO user_expression (user_id, expression_id, added, updated, last_practice_time, properties) VALUES
  ('ad1a54e9-baa2-4dfc-8b9d-2a884306fa21', '4d7993aa-d897-4647-994b-e0625c88f349', '2023-04-16 10:10:25', '2023-04-16 10:10:25', NULL, '{}'),
  ('ad1a54e9-baa2-4dfc-8b9d-2a884306fa21', '24d96f68-46e1-4fb3-b300-81cd89cea435', '2023-04-16 10:10:25', '2023-04-16 10:10:25', NULL, '{}'),
  ('ad1a54e9-baa2-4dfc-8b9d-2a884306fa21', 'd5c26549-74f7-4930-9c2c-16d10d46e55e', '2023-04-16 10:10:25', '2023-04-16 10:10:25', NULL, '{}');
