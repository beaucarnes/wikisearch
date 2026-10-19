ALTER TABLE articles ADD COLUMN IF NOT EXISTS search_text text
GENERATED ALWAYS AS (title || ' ' || body) STORED;
