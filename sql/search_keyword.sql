WITH candidates AS MATERIALIZED (
 SELECT id,search_text <@> to_bm25query(%(q)s,'articles_search_bm25') AS score
 FROM articles
 ORDER BY search_text <@> to_bm25query(%(q)s,'articles_search_bm25')
 LIMIT %(limit)s
), top_results AS MATERIALIZED (
 SELECT * FROM candidates WHERE score < 0 ORDER BY score,id LIMIT %(limit)s
)
SELECT a.id,a.title,a.url,a.word_count,t.score,
 ts_headline('english',a.body,plainto_tsquery('english',%(q)s),
 'StartSel=WIKISEARCHSTARTTOKEN,StopSel=WIKISEARCHSTOPTOKEN,MaxWords=45,MinWords=18,MaxFragments=2') AS snippet
FROM top_results t JOIN articles a USING(id) ORDER BY t.score,a.id;
