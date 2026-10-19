CREATE INDEX IF NOT EXISTS articles_embedding_idx ON articles
USING diskann(embedding vector_cosine_ops);
ANALYZE articles;
