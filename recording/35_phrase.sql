SET default_text_search_config = 'english';
SELECT title FROM articles
WHERE search_text @@ phraseto_tsquery('english','new orleans')
ORDER BY search_text <@> to_bm25query('jazz trumpet','articles_search_bm25') LIMIT 10;
