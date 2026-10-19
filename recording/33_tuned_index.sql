CREATE INDEX IF NOT EXISTS articles_tuned_bm25 ON articles
USING bm25(search_text) WITH(text_config='english',k1=1.5,b=0.8);
