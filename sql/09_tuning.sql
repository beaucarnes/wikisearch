-- Optional experiment. This adds storage/write overhead while it exists.
CREATE INDEX IF NOT EXISTS articles_tuned_bm25 ON articles
USING bm25(search_text) WITH(text_config='english',k1=1.5,b=0.8);
SELECT title FROM articles
ORDER BY search_text <@> to_bm25query('jazz trumpet','articles_tuned_bm25') LIMIT 10;
-- After comparing, remove ONLY the experimental index if no longer needed:
-- DROP INDEX articles_tuned_bm25;
