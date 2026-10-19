-- Candidate retrieval happens BEFORE row_number, preserving direct ORDER BY/LIMIT paths.
WITH keyword_candidates AS MATERIALIZED (
 SELECT id,search_text <@> to_bm25query(%(q)s,'articles_search_bm25') AS score
 FROM articles
 ORDER BY search_text <@> to_bm25query(%(q)s,'articles_search_bm25')
 LIMIT %(candidates)s
), vector_candidates AS MATERIALIZED (
 SELECT id,embedding <=> %(embedding)s AS distance FROM articles
 WHERE embedding IS NOT NULL
 ORDER BY embedding <=> %(embedding)s LIMIT %(candidates)s
), keyword_ranks AS (
 SELECT id,row_number() OVER(ORDER BY score,id) AS rank
 FROM keyword_candidates WHERE score < 0
), vector_ranks AS (
 SELECT id,row_number() OVER(ORDER BY distance,id) AS rank FROM vector_candidates
), contributions AS (
 SELECT id,%(kw_weight)s::double precision/(60+rank) AS contribution FROM keyword_ranks
 UNION ALL
 SELECT id,%(vec_weight)s::double precision/(60+rank) AS contribution FROM vector_ranks
), top_results AS MATERIALIZED (
 SELECT id,sum(contribution) AS score FROM contributions
 GROUP BY id ORDER BY score DESC,id LIMIT %(limit)s
)
SELECT a.id,a.title,a.url,a.word_count,t.score,
 ts_headline('english',a.body,plainto_tsquery('english',%(q)s),
 'StartSel=WIKISEARCHSTARTTOKEN,StopSel=WIKISEARCHSTOPTOKEN,MaxWords=45,MinWords=18,MaxFragments=2') AS snippet
FROM top_results t JOIN articles a USING(id) ORDER BY t.score DESC,a.id;
