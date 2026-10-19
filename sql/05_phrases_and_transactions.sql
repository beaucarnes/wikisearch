SET default_text_search_config = 'english';
-- pg_textsearch 1.5.1: parse the left-hand text using the same config as the index.
SELECT title FROM articles
WHERE search_text @@ to_tsquery('english','jazz & !rock')
ORDER BY search_text <@> to_bm25query('jazz trumpet','articles_search_bm25') LIMIT 10;
SELECT title FROM articles
WHERE search_text @@ phraseto_tsquery('english','new orleans')
ORDER BY search_text <@> to_bm25query('jazz trumpet','articles_search_bm25') LIMIT 10;
EXPLAIN (ANALYZE,BUFFERS)
SELECT title FROM articles
WHERE search_text @@ phraseto_tsquery('english','new orleans')
ORDER BY search_text <@> to_bm25query('jazz trumpet','articles_search_bm25') LIMIT 10;
-- Phrase checks may recheck table rows. Boolean+ranking is not one optimized scan.

BEGIN;
INSERT INTO articles(id,url,title,body,word_count)
VALUES(-1,'https://example.com','quokkatapir demo',
       'quokkatapir adds searchable text inside one PostgreSQL transaction.',8);
SELECT title FROM articles
WHERE search_text <@> to_bm25query('quokkatapir','articles_search_bm25') < 0
ORDER BY search_text <@> to_bm25query('quokkatapir','articles_search_bm25') LIMIT 3;
ROLLBACK;
SELECT title FROM articles
WHERE search_text <@> to_bm25query('quokkatapir','articles_search_bm25') < 0
ORDER BY search_text <@> to_bm25query('quokkatapir','articles_search_bm25') LIMIT 3;
