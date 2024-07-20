DELETE FROM parts;
DELETE FROM tag_expression;
DELETE FROM tags;
DELETE FROM users;
DELETE FROM expressions;
DELETE FROM user_expression;

INSERT INTO expressions (id, expression, definition, translations, added, updated) VALUES
  ('4d7993aa-d897-4647-994b-e0625c88f349', 'preceding'           , 'coming before something in order, position, or time'                                                                                 , '{"uk": "попередній"}'                          , '2016-06-22 19:10:25', '2016-06-22 19:10:25'),
  ('24d96f68-46e1-4fb3-b300-81cd89cea435', 'despair'             , 'the complete loss or absence of hope'                                                                                                , '{"uk": "відчай"}'                          , '2016-06-22 19:10:25', '2016-06-22 19:10:25'),
  ('d5c26549-74f7-4930-9c2c-16d10d46e55e', 'annual'              , 'occurring once every year'                                                                                                           , '{"uk": "щорічний"}'                          , '2016-06-22 19:10:25', '2016-06-22 19:10:25'),
  ('4eb806c0-a8cd-4ac9-8387-1b79cb97b138', 'show of hands'       , 'a vote carried out among a group by the raising of hands'                                                                            , '{"uk": "підняття рук"}'                          , '2016-06-22 19:10:25', '2016-06-22 19:10:25'),
  ('a0a68135-bc73-4025-a754-966450fa6cac', 'doubtfully'          , 'feeling uncertain about something'                                                                                                   , '{"uk": "сумнівно"}'                          , '2016-06-22 19:10:25', '2016-06-22 19:10:25'),
  ('4a2e0dc8-d1e0-4814-a91e-0c9bc6a9f22e', 'scrap metal'         , 'a small piece or amount of something, especially one that is left over after the greater part has been used'                         , '{"uk": "металобрухт"}'                          , '2016-06-22 19:10:25', '2016-06-22 19:10:25'),
  ('701709f4-6ff4-468a-b2ce-af29940cc3b9', 'end up'              , 'to reach or come to a place, condition, or situation that was not planned or expected'                                               , '{"uk": "закінчити"}'                          , '2016-06-22 19:10:25', '2016-06-22 19:10:25'),
  ('93ee7a1a-156f-48ea-884b-c75f4333544f', 'delightfully'        , 'in a manner that causes great pleasure; charmingly'                                                                                  , '{"uk": "чудово"}'                          , '2016-06-22 19:10:25', '2016-06-22 19:10:25'),
  ('a34074ad-acaf-49b4-b3c9-8e4eabdd5ad0', 'sick and tired of'   , 'annoyed about or bored with (someone or something) and unwilling to put up with them any longer'                                     , '{"uk": "набридло"}'          , '2016-06-22 19:10:25', '2016-06-22 19:10:25'),
  ('1ec00a47-5b03-43f6-926f-c304671d7c9b', 'although'            , 'in spite of the fact that; even though'                                                                                              , '{"uk": "незважаючи на те, що"}'                          , '2016-06-22 19:10:25', '2016-06-22 19:10:25'),
  ('7f60f6cc-c80a-40da-968c-3d162a598626', 'preceding despair'   , 'the coming before something in order, position, or time complete loss or absence of hope'                                            , '{}'                          , '2016-06-22 19:10:25', '2016-06-22 19:10:25'),
  ('db69dbce-805c-434a-b699-54bca998705f', 'annual show of hands', 'a vote carried out among a group by the raising of hands that is occurring once every year'                                          , '{}'                          , '2016-06-22 19:10:25', '2016-06-22 19:10:25'),
  ('4a10e583-a209-42d2-a08d-a359c63b7adc', 'inherent repugnance' , 'existing in something as a permanent, essential, or characteristic attribute intense disgust'                                        , '{"uk": "притаманна огида"}'  , '2016-06-22 19:10:25', '2016-06-22 19:10:25'),
  ('92fcf355-2745-42e8-be6a-5b67d3fe0376', 'rapid delight'       , 'happening in a short time or at a great rate great pleasure'                                                                         , '{"uk": "швидке задоволення"}', '2016-06-22 19:10:25', '2016-06-22 19:10:25'),
  ('cb80f8ac-572d-4b43-8cee-1a22c2759131', 'creature of habit'   , 'used to say one always does the same things in the same way'                                                                         , '{}'                          , '2016-06-22 19:10:25', '2016-06-22 19:10:25'),
  ('8fea0d7f-2005-4aa6-a25d-b00f7fea4391', 'beat about the bush' , 'discuss a matter without coming to the point'                                                                                        , '{}'                          , '2016-06-22 19:10:25', '2016-06-22 19:10:25'),
  ('478dc2c1-4106-43ce-986c-802971c53153', 'inn'                 , 'a pub, typically one in the country, in some cases providing accommodation'                                                          , '{}'                          , '2016-06-22 19:10:25', '2016-06-22 19:10:25'),
  ('9567dde5-5580-4efb-ba05-c8d8c66a7a7b', 'assertive big cheese', 'having or showing a confident and forceful personality important, influential person'                                                , '{}'                          , '2016-06-22 19:10:25', '2016-06-22 19:10:25'),
  ('6ba673bc-cb77-4d19-8c93-f72fb1a0a003', 'scoop'               , 'a piece of news published by a newspaper or broadcast by a television or radio station in advance of its rivals'                     , '{}'                          , '2023-03-25 15:13:23', '2023-03-25 15:13:23'),
  ('ef57a74d-869c-4e87-bae9-a36ee43b28ed', 'brittle'             , 'hard but liable to break easily'                                                                                                     , '{}'                          , '2023-03-25 15:13:23', '2023-03-25 15:13:23'),
  ('cba6423e-fd91-41df-b039-46f9cd1c73c0', 'wilfully'            , 'with the intention of causing harm; deliberately'                                                                                    , '{}'                          , '2023-03-25 15:13:23', '2023-03-25 15:13:23'),
  ('65f0e40d-835d-4675-ab1e-cdd5ed40059c', 'tenacity'            , 'the quality or fact of being able to grip something firmly'                                                                          , '{}'                          , '2023-03-25 15:13:23', '2023-03-25 15:13:23'),
  ('30ffb978-ec48-4805-8f13-8655b0a3c00d', 'quill'               , 'the hollow sharp spines of a porcupine, hedgehog, or other spiny mammal'                                                             , '{}'                          , '2023-03-25 15:13:23', '2023-03-25 15:13:23'),
  ('4fcce2f6-66e3-4d34-81b2-5500af426a58', 'doom-monger'         , 'a person who predicts disaster'                                                                                                      , '{}'                          , '2023-03-25 15:13:23', '2023-03-25 15:13:23'),
  ('43c5220f-1a31-4177-acac-055915539e61', 'incline'             , 'be favourably disposed towards or willing to do something'                                                                           , '{}'                          , '2023-03-25 15:13:23', '2023-03-25 15:13:23'),
  ('7a437618-792e-433a-9c8d-0651d10dd64a', 'surpass'             , 'exceed; be greater than'                                                                                                             , '{}'                          , '2023-03-25 15:13:23', '2023-03-25 15:13:23'),
  ('c0b29d7a-dfb4-455a-b0bc-57cfa6518fe2', 'abnormally'          , 'in a manner that deviates from what is normal or usual; irregularly or extraordinarily'                                              , '{}'                          , '2023-03-25 15:13:23', '2023-03-25 15:13:23'),
  ('3e4e2e9f-1733-4d39-9f3f-35779e9d65a2', 'sullen'              , 'bad-tempered and sulky'                                                                                                              , '{}'                          , '2023-03-25 15:13:23', '2023-03-25 15:13:23'),
  ('96b72448-6832-440f-89ad-e7a5d77556be', 'excess'              , 'an amount of something that is more than necessary, permitted, or desirable'                                                         , '{}'                          , '2023-03-25 15:13:23', '2023-03-25 15:13:23'),
  ('0c4045e1-7df1-4728-b16f-9c9f6d79c707', 'keep schtum'         , 'to not say anything about something'                                                                                                 , '{}'                          , '2023-03-25 15:13:23', '2023-03-25 15:13:23'),
  ('85adc9f1-fa25-4513-a7d7-e5f7a9b1d7ab', 'reluctant'           , 'unwilling and hesitant; disinclined'                                                                                                 , '{}'                          , '2023-03-25 15:13:23', '2023-03-25 15:13:23'),
  ('6f1d0d71-8671-490a-8dbc-b79271f6798d', 'distraught'          , 'very worried and upset'                                                                                                              , '{}'                          , '2023-03-25 15:13:23', '2023-03-25 15:13:23'),
  ('497b1b83-b09b-4803-8dca-b00b3780dfd4', 'oppressed'           , 'subject to harsh and authoritarian treatment'                                                                                        , '{}'                          , '2023-03-25 15:13:23', '2023-03-25 15:13:23'),
  ('d477e1cf-ce75-48ed-ab8a-d4ffdd1a9d32', 'elongated'           , 'long in relation to width, especially unusually so'                                                                                  , '{}'                          , '2023-03-25 15:13:23', '2023-03-25 15:13:23'),
  ('575fa6d5-4610-480e-aa5d-bb80374fdd60', 'praise'              , 'the expression of approval or admiration for someone or something'                                                                   , '{}'                          , '2023-03-25 15:13:23', '2023-03-25 15:13:23'),
  ('3e558543-5600-4787-bff3-c2f38c03e07c', 'flogging'            , 'a punishment in which the victim is hit repeatedly with a whip or stick'                                                             , '{}'                          , '2023-03-25 15:13:23', '2023-03-25 15:13:23'),
  ('2471778b-3303-43fe-8be2-870b3f5cc1a9', 'hail'                , 'pellets of frozen rain which fall in showers from cumulonimbus clouds'                                                               , '{}'                          , '2023-03-25 15:13:23', '2023-03-25 15:13:23'),
  ('f35d073f-703e-4bf1-9740-abb8f8af7736', 'disproportionate'    , 'too large or too small in comparison with something else'                                                                            , '{}'                          , '2023-03-25 15:13:23', '2023-03-25 15:13:23'),
  ('8ebd46e8-2e6d-43d9-9210-a2b07fa7a504', 'divulge'             , 'make known'                                                                                                                          , '{}'                          , '2023-03-25 15:13:23', '2023-03-25 15:13:23'),
  ('d9d3ec66-de1e-426e-9950-57c708e055e5', 'webbed'              , 'having the toes connected by a membrane'                                                                                             , '{}'                          , '2023-03-25 15:13:23', '2023-03-25 15:13:23'),
  ('f042f193-e6f9-42d2-98a6-b92b13e7d002', 'stipulation'         , 'a condition or requirement that is specified or demanded as part of an agreement'                                                    , '{}'                          , '2023-03-25 15:13:23', '2023-03-25 15:13:23'),
  ('f7820ec3-f854-4a20-834d-faf348a80e40', 'opposition'          , 'resistance or dissent, expressed in action or argument'                                                                              , '{}'                          , '2023-03-25 15:13:23', '2023-03-25 15:13:23'),
  ('ab8796c1-3780-4c09-b6cd-688b583ef416', 'hush-hush'           , 'highly secret or confidential'                                                                                                       , '{}'                          , '2023-03-25 15:13:23', '2023-03-25 15:13:23'),
  ('706d12d6-0d19-4e5e-ba3c-27a428b37b6c', 'carry out'           , 'perform a task'                                                                                                                      , '{}'                          , '2023-03-25 15:13:23', '2023-03-25 15:13:23'),
  ('358fc969-14ba-4f09-99fb-3274ef671358', 'impaired'            , 'weakened or damaged'                                                                                                                 , '{}'                          , '2023-03-25 15:13:23', '2023-03-25 15:13:23'),
  ('a2d60e73-fab7-4221-9ef4-307a3400620c', 'cloak'               , 'a sleeveless outdoor overgarment that hangs loosely from the shoulders'                                                              , '{}'                          , '2023-03-25 15:13:23', '2023-03-25 15:13:23'),
  ('4b3588df-b14b-4d7f-a910-c7b048b3d773', 'confessional'        , 'in which a person reveals private thoughts or admits to past incidents, especially ones about which they feel ashamed or embarrassed', '{}'                          , '2023-03-25 15:13:23', '2023-03-25 15:13:23'),
  ('cfb924f4-b403-450b-9edd-1aed677e5c51', 'compulsory'          , 'required by law or a rule; obligatory'                                                                                               , '{}'                          , '2023-03-25 15:13:23', '2023-03-25 15:13:23');

INSERT INTO tags (id, tag, added, updated) VALUES
  ('c70a5101-b51a-443a-8b93-33e37bbda653', 'phrase', '2016-06-22 19:10:25', '2016-06-22 19:10:25'),
  ('8b5e2c59-18a3-4502-8950-6bd57801fc15', 'noun', '2016-06-22 19:10:25', '2016-06-22 19:10:25'),
  ('c3fdf17d-a764-4832-92bc-4970ac0cb317', 'verb', '2016-06-22 19:10:25', '2016-06-22 19:10:25'),
  ('b9a68301-bc1b-44f2-a5f8-6f5de86922c3', 'adjective', '2016-06-22 19:10:25', '2016-06-22 19:10:25'),
  ('b6de92a9-88bc-4237-a60a-33cac9086be9', 'adverb', '2016-06-22 19:10:25', '2016-06-22 19:10:25'),
  ('33b0144f-0a31-4e91-ac5a-ddcab55d1f2f', 'conjunction', '2016-06-22 19:10:25', '2016-06-22 19:10:25'),
  ('8eeb8975-d28f-4196-8f7e-1b75068c7142', 'idiom', '2016-06-22 19:10:25', '2016-06-22 19:10:25');

INSERT INTO tag_expression (tag_id, expression_id) VALUES
  ('c70a5101-b51a-443a-8b93-33e37bbda653', 'a34074ad-acaf-49b4-b3c9-8e4eabdd5ad0'),
  ('c70a5101-b51a-443a-8b93-33e37bbda653', '4a2e0dc8-d1e0-4814-a91e-0c9bc6a9f22e'),
  ('c70a5101-b51a-443a-8b93-33e37bbda653', '4eb806c0-a8cd-4ac9-8387-1b79cb97b138'),
  ('c70a5101-b51a-443a-8b93-33e37bbda653', '8fea0d7f-2005-4aa6-a25d-b00f7fea4391'),
  ('c70a5101-b51a-443a-8b93-33e37bbda653', 'cb80f8ac-572d-4b43-8cee-1a22c2759131'),
  ('c70a5101-b51a-443a-8b93-33e37bbda653', '92fcf355-2745-42e8-be6a-5b67d3fe0376'),
  ('c70a5101-b51a-443a-8b93-33e37bbda653', '4a10e583-a209-42d2-a08d-a359c63b7adc'),
  ('c70a5101-b51a-443a-8b93-33e37bbda653', 'db69dbce-805c-434a-b699-54bca998705f'),
  ('c70a5101-b51a-443a-8b93-33e37bbda653', '7f60f6cc-c80a-40da-968c-3d162a598626'),
  ('8b5e2c59-18a3-4502-8950-6bd57801fc15', '7f60f6cc-c80a-40da-968c-3d162a598626'),
  ('8b5e2c59-18a3-4502-8950-6bd57801fc15', 'db69dbce-805c-434a-b699-54bca998705f'),
  ('8b5e2c59-18a3-4502-8950-6bd57801fc15', '4a10e583-a209-42d2-a08d-a359c63b7adc'),
  ('8b5e2c59-18a3-4502-8950-6bd57801fc15', '92fcf355-2745-42e8-be6a-5b67d3fe0376'),
  ('8b5e2c59-18a3-4502-8950-6bd57801fc15', 'cb80f8ac-572d-4b43-8cee-1a22c2759131'),
  ('8b5e2c59-18a3-4502-8950-6bd57801fc15', '24d96f68-46e1-4fb3-b300-81cd89cea435'),
  ('8b5e2c59-18a3-4502-8950-6bd57801fc15', '4eb806c0-a8cd-4ac9-8387-1b79cb97b138'),
  ('8b5e2c59-18a3-4502-8950-6bd57801fc15', '4a2e0dc8-d1e0-4814-a91e-0c9bc6a9f22e'),
  ('c3fdf17d-a764-4832-92bc-4970ac0cb317', '701709f4-6ff4-468a-b2ce-af29940cc3b9'),
  ('c3fdf17d-a764-4832-92bc-4970ac0cb317', '8fea0d7f-2005-4aa6-a25d-b00f7fea4391'),
  ('b9a68301-bc1b-44f2-a5f8-6f5de86922c3', 'd5c26549-74f7-4930-9c2c-16d10d46e55e'),
  ('b9a68301-bc1b-44f2-a5f8-6f5de86922c3', '4d7993aa-d897-4647-994b-e0625c88f349'),
  ('b6de92a9-88bc-4237-a60a-33cac9086be9', '93ee7a1a-156f-48ea-884b-c75f4333544f'),
  ('b6de92a9-88bc-4237-a60a-33cac9086be9', 'a0a68135-bc73-4025-a754-966450fa6cac'),
  ('33b0144f-0a31-4e91-ac5a-ddcab55d1f2f', '1ec00a47-5b03-43f6-926f-c304671d7c9b'),
  ('8eeb8975-d28f-4196-8f7e-1b75068c7142', '8fea0d7f-2005-4aa6-a25d-b00f7fea4391'),
  ('8eeb8975-d28f-4196-8f7e-1b75068c7142', 'cb80f8ac-572d-4b43-8cee-1a22c2759131');

INSERT INTO parts (expression_id, part_id) VALUES
  ('7f60f6cc-c80a-40da-968c-3d162a598626', '4d7993aa-d897-4647-994b-e0625c88f349'),
  ('7f60f6cc-c80a-40da-968c-3d162a598626', '24d96f68-46e1-4fb3-b300-81cd89cea435'),
  ('db69dbce-805c-434a-b699-54bca998705f', 'd5c26549-74f7-4930-9c2c-16d10d46e55e'),
  ('db69dbce-805c-434a-b699-54bca998705f', '4eb806c0-a8cd-4ac9-8387-1b79cb97b138');

INSERT INTO users (id, first, last, email, role, password_hash, properties, added, updated, last_login) VALUES -- psw: qwe123
  ('5a5721b9-ead3-4ac7-9dc6-c6b85eea2273', 'First', 'Last', 'first@test.mail', 'self-educated', '18138372fad4b94533cd4881f03dc6c69296dd897234e0cee83f727e2e6b1f63', '{"nativeLang": "uk"}', '2023-04-16 09:10:25', '2023-04-16 09:10:25', '2023-04-16 09:10:25');

INSERT INTO user_expression (user_id, expression_id, added, updated, properties) VALUES
  ('5a5721b9-ead3-4ac7-9dc6-c6b85eea2273', '4d7993aa-d897-4647-994b-e0625c88f349', '2023-04-16 10:10:25', '2023-04-16 10:10:25', '{}'),
  ('5a5721b9-ead3-4ac7-9dc6-c6b85eea2273', '24d96f68-46e1-4fb3-b300-81cd89cea435', '2023-04-16 10:10:25', '2023-04-16 10:10:25', '{}'),
  ('5a5721b9-ead3-4ac7-9dc6-c6b85eea2273', 'd5c26549-74f7-4930-9c2c-16d10d46e55e', '2023-04-16 10:10:25', '2023-04-16 10:10:25', '{}'),
  ('5a5721b9-ead3-4ac7-9dc6-c6b85eea2273', '4eb806c0-a8cd-4ac9-8387-1b79cb97b138', '2023-04-16 10:10:25', '2023-04-16 10:10:25', '{}'),
  ('5a5721b9-ead3-4ac7-9dc6-c6b85eea2273', 'a0a68135-bc73-4025-a754-966450fa6cac', '2023-04-16 10:10:25', '2023-04-16 10:10:25', '{}'),
  ('5a5721b9-ead3-4ac7-9dc6-c6b85eea2273', '4a2e0dc8-d1e0-4814-a91e-0c9bc6a9f22e', '2023-04-16 10:10:25', '2023-04-16 10:10:25', '{}'),
  ('5a5721b9-ead3-4ac7-9dc6-c6b85eea2273', '701709f4-6ff4-468a-b2ce-af29940cc3b9', '2023-04-16 10:10:25', '2023-04-16 10:10:25', '{}'),
  ('5a5721b9-ead3-4ac7-9dc6-c6b85eea2273', '93ee7a1a-156f-48ea-884b-c75f4333544f', '2023-04-16 10:10:25', '2023-04-16 10:10:25', '{}'),
  ('5a5721b9-ead3-4ac7-9dc6-c6b85eea2273', 'a34074ad-acaf-49b4-b3c9-8e4eabdd5ad0', '2023-04-16 10:10:25', '2023-04-16 10:10:25', '{}'),
  ('5a5721b9-ead3-4ac7-9dc6-c6b85eea2273', '1ec00a47-5b03-43f6-926f-c304671d7c9b', '2023-04-16 10:10:25', '2023-04-16 10:10:25', '{}'),
  ('5a5721b9-ead3-4ac7-9dc6-c6b85eea2273', '7f60f6cc-c80a-40da-968c-3d162a598626', '2023-04-16 10:10:25', '2023-04-16 10:10:25', '{}'),
  ('5a5721b9-ead3-4ac7-9dc6-c6b85eea2273', 'db69dbce-805c-434a-b699-54bca998705f', '2023-04-16 10:10:25', '2023-04-16 10:10:25', '{}'),
  ('5a5721b9-ead3-4ac7-9dc6-c6b85eea2273', '4a10e583-a209-42d2-a08d-a359c63b7adc', '2023-04-16 10:10:25', '2023-04-16 10:10:25', '{}');
