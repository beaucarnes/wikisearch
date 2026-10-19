-- Run AFTER embed.py.
CREATE INDEX IF NOT EXISTS articles_embedding_idx ON articles
USING diskann(embedding vector_cosine_ops);
ANALYZE articles;
-- The scalar subquery becomes an initplan; exclude the source article itself.
SELECT title,embedding <=> (SELECT embedding FROM articles WHERE title='Volcano' ORDER BY id LIMIT 1) AS distance
FROM articles WHERE embedding IS NOT NULL AND title <> 'Volcano'
ORDER BY embedding <=> (SELECT embedding FROM articles WHERE title='Volcano' ORDER BY id LIMIT 1)
LIMIT 10;
