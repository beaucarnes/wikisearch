SELECT title,embedding <=> (SELECT embedding FROM articles WHERE title='Volcano' ORDER BY id LIMIT 1) AS distance
FROM articles WHERE embedding IS NOT NULL AND title <> 'Volcano'
ORDER BY embedding <=> (SELECT embedding FROM articles WHERE title='Volcano' ORDER BY id LIMIT 1)
LIMIT 10;
