CREATE INDEX IF NOT EXISTS articles_body_gin ON articles
USING gin(to_tsvector('english',body));
SELECT title,ts_rank(to_tsvector('english',body),q) AS rank
FROM articles CROSS JOIN plainto_tsquery('english','volcano eruption ash cloud aviation') q
WHERE to_tsvector('english',body) @@ q
ORDER BY rank DESC LIMIT 10;
EXPLAIN (ANALYZE,BUFFERS)
SELECT id,ts_rank(to_tsvector('english',body),q) AS rank
FROM articles CROSS JOIN plainto_tsquery('english','volcano eruption ash cloud aviation') q
WHERE to_tsvector('english',body) @@ q
ORDER BY rank DESC LIMIT 10;
-- Core PostgreSQL also supports OR and phrases; AND is a plainto_tsquery choice.
SELECT to_tsquery('english','volcano | eruption | ash | cloud | aviation');
-- Controlled example: adding one absent term excludes an otherwise useful text.
SELECT to_tsvector('english','Volcanic ash from an eruption disrupts flights')
  @@ plainto_tsquery('english','volcano eruption ash cloud aviation') AS and_match;
