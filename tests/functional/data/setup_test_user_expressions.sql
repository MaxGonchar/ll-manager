DELETE FROM users;
DELETE FROM expressions;
DELETE FROM user_expression;

INSERT INTO users (id, first, last, email, role, password_hash, properties, added, updated, last_login) VALUES -- psw: daily_training
  ('04aa4f4e-a53e-4b6c-96c5-3604e3fcc4ef', 'First', 'Last', 'daily_training@test.mail', 'self-educated', 'c1a4b7e252281a7649d17a0f9f1d5180d5b5b1783dca84e121bbfcadda4ecc12', '{"nativeLang": "uk", "challenges": {"dailyTraining": {"learnListSize": 50, "practiceCountThreshold": 50, "knowledgeLevelThreshold": 0.9, "learning_list": [{"expressionId": "4d7993aa-d897-4647-994b-e0625c88f349", "position": 0, "practiceCount": 0, "knowledgeLevel": "0"}, {"expressionId": "24d96f68-46e1-4fb3-b300-81cd89cea435", "position": 0, "practiceCount": 0, "knowledgeLevel": "0"}, {"expressionId": "d5c26549-74f7-4930-9c2c-16d10d46e55e", "position": 0, "practiceCount": 0, "knowledgeLevel": "0"}]}}}', '2023-04-16 09:10:25', '2023-04-16 09:10:25', '2023-04-16 09:10:25');

INSERT INTO expressions (id, expression, definition, translations, added, updated) VALUES
  ('4d7993aa-d897-4647-994b-e0625c88f349', 'preceding'                    , 'coming before something in order, position, or time'      , '{"uk": "попередній"}'   , '2016-06-22 19:10:25', '2016-06-22 19:10:25'),
  ('24d96f68-46e1-4fb3-b300-81cd89cea435', 'despair'                      , 'the complete loss or absence of hope'                     , '{"uk": "відчай"}'       , '2016-06-22 19:10:25', '2016-06-22 19:10:25'),
  ('d5c26549-74f7-4930-9c2c-16d10d46e55e', 'annual'                       , 'occurring once every year'                                , '{"uk": "щорічний"}'     , '2016-06-22 19:10:25', '2016-06-22 19:10:25'),
  ('4eb806c0-a8cd-4ac9-8387-1b79cb97b138', 'show of hands'                , 'a vote carried out among a group by the raising of hands' , '{"uk": "підняття рук"}' , '2016-06-22 19:10:25', '2016-06-22 19:10:25'),
  ('a0a68135-bc73-4025-a754-966450fa6cac', 'doubtfully'                   , 'feeling uncertain about something'                        , '{"uk": "сумнівно"}'     , '2016-06-22 19:10:25', '2016-06-22 19:10:25'),

  ('b02dcda4-65ae-45ba-a2d7-0502fae3d08a', 'go to school'                 , 'go to school definition'                 , '{}'     , '2016-06-22 19:10:25', '2016-06-22 19:10:25'),
  ('66c21b88-3e73-471a-9776-9b691978e650', 'school to go'                 , 'school to go definition'                 , '{}'     , '2016-06-22 19:10:25', '2016-06-22 19:10:25'),
  ('eaf0a44f-abb2-4ddd-98d0-8944c163dae5', 'go away'                      , 'go away definition'                      , '{}'     , '2016-06-22 19:10:25', '2016-06-22 19:10:25'),
  ('53c2fc3c-0a99-477d-9feb-3a07792eaf86', 'terrible school'              , 'terrible school definition'              , '{}'     , '2016-06-22 19:10:25', '2016-06-22 19:10:25'),
  ('542d93d5-6a38-4ce6-95ba-de942ad3b309', 'go away from terrible school' , 'go away from terrible school definition' , '{}'     , '2016-06-22 19:10:25', '2016-06-22 19:10:25');

INSERT INTO user_expression (user_id, expression_id, added, updated, properties) VALUES
  ('04aa4f4e-a53e-4b6c-96c5-3604e3fcc4ef', '4d7993aa-d897-4647-994b-e0625c88f349', '2023-04-12 10:10:25', '2023-04-16 10:10:25', '{}'),
  ('04aa4f4e-a53e-4b6c-96c5-3604e3fcc4ef', '24d96f68-46e1-4fb3-b300-81cd89cea435', '2023-04-14 10:10:25', '2023-04-16 10:10:25', '{}'),
  ('04aa4f4e-a53e-4b6c-96c5-3604e3fcc4ef', 'd5c26549-74f7-4930-9c2c-16d10d46e55e', '2023-04-13 10:10:25', '2023-04-16 10:10:25', '{}'),
  ('04aa4f4e-a53e-4b6c-96c5-3604e3fcc4ef', '4eb806c0-a8cd-4ac9-8387-1b79cb97b138', '2023-04-15 10:10:25', '2023-04-16 10:10:25', '{}'),
  ('04aa4f4e-a53e-4b6c-96c5-3604e3fcc4ef', 'a0a68135-bc73-4025-a754-966450fa6cac', '2023-04-16 10:10:25', '2023-04-16 10:10:25', '{}'),
  ('04aa4f4e-a53e-4b6c-96c5-3604e3fcc4ef', 'b02dcda4-65ae-45ba-a2d7-0502fae3d08a', '2023-04-11 10:10:25', '2023-04-16 10:10:25', '{}'),
  ('04aa4f4e-a53e-4b6c-96c5-3604e3fcc4ef', 'eaf0a44f-abb2-4ddd-98d0-8944c163dae5', '2023-04-10 10:10:25', '2023-04-16 10:10:25', '{}'),
  ('04aa4f4e-a53e-4b6c-96c5-3604e3fcc4ef', '542d93d5-6a38-4ce6-95ba-de942ad3b309', '2023-04-09 10:10:25', '2023-04-16 10:10:25', '{}');
