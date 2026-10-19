SELECT cfgname FROM pg_ts_config ORDER BY cfgname;
SELECT to_tsvector('english', 'Databases and pooling') AS english,
       to_tsvector('simple', 'Databases and pooling') AS simple;
SELECT title, left(body, 200) AS introduction FROM articles
WHERE title = 'Volcano' ORDER BY id LIMIT 1;
