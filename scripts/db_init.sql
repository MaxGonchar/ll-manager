-- table for words, phrases, sentences, etc.
CREATE TABLE IF NOT EXISTS expressions (
    id            uuid PRIMARY KEY,
    expression    TEXT NOT NULL,
    definition    TEXT,
    example       TEXT,
    translations  json NOT NULL,
    added         TIMESTAMP NOT NULL,
    updated       TIMESTAMP NOT NULL,
    properties    json NOT NULL DEFAULT '{}'
);

-- tags define expression characteristics like type, part of speech, topic, word, idiom, etc.
CREATE TABLE IF NOT EXISTS tags (
    id            uuid PRIMARY KEY,
    tag           VARCHAR(50) UNIQUE NOT NULL CONSTRAINT forbidden_tag CHECK (tag <> 'untagged'),
    added         TIMESTAMP NOT NULL,
    updated       TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS tag_expression (
    tag_id         uuid NOT NULL,
    expression_id  uuid NOT NULL,

    PRIMARY KEY    (expression_id, tag_id),
    FOREIGN KEY    (expression_id) REFERENCES expressions (id) ON DELETE CASCADE,
    FOREIGN KEY    (tag_id) REFERENCES tags (id) ON DELETE CASCADE
);

-- the expression can consist of other expressions
-- table reflects relation like this
CREATE TABLE IF NOT EXISTS parts (
    expression_id  uuid NOT NULL,
    part_id        uuid NOT NULL,

    PRIMARY KEY    (part_id, expression_id),
    FOREIGN KEY    (part_id) REFERENCES expressions (id) ON DELETE CASCADE,
    FOREIGN KEY    (expression_id) REFERENCES expressions (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS users (
    id               uuid NOT NULL PRIMARY KEY,
    first            VARCHAR(20),
    last             VARCHAR(20),
    email            VARCHAR(50) NOT NULL UNIQUE,
    role             VARCHAR(15) NOT NULL,
    password_hash    VARCHAR(70) NOT NULL,
    properties       json NOT NULL,
    added            TIMESTAMP NOT NULL,
    updated          TIMESTAMP NOT NULL,
    last_login       TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS user_expression (
    user_id             uuid NOT NULL,
    expression_id       uuid NOT NULL,
    active              SMALLINT NOT NULL DEFAULT 1,
    last_practice_time  TIMESTAMP,
    knowledge_level     NUMERIC(8, 5) DEFAULT 0,
    practice_count      INT DEFAULT 0,
    added               TIMESTAMP NOT NULL,
    updated             TIMESTAMP NOT NULL,
    properties          json NOT NULL,

    PRIMARY KEY         (user_id, expression_id),
    FOREIGN KEY         (user_id) REFERENCES users (id) ON DELETE CASCADE,
    FOREIGN KEY         (expression_id) REFERENCES expressions (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS expression_context (
    id             uuid NOT NULL,
    expression_id  uuid NOT NULL,
    sentence        TEXT NOT NULL,
    template       json NOT NULL,
    added          TIMESTAMP NOT NULL,
    updated        TIMESTAMP NOT NULL,
    translation    json NOT NULL DEFAULT '{}',

    PRIMARY KEY    (id, expression_id),
    FOREIGN KEY    (expression_id) REFERENCES expressions (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS dialogues (
    id             uuid NOT NULL,
    user_id        uuid NOT NULL,
    title          TEXT NOT NULL,
    description    TEXT,
    settings       json NOT NULL,
    dialogues      json NOT NULL DEFAULT '[]',
    expressions    json NOT NULL DEFAULT '[]',
    added          TIMESTAMP NOT NULL,
    updated        TIMESTAMP NOT NULL,

    PRIMARY KEY    (id, user_id),
    FOREIGN KEY    (user_id) REFERENCES users (id) ON DELETE CASCADE
);

-- ============================================================================================================
-- MIGRATIONS:
-- ============================================================================================================

ALTER TABLE users ADD COLUMN IF NOT EXISTS exprs_learn_list VARCHAR(43) [];
ALTER TABLE user_expression DROP COLUMN IF EXISTS repeat_range;

---------------------------------------------------------------------------------------------------------------

DO $$
BEGIN
  IF EXISTS(SELECT *
    FROM information_schema.columns
    WHERE table_name='expressions' and column_name='translation')
  THEN
      ALTER TABLE "public"."expressions" RENAME COLUMN "translation" TO "translations";
  END IF;
END $$;

---------------------------------------------------------------------------------------------------------------

ALTER TABLE users DROP COLUMN IF EXISTS exprs_learn_list;

---------------------------------------------------------------------------------------------------------------

ALTER TABLE expressions ADD COLUMN IF NOT EXISTS properties json NOT NULL DEFAULT '{}';

---------------------------------------------------------------------------------------------------------------
