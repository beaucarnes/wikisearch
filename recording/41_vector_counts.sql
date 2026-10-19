WITH longest AS (
  SELECT id FROM articles WHERE id > 0 ORDER BY word_count DESC, id LIMIT 25000
), cohort AS (
  SELECT id FROM longest UNION
  SELECT id FROM articles WHERE title IN ('Bioluminescence', 'Volcano')
)
SELECT count(*) AS selected_articles, count(a.embedding) AS saved_embeddings,
       count(*) FILTER (WHERE a.embedding IS NULL) AS missing_embeddings
FROM articles a JOIN cohort c USING (id);
