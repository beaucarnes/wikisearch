CREATE EXTENSION IF NOT EXISTS pg_textsearch;
CREATE EXTENSION IF NOT EXISTS vectorscale CASCADE;
SELECT extname,extversion FROM pg_extension
WHERE extname IN ('pg_textsearch','vector','vectorscale');
DO $$
DECLARE v text;
BEGIN
  SELECT extversion INTO v FROM pg_extension WHERE extname='pg_textsearch';
  IF string_to_array(v,'.')::int[] < ARRAY[1,5,1] THEN
    RAISE EXCEPTION 'Course requires pg_textsearch >=1.5.1; installed %. Update the service and extension first.',v;
  END IF;
END $$;
SET default_text_search_config = 'english';
