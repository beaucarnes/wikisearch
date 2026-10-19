CREATE INDEX IF NOT EXISTS articles_long_bm25 ON articles
USING bm25(search_text) WITH (text_config='english') WHERE word_count > 300;
