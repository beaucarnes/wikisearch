SET max_parallel_maintenance_workers = 4;
SET maintenance_work_mem = '256MB';
CREATE INDEX IF NOT EXISTS articles_body_bm25 ON articles
USING bm25(body) WITH (text_config='english');
SELECT title,body <@> to_bm25query('volcano eruption ash cloud aviation','articles_body_bm25') AS score
FROM articles
ORDER BY body <@> to_bm25query('volcano eruption ash cloud aviation','articles_body_bm25') LIMIT 10;
EXPLAIN (ANALYZE,BUFFERS)
SELECT title FROM articles
ORDER BY body <@> to_bm25query('volcano eruption ash cloud aviation','articles_body_bm25') LIMIT 10;
SELECT cfgname FROM pg_ts_config ORDER BY cfgname;
