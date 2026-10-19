-- Read-only. Run in a SECOND terminal while an index build is running.
SELECT a.pid, a.state, clock_timestamp() - a.query_start AS elapsed,
       a.wait_event_type, a.wait_event, pg_blocking_pids(a.pid) AS blocked_by,
       p.phase, p.blocks_done, p.blocks_total, left(a.query, 200) AS query
FROM pg_stat_activity a
LEFT JOIN pg_stat_progress_create_index p ON p.pid = a.pid
WHERE a.datname = current_database() AND a.pid <> pg_backend_pid()
  AND a.backend_type = 'client backend' AND a.state <> 'idle'
ORDER BY a.query_start;
