SELECT id, title, word_count, url FROM articles
WHERE id > 0 ORDER BY word_count DESC, id LIMIT 10;
SELECT id, title, word_count, left(body, 200) AS introduction
FROM articles WHERE title IN ('Bioluminescence', 'Volcano') ORDER BY title;
