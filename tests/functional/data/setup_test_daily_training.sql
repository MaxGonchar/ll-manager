DELETE FROM users;
DELETE FROM expressions;
DELETE FROM user_expression;


-----------------------------
-- test_daily_training_get --
-----------------------------
INSERT INTO users (id, first, last, email, role, password_hash, properties, added, updated, last_login) VALUES -- psw: daily_training
  ('04aa4f4e-a53e-4b6c-96c5-3604e3fcc4ef', 'First', 'Last', 'daily_training@test.mail', 'self-educated', 'c1a4b7e252281a7649d17a0f9f1d5180d5b5b1783dca84e121bbfcadda4ecc12', '{"nativeLang": "uk", "challenges": {"dailyTraining": {"learnListSize": 50, "practiceCountThreshold": 50, "knowledgeLevelThreshold": 0.9, "learning_list": [{"expressionId": "4d7993aa-d897-4647-994b-e0625c88f349", "position": 0, "practiceCount": 0, "knowledgeLevel": 0}, {"expressionId": "24d96f68-46e1-4fb3-b300-81cd89cea435", "position": 0, "practiceCount": 0, "knowledgeLevel": 0}, {"expressionId": "d5c26549-74f7-4930-9c2c-16d10d46e55e", "position": 0, "practiceCount": 0, "knowledgeLevel": 0}]}}}', '2023-04-16 09:10:25', '2023-04-16 09:10:25', '2023-04-16 09:10:25');

INSERT INTO expressions (id, expression, definition, translations, added, updated) VALUES
  ('4d7993aa-d897-4647-994b-e0625c88f349', 'preceding'           , 'coming before something in order, position, or time' , '{"uk": "попередній"}' , '2016-06-22 19:10:25', '2016-06-22 19:10:25'),
  ('24d96f68-46e1-4fb3-b300-81cd89cea435', 'despair'             , 'the complete loss or absence of hope'                , '{"uk": "відчай"}'     , '2016-06-22 19:10:25', '2016-06-22 19:10:25'),
  ('d5c26549-74f7-4930-9c2c-16d10d46e55e', 'annual'              , 'occurring once every year'                           , '{"uk": "щорічний"}'   , '2016-06-22 19:10:25', '2016-06-22 19:10:25');

INSERT INTO user_expression (user_id, expression_id, added, updated, last_practice_time, properties) VALUES
  ('04aa4f4e-a53e-4b6c-96c5-3604e3fcc4ef', '4d7993aa-d897-4647-994b-e0625c88f349', '2023-04-16 10:10:25', '2023-04-16 10:10:25', '2023-04-17', '{}'),
  ('04aa4f4e-a53e-4b6c-96c5-3604e3fcc4ef', '24d96f68-46e1-4fb3-b300-81cd89cea435', '2023-04-16 10:10:25', '2023-04-16 10:10:25', '2023-04-17', '{}'),
  ('04aa4f4e-a53e-4b6c-96c5-3604e3fcc4ef', 'd5c26549-74f7-4930-9c2c-16d10d46e55e', '2023-04-16 10:10:25', '2023-04-16 10:10:25', '2023-04-17', '{}');


-----------------------------
-- test_submit_failed_test --
-----------------------------
INSERT INTO users (id, first, last, email, role, password_hash, properties, added, updated, last_login) VALUES -- psw: daily_training
  ('e0105858-97ef-4a0a-a9d8-c80b89a800a3', 'First', 'Last', 'failed_test@test.mail', 'self-educated', 'c1a4b7e252281a7649d17a0f9f1d5180d5b5b1783dca84e121bbfcadda4ecc12', '{"nativeLang": "uk", "challenges": {"dailyTraining": {"learnListSize": 50, "practiceCountThreshold": 50, "knowledgeLevelThreshold": 0.9, "learning_list": [{"expressionId": "4d7993aa-d897-4647-994b-e0625c88f349", "position": 2, "practiceCount": 0, "knowledgeLevel": 0}, {"expressionId": "24d96f68-46e1-4fb3-b300-81cd89cea435", "position": 0, "practiceCount": 0, "knowledgeLevel": 0}, {"expressionId": "d5c26549-74f7-4930-9c2c-16d10d46e55e", "position": 0, "practiceCount": 0, "knowledgeLevel": 0}]}}}', '2023-04-16 09:10:25', '2023-04-16 09:10:25', '2023-04-16 09:10:25');

INSERT INTO user_expression (user_id, expression_id, knowledge_level, practice_count, added, updated, properties) VALUES
  ('e0105858-97ef-4a0a-a9d8-c80b89a800a3', '4d7993aa-d897-4647-994b-e0625c88f349', 1, 2, '2023-04-16 10:10:25', '2023-04-16 10:10:25', '{}');

INSERT INTO user_expression (user_id, expression_id, added, updated, properties) VALUES
  ('e0105858-97ef-4a0a-a9d8-c80b89a800a3', '24d96f68-46e1-4fb3-b300-81cd89cea435', '2023-04-16 10:10:25', '2023-04-16 10:10:25', '{}'),
  ('e0105858-97ef-4a0a-a9d8-c80b89a800a3', 'd5c26549-74f7-4930-9c2c-16d10d46e55e', '2023-04-16 10:10:25', '2023-04-16 10:10:25', '{}');


---------------------------------------------
-- test_daily_training_get_nothing_to_test --
---------------------------------------------
INSERT INTO users (id, first, last, email, role, password_hash, properties, added, updated, last_login) VALUES -- psw: nothing_to_test
  ('7b211e90-1262-4462-aba8-c765dc045359', 'First', 'Last', 'nothing_to_test@test.mail', 'self-educated', 'ceb4179ee038d28ba21f47c9c896b92ae13c8b4e7a3db4d176c360e1275f98c2', '{"nativeLang": "uk", "challenges": {"dailyTraining": {"learnListSize": 50, "practiceCountThreshold": 50, "knowledgeLevelThreshold": 0.9, "learning_list": []}}}', '2023-04-16 09:10:25', '2023-04-16 09:10:25', '2023-04-16 09:10:25');


-----------------------------------------
-- test_get_daily_training_expressions --
-----------------------------------------
INSERT INTO users (id, first, last, email, role, password_hash, properties, added, updated, last_login) VALUES -- psw: get_daily_training_expressions
  ('ca5e9524-30fc-4948-b167-63b6fe720220', 'First', 'Last', 'get_training_expressions@test.mail', 'self-educated', '70ab2243378b569d195db977aaaaaa096864a9a4cd01ba58584ba5e295600f23', '{"nativeLang": "uk", "challenges": {"dailyTraining": {"learnListSize": 50, "practiceCountThreshold": 50, "knowledgeLevelThreshold": 0.9, "learning_list": [{"expressionId": "4d7993aa-d897-4647-994b-e0625c88f349", "position": "0", "practiceCount": 6, "knowledgeLevel": 0}, {"expressionId": "24d96f68-46e1-4fb3-b300-81cd89cea435", "position": "0", "practiceCount": 9, "knowledgeLevel": 0}, {"expressionId": "d5c26549-74f7-4930-9c2c-16d10d46e55e", "position": "0", "practiceCount": 1, "knowledgeLevel": 0}]}}}', '2023-04-16 09:10:25', '2023-04-16 09:10:25', '2023-04-16 09:10:25');

INSERT INTO user_expression (user_id, expression_id, added, updated, properties, practice_count) VALUES
  ('ca5e9524-30fc-4948-b167-63b6fe720220', '4d7993aa-d897-4647-994b-e0625c88f349', '2023-04-16 10:10:25', '2023-04-16 10:10:25', '{}', 6),
  ('ca5e9524-30fc-4948-b167-63b6fe720220', '24d96f68-46e1-4fb3-b300-81cd89cea435', '2023-04-16 10:10:25', '2023-04-16 10:10:25', '{}', 9),
  ('ca5e9524-30fc-4948-b167-63b6fe720220', 'd5c26549-74f7-4930-9c2c-16d10d46e55e', '2023-04-16 10:10:25', '2023-04-16 10:10:25', '{}', 1);


--------------------------------------------------------
-- test_get_daily_training_expressions_no_expressions --
--------------------------------------------------------
INSERT INTO users (id, first, last, email, role, password_hash, properties, added, updated, last_login) VALUES -- psw: get_daily_training_expressions
  ('9a18dfdd-57b3-41d0-b2f2-682ce8bce316', 'First', 'Last', 'get_training_expressions_no@test.mail', 'self-educated', '70ab2243378b569d195db977aaaaaa096864a9a4cd01ba58584ba5e295600f23', '{"nativeLang": "uk", "challenges": {"dailyTraining": {"learnListSize": 50, "practiceCountThreshold": 50, "knowledgeLevelThreshold": 0.9, "learning_list": []}}}', '2023-04-16 09:10:25', '2023-04-16 09:10:25', '2023-04-16 09:10:25');


-------------------------------------
-- DailyTrainingAddExpressionTests --
-------------------------------------
-------------------------
-- test_add_expression --
-------------------------
INSERT INTO users (id, first, last, email, role, password_hash, properties, added, updated, last_login) VALUES -- psw: test_add_expression
  ('ba2c3934-daa2-48b0-bda5-8e34b412dec7', 'First', 'Last', 'test_add_expression@test.mail', 'self-educated', 'd447c40e3a299cbc63ce5c62a8f49805f4c79e03a2459c1756f8b0b675eb90f0', '{"nativeLang": "uk", "challenges": {"dailyTraining": {"learnListSize": 50, "practiceCountThreshold": 50, "knowledgeLevelThreshold": 0.9, "learning_list": [{"expressionId": "4d7993aa-d897-4647-994b-e0625c88f349", "position": "0", "practiceCount": 1, "knowledgeLevel": 0}, {"expressionId": "24d96f68-46e1-4fb3-b300-81cd89cea435", "position": "1", "practiceCount": 2, "knowledgeLevel": 0}]}}}', '2023-04-16 09:10:25', '2023-04-16 09:10:25', '2023-04-16 09:10:25');

INSERT INTO user_expression (user_id, expression_id, added, updated, properties) VALUES
  ('ba2c3934-daa2-48b0-bda5-8e34b412dec7', '4d7993aa-d897-4647-994b-e0625c88f349', '2023-04-16 10:10:25', '2023-04-16 10:10:25', '{}'),
  ('ba2c3934-daa2-48b0-bda5-8e34b412dec7', '24d96f68-46e1-4fb3-b300-81cd89cea435', '2023-04-16 10:10:24', '2023-04-16 10:10:25', '{}'),
  ('ba2c3934-daa2-48b0-bda5-8e34b412dec7', 'd5c26549-74f7-4930-9c2c-16d10d46e55e', '2023-04-16 10:10:26', '2023-04-16 10:10:25', '{}');


----------------------------------------
-- test_add_expression_to_empty_llist --
----------------------------------------
INSERT INTO users (id, first, last, email, role, password_hash, properties, added, updated, last_login) VALUES -- psw: test_add_expression_to_empty_llist
  ('416b0b33-43e2-4f3c-80bb-0a4bacce9d6f', 'First', 'Last', 'tadd_expression_to_empty_llist@test.mail', 'self-educated', '784c00d3bff14de2e1034a50b683f7db0ab59e4de76761a8b8a3ad65263497b5', '{"nativeLang": "uk", "challenges": {"dailyTraining": {"learnListSize": 50, "practiceCountThreshold": 50, "knowledgeLevelThreshold": 0.9, "learning_list": []}}}', '2023-04-16 09:10:25', '2023-04-16 09:10:25', '2023-04-16 09:10:25');

INSERT INTO user_expression (user_id, expression_id, added, updated, properties) VALUES
  ('416b0b33-43e2-4f3c-80bb-0a4bacce9d6f', 'd5c26549-74f7-4930-9c2c-16d10d46e55e', '2023-04-16 10:10:25', '2023-04-16 10:10:25', '{}');


-----------------------------------------------------------------------
-- test_add_item_to_learn_list_when_llist_has_already_max_size_is_ok --
-----------------------------------------------------------------------
INSERT INTO users (id, first, last, email, role, password_hash, properties, added, updated, last_login) VALUES -- psw: test_add_expression_to_max_llist
  ('ec451b4d-65d9-41dd-9ca3-60cc58a5381b', 'First', 'Last', 'tadd_expression_to_max_llist@test.mail', 'self-educated', '613caade0e37f388a7ef26dfc7703e1745c3bd63e6a730b1dd6f5c1dbc12bfc3', '{"nativeLang": "uk", "challenges": {"dailyTraining": {"learnListSize": 2, "practiceCountThreshold": 50, "knowledgeLevelThreshold": 0.9, "learning_list": [{"expressionId": "4d7993aa-d897-4647-994b-e0625c88f349", "position": "0", "practiceCount": 1, "knowledgeLevel": 0}, {"expressionId": "24d96f68-46e1-4fb3-b300-81cd89cea435", "position": "1", "practiceCount": 2, "knowledgeLevel": 0}]}}}', '2023-04-16 09:10:25', '2023-04-16 09:10:25', '2023-04-16 09:10:25');

INSERT INTO user_expression (user_id, expression_id, added, updated, properties) VALUES
  ('ec451b4d-65d9-41dd-9ca3-60cc58a5381b', '4d7993aa-d897-4647-994b-e0625c88f349', '2023-04-16 10:10:25', '2023-04-16 10:10:25', '{}'),
  ('ec451b4d-65d9-41dd-9ca3-60cc58a5381b', '24d96f68-46e1-4fb3-b300-81cd89cea435', '2023-04-16 10:10:24', '2023-04-16 10:10:25', '{}'),
  ('ec451b4d-65d9-41dd-9ca3-60cc58a5381b', 'd5c26549-74f7-4930-9c2c-16d10d46e55e', '2023-04-16 10:10:26', '2023-04-16 10:10:25', '{}');


----------------------------------------
-- DailyTrainingRemoveExpressionTests --
----------------------------------------
----------------------------
-- test_remove_expression --
----------------------------
INSERT INTO users (id, first, last, email, role, password_hash, properties, added, updated, last_login) VALUES -- psw: test_remove_expression
  ('f2f80eed-9c54-4318-b44f-0c73593c550b', 'First', 'Last', 'test_remove_expression@test.mail', 'self-educated', '866ad70f25bbcfb883bf200ef6b5dfc1cd766dc5b23727b7e96158806d98718b', '{"nativeLang": "uk", "challenges": {"dailyTraining": {"learnListSize": 50, "practiceCountThreshold": 50, "knowledgeLevelThreshold": 0.9, "learning_list": [{"expressionId": "4d7993aa-d897-4647-994b-e0625c88f349", "position": "0", "practiceCount": 0, "knowledgeLevel": 0}, {"expressionId": "d5c26549-74f7-4930-9c2c-16d10d46e55e", "position": "0", "practiceCount": 0, "knowledgeLevel": 0}]}}}', '2023-04-16 09:10:25', '2023-04-16 09:10:25', '2023-04-16 09:10:25');

INSERT INTO user_expression (user_id, expression_id, added, updated, properties) VALUES
  ('f2f80eed-9c54-4318-b44f-0c73593c550b', '4d7993aa-d897-4647-994b-e0625c88f349', '2023-04-16 10:10:25', '2023-04-16 10:10:25', '{}'),
  ('f2f80eed-9c54-4318-b44f-0c73593c550b', 'd5c26549-74f7-4930-9c2c-16d10d46e55e', '2023-04-16 10:10:25', '2023-04-16 10:10:25', '{}');


--------------------------------------
-- DailyTrainingUpdateSettingsTests --
--------------------------------------
-----------------------
-- test_get_settings --
-----------------------
INSERT INTO users (id, first, last, email, role, password_hash, properties, added, updated, last_login) VALUES -- psw: test_get_settings
  ('1c57cf5b-d6c4-4bc4-8d49-d2ff88753bbc', 'First', 'Last', 'test_get_settings@test.mail', 'self-educated', '8cee08faa805de637d5e0a5945a91e429ef2772cfdc8efabba9722481c64b9e6', '{"nativeLang": "uk", "challenges": {"dailyTraining": {"learnListSize": 3, "practiceCountThreshold": 50, "knowledgeLevelThreshold": 0.9, "learning_list": [{"expressionId": "4d7993aa-d897-4647-994b-e0625c88f349", "position": 1, "practiceCount": 3, "knowledgeLevel": 0.3}, {"expressionId": "24d96f68-46e1-4fb3-b300-81cd89cea435", "position": 2, "practiceCount": 6, "knowledgeLevel": 0.4}, {"expressionId": "d5c26549-74f7-4930-9c2c-16d10d46e55e", "position": 3, "practiceCount": 7, "knowledgeLevel": 0.5}]}}}', '2023-04-16 09:10:25', '2023-04-16 09:10:25', '2023-04-16 09:10:25');

INSERT INTO expressions (id, expression, definition, translations, added, updated) VALUES
  ('4eb806c0-a8cd-4ac9-8387-1b79cb97b138', 'show of hands'       , 'a vote carried out among a group by the raising of hands',                                                    '{"uk": "підняття рук"}', '2016-06-22 19:10:25', '2016-06-22 19:10:25'),
  ('a0a68135-bc73-4025-a754-966450fa6cac', 'doubtfully'          , 'feeling uncertain about something',                                                                           '{"uk": "сумнівно"}',     '2016-06-22 19:10:25', '2016-06-22 19:10:25'),
  ('4a2e0dc8-d1e0-4814-a91e-0c9bc6a9f22e', 'scrap metal'         , 'a small piece or amount of something, especially one that is left over after the greater part has been used', '{"uk": "металобрухт"}',  '2016-06-22 19:10:25', '2016-06-22 19:10:25');

INSERT INTO user_expression (user_id, expression_id, added, updated, last_practice_time, properties) VALUES
  ('1c57cf5b-d6c4-4bc4-8d49-d2ff88753bbc', '4d7993aa-d897-4647-994b-e0625c88f349', '2023-04-16 10:10:25', '2023-04-16 10:10:25', '2023-04-17', '{}'),
  ('1c57cf5b-d6c4-4bc4-8d49-d2ff88753bbc', '24d96f68-46e1-4fb3-b300-81cd89cea435', '2023-04-16 10:10:24', '2023-04-16 10:10:25', '2023-04-17', '{}'),
  ('1c57cf5b-d6c4-4bc4-8d49-d2ff88753bbc', 'd5c26549-74f7-4930-9c2c-16d10d46e55e', '2023-04-16 10:10:23', '2023-04-16 10:10:25', '2023-04-17', '{}'),
  ('1c57cf5b-d6c4-4bc4-8d49-d2ff88753bbc', '4eb806c0-a8cd-4ac9-8387-1b79cb97b138', '2023-04-16 10:10:22', '2023-04-16 10:10:25', null, '{}'),
  ('1c57cf5b-d6c4-4bc4-8d49-d2ff88753bbc', 'a0a68135-bc73-4025-a754-966450fa6cac', '2023-04-16 10:10:21', '2023-04-16 10:10:25', null, '{}'),
  ('1c57cf5b-d6c4-4bc4-8d49-d2ff88753bbc', '4a2e0dc8-d1e0-4814-a91e-0c9bc6a9f22e', '2023-04-16 10:10:20', '2023-04-16 10:10:25', null, '{}');
