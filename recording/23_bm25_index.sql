SET max_parallel_maintenance_workers = 4;
SET maintenance_work_mem = '256MB';
CREATE INDEX IF NOT EXISTS articles_body_bm25 ON articles
USING bm25(body) WITH (text_config='english');
