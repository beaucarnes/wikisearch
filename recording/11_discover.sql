SELECT version();
SELECT name, default_version, installed_version
FROM pg_available_extensions
WHERE name IN ('pg_textsearch', 'vector', 'vectorscale');
SELECT version, installed FROM pg_available_extension_versions
WHERE name = 'pg_textsearch' ORDER BY version;
