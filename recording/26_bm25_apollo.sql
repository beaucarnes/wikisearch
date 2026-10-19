SELECT title, body <@> to_bm25query('Apollo 13', 'articles_body_bm25') AS score
FROM articles
ORDER BY body <@> to_bm25query('Apollo 13', 'articles_body_bm25')
LIMIT 10;
