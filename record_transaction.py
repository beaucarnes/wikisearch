"""Interactive, rollback-only transaction demo. Run from the project directory."""
import psycopg
from settings import database_url

TERM = 'quokkatapirtxrehearsal'
SEARCH = """SELECT id, title FROM articles
WHERE search_text <@> to_bm25query(%s, 'articles_search_bm25') < 0
ORDER BY search_text <@> to_bm25query(%s, 'articles_search_bm25') LIMIT 10"""

def main():
    with psycopg.connect(database_url(), autocommit=True) as conn:
        conn.execute("SET default_text_search_config = 'english'")
        demo_id = conn.execute("SELECT nextval('demo_article_id')").fetchone()[0]
        input('Ready. Press Enter to BEGIN and INSERT the temporary article... ')
        conn.execute('BEGIN')
        try:
            conn.execute("""INSERT INTO articles(id, url, title, body, word_count)
                VALUES (%s, 'https://example.com', %s, %s, 4)""",
                (demo_id, TERM + ' transaction demo', TERM + ' demonstrates transactional search.'))
            print('Before rollback:', conn.execute(SEARCH, (TERM, TERM)).fetchall(), flush=True)
            input('Leave this result visible. Press Enter to ROLLBACK... ')
        finally:
            conn.execute('ROLLBACK')
        rows = conn.execute(SEARCH, (TERM, TERM)).fetchall()
        print('After rollback:', rows, flush=True)
        assert all(row[0] != demo_id for row in rows)
        assert conn.execute('SELECT count(*) FROM articles WHERE id=%s', (demo_id,)).fetchone()[0] == 0
        print('The temporary article is gone. No article was committed.', flush=True)

if __name__ == '__main__':
    main()
