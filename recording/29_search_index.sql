CREATE INDEX IF NOT EXISTS articles_search_bm25 ON articles
USING bm25(search_text) WITH (text_config='english');
