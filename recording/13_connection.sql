SELECT current_database(), current_user, version();
SELECT extname, extversion FROM pg_extension
WHERE extname IN ('pg_textsearch', 'vector', 'vectorscale');
SELECT 1 AS connected;
