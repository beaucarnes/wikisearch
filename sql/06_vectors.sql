ALTER TABLE articles ADD COLUMN IF NOT EXISTS embedding vector(384);
-- Now run: python embed.py --limit 25000
