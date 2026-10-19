SET default_text_search_config = 'english';
SELECT title FROM articles
WHERE search_text @@ to_tsquery('english','jazz & !rock')
ORDER BY search_text <@> to_bm25query('jazz trumpet','articles_search_bm25') LIMIT 10;
