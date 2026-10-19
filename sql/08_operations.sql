SELECT s.schemaname,s.relname AS tablename,s.indexrelname AS indexname,
       s.idx_scan,s.idx_tup_read,s.idx_tup_fetch
FROM pg_stat_user_indexes s JOIN pg_class i ON i.oid=s.indexrelid
JOIN pg_am am ON am.oid=i.relam WHERE am.amname='bm25';
SELECT bm25_needs_compaction('articles_search_bm25'::regclass);
SELECT bm25_level_counts('articles_search_bm25'::regclass);
-- Maintenance examples: run deliberately during a suitable window.
-- SELECT bm25_force_merge('articles_search_bm25');
-- REINDEX INDEX articles_search_bm25;
-- 1.5.1 force_merge is a bounded best-effort pass, not a guarantee of one segment.
-- Background compaction is preview and requires pg_durable. See the tagged README.
