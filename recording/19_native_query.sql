SELECT title, ts_rank(to_tsvector('english', body), q) AS rank
FROM articles
CROSS JOIN plainto_tsquery('english', 'volcano eruption ash cloud aviation') q
WHERE to_tsvector('english', body) @@ q
ORDER BY rank DESC LIMIT 10;
