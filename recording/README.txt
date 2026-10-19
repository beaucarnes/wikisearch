WIKISEARCH RECORDING COMMANDS
Run inside wikisearch with .venv active. Run one command at a time. Do not paste this entire file into a terminal.
Keep Terminal A for the server after reference 52:00; use Terminal B for later commands. Run only the commands printed here; numbering gaps are intentional.

@@ 00:00–00:20 | Browser: http://127.0.0.1:8000
Record this opening AFTER the app is finished. Enter the query, choose Keyword, click Search, and hold the returned titles.
BROWSER QUERY: animals that make their own light
CHECK: Show actual titles, coverage, and elapsed time. No promised first result.

@@ 11:00–11:15 | Browser: Tiger Console, selected service
Click SQL Editor at the bottom of the service page. Type this one statement and click Run. Expand the result pane if necessary.
SELECT CURRENT_DATE;
CHECK: A date row appears. If SQL Editor is hidden, see the exact console documentation linked in recording-notes.txt.

@@ 11:15–11:35 | Browser: same SQL Editor
Replace the editor contents by pasting recording/11_discover.sql, then click Run. Show available versions.
PASTE FILE: recording/11_discover.sql
SELECT version();
SELECT name, default_version, installed_version
FROM pg_available_extensions
WHERE name IN ('pg_textsearch', 'vector', 'vectorscale');
SELECT version, installed FROM pg_available_extension_versions
WHERE name = 'pg_textsearch' ORDER BY version;
CHECK: Verify 1.5.1 is available or a compatible later version is installed. Do not show credentials.

@@ 11:35–12:00 | Browser: same SQL Editor
Replace contents with sql/00_extensions.sql and click Run. Show extension versions and the successful guard check.
PASTE FILE: sql/00_extensions.sql
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
CHECK: pg_textsearch, vector, and vectorscale appear. Stop this take if the version guard fails; resolve the service update off camera.

@@ 12:00–12:25 | Terminal A: parent of the downloaded wikisearch folder
For a fresh checkout, enter these one at a time. Wait for package installation to finish before the next command. Existing .venv users only activate it.
cd wikisearch
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
CHECK: Cut download/install time. On Windows use .venv\Scripts\Activate.ps1 instead of source.

@@ 12:25–12:45 | Terminal A, then private editor window
Create .env only if absent. Pause capture, paste the Tiger Cloud URI into DATABASE_URL, preserve SSL, then generate and paste an admin token into ADMIN_TOKEN. Close .env before resuming.
cp -n .env.example .env
python -c 'import secrets; print(secrets.token_urlsafe(32))'
CHECK: Never overwrite the existing working .env or display either secret. The token command belongs in the private pause.

@@ 13:00–13:20 | Editor above terminal A
Open recording/13_connection.sql. Run the connection check and keep all three result sets visible.
python db.py recording/13_connection.sql
CHECK: The server version, extension versions, and connected = 1 print successfully.

@@ 15:00–15:20 | Editor: sql/01_schema.sql above terminal A
Highlight the five initial columns, then run the schema file.
python db.py sql/01_schema.sql
CHECK: CREATE TABLE and CREATE SEQUENCE, or already-exists notices on a rehearsal database.

@@ 16:00–16:20 | Terminal A
Run the full import. Keep this process in the foreground. Do not paste later commands underneath it.
python load.py
CHECK: Capture genuine download/import progress. On an existing complete database, explain the zero-insert rerun instead of pretending to load again.

@@ 17:00–17:20 | Editor above terminal A
Open recording/17_counts.sql. Run the source-only count. Highlight the value.
python db.py recording/17_counts.sql
CHECK: Expected 241,787 after the full pinned load, even if negative-ID demos exist.

@@ 17:20–17:40 | Editor above terminal A
Open recording/17_articles.sql. Run the largest-article and demo-title checks. Hold the title, URL, and introduction columns.
python db.py recording/17_articles.sql
CHECK: Volcano and Bioluminescence should exist. Fix a partial import before ranking comparisons.

@@ Ref 19:00 | Editor above terminal A
Open recording/19_gin_index.sql above terminal A. Point to to_tsvector, english, and USING gin as each is explained. Type the command, press Enter, and wait for completion.
python db.py recording/19_gin_index.sql
CHECK: Wait for CREATE INDEX and the shell prompt. Cut build time; do not execute the whole baseline file.

@@ Ref 19:20 | Editor above terminal A
Open recording/19_native_query.sql. First explain plainto_tsquery, WHERE, ts_rank, ORDER BY, and LIMIT in that order. Then run the command. Hold the returned titles and rank values.
python db.py recording/19_native_query.sql
CHECK: The file returns titles and ranks only. If it returns no rows, say that this all-terms query found no matches and continue to the small example. Do not promise a particular title.

@@ Ref 20:00 | Editor above terminal A
Run recording/20_matching.sql. Read the three labeled outputs in order: all_terms with & signs, and_match = false, and any_term with | signs.
python db.py recording/20_matching.sql
CHECK: and_match should be false. The example is missing cloud and aviation, among the required processed terms. No need to teach each stemmed spelling.

@@ Ref 20:25 | Editor above terminal A
Open recording/20_or_query.sql. Highlight the OR operators before running. Compare its titles with the original all-terms query.
python db.py recording/20_or_query.sql
CHECK: Compare actual titles. OR admits at least as broad a set of matches, but LIMIT 10 means both displayed lists can still have ten rows.

@@ Ref 21:00 | Editor above terminal A
Open recording/21_native_plan.sql. Run EXPLAIN ANALYZE with BUFFERS. Expand the terminal so the plan is readable.
python db.py recording/21_native_plan.sql
CHECK: Point to actual scan, sort, and limit nodes; do not name a node absent from this plan.

@@ Ref 21:40 | Terminal A
Run the repeat-plan command. Find Execution Time near the bottom. Leave native-plan.txt saved for the comparison at reference 25:20.
python db.py recording/21_native_plan.sql | tee recording/native-plan.txt
CHECK: Label this a repeat run with possible warm-cache effects.

@@ Ref 22:00 | Editor above terminal A
Run the jazz file. In a local scratch note, write: native jazz — followed by one or two returned titles and your brief judgment, or no rows. Keep this note for reference 26:00.
python db.py recording/22_native_jazz.sql

@@ Ref 22:20 | Editor above terminal A
Run the Apollo file. Record its first few titles in the same scratch note under native Apollo 13. Keep the exact query text unchanged.
python db.py recording/22_native_apollo.sql

@@ Ref 23:00 | Editor above terminal A
Open recording/23_bm25_index.sql. Highlight USING bm25(body), text_config, then the two session maintenance settings. Run only this build.
python db.py recording/23_bm25_index.sql
CHECK: Wait for CREATE INDEX and a shell prompt. The settings are examples for a service that can support them.

@@ Ref 24:00 | Editor above terminal A
Open recording/24_bm25_query.sql. Highlight <@> and both to_bm25query calls. Run the query.
python db.py recording/24_bm25_query.sql
CHECK: Keep returned titles and negative scores visible.

@@ Ref 25:00 | Editor above terminal A
Open recording/25_bm25_plan.sql. Run the unforced plan and locate the BM25 index access path, if selected.
python db.py recording/25_bm25_plan.sql
CHECK: Save real timings; do not copy the earlier sample timing into this take.

@@ Ref 29:00 | Editor above terminal A
Open recording/29_search_column.sql. Point briefly to title and body while explaining the benefit. Run the command after the explanation. Cut out the wait.
python db.py recording/29_search_column.sql
CHECK: Wait for ALTER TABLE. This rewrite can take time on the full corpus.

@@ Ref 29:25 | Editor above terminal A
Open recording/29_search_index.sql. Point to search_text. Say the first paragraph, run the command, wait for CREATE INDEX, then say the transition.
python db.py recording/29_search_index.sql
CHECK: Wait for CREATE INDEX before any query naming articles_search_bm25.

@@ Ref 35:00 | Editor above terminal A
Open recording/35_boolean.sql. Point to SET default_text_search_config, jazz & !rock, and the separate BM25 ordering expression. Then run the file.
python db.py recording/35_boolean.sql
CHECK: Keep returned titles visible; English configuration is set in this connection.

@@ Ref 35:20 | Editor above terminal A
Open recording/35_phrase.sql. Highlight phraseto_tsquery and new orleans, then run.
python db.py recording/35_phrase.sql
CHECK: This is tokenized phrase matching, not a byte-for-byte substring test.

@@ Ref 39:40 | Editor: settings.py, then sql/06_vectors.sql
Open sql/06_vectors.sql and point to vector(384). Explain the storage purpose, then run the command. Keep the fixed model settings available only if needed.
python db.py sql/06_vectors.sql
CHECK: ALTER TABLE succeeds. Do not change the model for an existing embedding set.

@@ Ref 40:20 | Terminal A
Run the embedding job. Show the missing count, model-loading line, and one genuine committed progress line.
python embed.py --limit 25000
CHECK: Keep this terminal busy until completion. If the cohort is already embedded, show that message honestly.

@@ Ref 41:00 | Editor above terminal A
Open recording/41_vector_counts.sql. Run the fixed-cohort count only after the embedding job exits. Highlight saved and missing counts.
python db.py recording/41_vector_counts.sql
CHECK: missing_embeddings must be 0 before proceeding. The selected count is at most 25,002 on the full source snapshot.

@@ Ref 41:20 | Editor above terminal A
Open recording/41_vector_index.sql. Point to the vector index definition. Explain why it is needed, then run the file and wait for CREATE INDEX and ANALYZE.
python db.py recording/41_vector_index.sql
CHECK: Wait for CREATE INDEX and ANALYZE. Cut build time.

@@ Ref 43:00 | Terminal A
Run the natural-language query and hold its titles.
python query.py 'animals that make their own light' --mode semantic

@@ Ref 43:20 | Terminal A
Run the exact-name query without changing the model.
python query.py 'Apollo 13' --mode semantic

@@ Ref 47:20 | Terminal A
Run the hybrid plan command. Find the named keyword_candidates and vector_candidates stages and actual rows. Then find grouping and final limit. It is fine to pause the recording to locate them first.
python query.py 'Apollo 13' --mode hybrid --explain
CHECK: Expect at most 20 candidates per retriever with the default settings. Follow actual plan details.

@@ Ref 47:40 | Terminal A
Run the three commands separately. After each finishes, copy the first few titles into the scratch note under its mode. Use that note at reference 49:00. Allow a separate take for each command.
python query.py 'Apollo 13' --mode keyword
python query.py 'Apollo 13' --mode semantic
python query.py 'Apollo 13' --mode hybrid
CHECK: Capture extra comparison footage if needed; the minute marker is an edit target, not a command deadline.

@@ Ref 52:00 | Terminal A, then browser
Start Uvicorn and leave it running in terminal A. Wait for startup, then open http://127.0.0.1:8000 in the browser. Cut out the startup wait.
uvicorn app:app --host 127.0.0.1 --port 8000
CHECK: Open http://127.0.0.1:8000. An already-running rehearsal server can remain; do not launch a second copy on port 8000.

@@ Ref 52:20 | Browser: WikiSearch, Developer Tools Network tab
Enter the query in the browser. Select Keyword and Search, then Semantic and Search, then Hybrid and Search. Let each finish and hold its titles. Then open Developer Tools > Network, submit one more search, and inspect the /search response. Capture these as separate takes if needed.
BROWSER QUERY: animals that make their own light
CHECK: Show the coverage counts, result titles, attribution footer, and actual request timing.

@@ Ref 52:40 | Terminal B: activated .venv
In activated terminal B, paste and run the entire multiline curl command as one command. Keep Uvicorn running in A. Point to returned titles and mode in the formatted JSON.
curl -sS -G http://127.0.0.1:8000/search \
  --data-urlencode 'q=Apollo 13' \
  --data-urlencode 'mode=hybrid' \
  --data-urlencode 'semantic_weight=0.7' | python -m json.tool
CHECK: Keep Uvicorn running in A. Point to mode and actual returned titles in B.

@@ Ref 53:40 | Terminal B, then browser WikiSearch
Run the helper once in terminal B. Wait for its 201 response. Then search quokkatapir in the browser and try all three modes. Describe actual results; do not promise a particular rank.
python demo_insert.py
BROWSER QUERY: quokkatapir
CHECK: The response has a negative ID. Repeated runs intentionally add more demo rows; do not run it repeatedly while filming the same insertion.

@@ Ref 54:00 | Terminal B
Install test dependencies if needed, then run the unit suite. Wait for each command before proceeding.
python -m pip install -r requirements-dev.txt
python -m unittest discover -s tests -v
CHECK: Show the actual test summary. Edit installation time out.

@@ Ref 54:20 | Terminal B
Run the real-database smoke test only after the schema and indexes are complete.
python smoke.py
CHECK: Show its real success or fix a failure before recording a success claim. The fixture rolls back.

@@ Ref 54:40 | Terminal B
Run the three curl commands one at a time. Point to the HTTP status line after each. The third request deliberately omits the admin token.
curl -sS -i 'http://127.0.0.1:8000/search?q=&mode=keyword'
curl -sS -i 'http://127.0.0.1:8000/search?q=jazz&mode=invalid'
curl -sS -i -X POST http://127.0.0.1:8000/articles \
  -H 'Content-Type: application/json' \
  -d '{"title":"Auth check","body":"Do not insert without a token","url":"https://example.com"}'
CHECK: Expect 422 for the first two. Expect 401 for missing auth when writes are configured, or 503 when disabled. Investigate an unexpected success before continuing.

@@ Ref 55:25 | Editor: sql/08_operations.sql above terminal B
Show the monitoring queries and leave maintenance commands commented. Run the read-only operations file.
python db.py sql/08_operations.sql
CHECK: The script reports index use and compaction state. It does not run force merge or REINDEX.

