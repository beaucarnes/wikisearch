ALTER TABLE articles ADD COLUMN IF NOT EXISTS search_text text
GENERATED ALWAYS AS (title || ' ' || body) STORED;
CREATE INDEX IF NOT EXISTS articles_search_bm25 ON articles
USING bm25(search_text) WITH (text_config='english');
CREATE INDEX IF NOT EXISTS articles_word_count_idx ON articles(word_count);
CREATE INDEX IF NOT EXISTS articles_long_bm25 ON articles
USING bm25(search_text) WITH (text_config='english') WHERE word_count > 300;
SELECT title,word_count FROM articles WHERE word_count > 300
ORDER BY search_text <@> to_bm25query('jazz trumpet new orleans','articles_long_bm25') LIMIT 10;
-- A score threshold is corpus/query-specific, not a probability of relevance.
SELECT title FROM articles
WHERE search_text <@> to_bm25query('jazz trumpet','articles_search_bm25') < -5
ORDER BY search_text <@> to_bm25query('jazz trumpet','articles_search_bm25') LIMIT 10;
-- Counts here describe only the best 100 candidates, not all matches.
WITH candidates AS MATERIALIZED (
 SELECT id,word_count FROM articles
 ORDER BY search_text <@> to_bm25query('jazz trumpet','articles_search_bm25') LIMIT 100
)
SELECT CASE WHEN word_count > 300 THEN 'long' ELSE 'short' END AS article_size,count(*)
FROM candidates GROUP BY article_size;
-- Optional expression index demonstration (avoid maintaining redundant indexes):
-- CREATE INDEX articles_expression_bm25 ON articles
-- USING bm25 ((coalesce(title,'') || ' ' || coalesce(body,''))) WITH (text_config='english');
-- SELECT title FROM articles ORDER BY (coalesce(title,'') || ' ' || coalesce(body,''))
-- <@> to_bm25query('jazz trumpet','articles_expression_bm25') LIMIT 10;
