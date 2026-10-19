EXPLAIN (ANALYZE, BUFFERS)
SELECT title, word_count FROM articles WHERE word_count > 300
ORDER BY search_text <@> to_bm25query('jazz trumpet new orleans', 'articles_search_bm25')
LIMIT 10;
