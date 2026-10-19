CREATE TABLE IF NOT EXISTS articles (
  id bigint PRIMARY KEY,
  url text NOT NULL,
  title text NOT NULL,
  body text NOT NULL,
  word_count integer NOT NULL CHECK(word_count >= 0)
);
-- Positive IDs belong to Wikipedia. Demo inserts get distinct negative IDs.
CREATE SEQUENCE IF NOT EXISTS demo_article_id AS bigint
INCREMENT BY -1 MINVALUE -9223372036854775807 MAXVALUE -1000 START WITH -1000;
