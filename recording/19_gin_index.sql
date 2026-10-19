CREATE INDEX IF NOT EXISTS articles_body_gin ON articles
USING gin(to_tsvector('english',body));
