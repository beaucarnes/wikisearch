WITH top_results AS MATERIALIZED (
 SELECT id,embedding <=> %(embedding)s AS score FROM articles
 WHERE embedding IS NOT NULL
 ORDER BY embedding <=> %(embedding)s LIMIT %(limit)s
)
SELECT a.id,a.title,a.url,a.word_count,t.score,
 ts_headline('english',a.body,plainto_tsquery('english',%(q)s),
 'StartSel=WIKISEARCHSTARTTOKEN,StopSel=WIKISEARCHSTOPTOKEN,MaxWords=45,MinWords=18,MaxFragments=2') AS snippet
FROM top_results t JOIN articles a USING(id) ORDER BY t.score,a.id;
