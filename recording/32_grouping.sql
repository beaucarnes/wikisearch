WITH candidates AS MATERIALIZED (
 SELECT id,word_count FROM articles
 ORDER BY search_text <@> to_bm25query('jazz trumpet','articles_search_bm25') LIMIT 100
)
SELECT CASE WHEN word_count > 300 THEN 'long' ELSE 'short' END AS article_size,count(*)
FROM candidates GROUP BY article_size;
