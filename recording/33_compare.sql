SELECT title, search_text <@> to_bm25query('jazz trumpet', 'articles_search_bm25') AS score
FROM articles
ORDER BY search_text <@> to_bm25query('jazz trumpet', 'articles_search_bm25')
LIMIT 10;
SELECT title, search_text <@> to_bm25query('jazz trumpet', 'articles_tuned_bm25') AS score
FROM articles
ORDER BY search_text <@> to_bm25query('jazz trumpet', 'articles_tuned_bm25')
LIMIT 10;
