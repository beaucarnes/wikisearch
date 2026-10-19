EXPLAIN (ANALYZE, BUFFERS)
SELECT title, body <@> to_bm25query('volcano eruption ash cloud aviation', 'articles_body_bm25') AS score
FROM articles
ORDER BY body <@> to_bm25query('volcano eruption ash cloud aviation', 'articles_body_bm25')
LIMIT 10;
