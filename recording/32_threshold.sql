SELECT title FROM articles
WHERE search_text <@> to_bm25query('jazz trumpet','articles_search_bm25') < -5
ORDER BY search_text <@> to_bm25query('jazz trumpet','articles_search_bm25') LIMIT 10;
