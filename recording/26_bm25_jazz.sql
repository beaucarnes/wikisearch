SELECT title, body <@> to_bm25query('jazz trumpet new orleans', 'articles_body_bm25') AS score
FROM articles
ORDER BY body <@> to_bm25query('jazz trumpet new orleans', 'articles_body_bm25')
LIMIT 10;
