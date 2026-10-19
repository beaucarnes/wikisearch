"""Resume embeddings for a fixed longest-article subset, plus two demo titles."""
import argparse
import time
import psycopg
from pgvector.psycopg import register_vector
from settings import database_url, document_text, new_model


class Database:
    """Retry idempotent operations on a fresh connection after a connection failure."""

    def __init__(self, attempts=5):
        self.conn = None
        self.attempts = attempts

    def close(self):
        if self.conn is not None:
            self.conn.close()
            self.conn = None

    def run(self, operation, label):
        for attempt in range(1, self.attempts + 1):
            try:
                if self.conn is None or self.conn.closed:
                    self.conn = psycopg.connect(
                        database_url(), autocommit=True, connect_timeout=10,
                        application_name='wikisearch-embed',
                        keepalives=1, keepalives_idle=30,
                        keepalives_interval=10, keepalives_count=3,
                    )
                    register_vector(self.conn)
                return operation(self.conn)
            except (psycopg.OperationalError, psycopg.InterfaceError) as error:
                # Retry connection errors and server restarts, not SQL mistakes,
                # permission errors, query cancellation, or arbitrary exceptions.
                state = error.sqlstate
                retryable = state is None or state.startswith('08') or state in {
                    '57P01', '57P02', '57P03',
                }
                self.close()
                if not retryable or attempt == self.attempts:
                    raise
                delay = min(2 ** attempt, 30)
                print(f'Connection interrupted during {label}. Reconnecting in '
                      f'{delay}s (attempt {attempt + 1}/{self.attempts})...', flush=True)
                time.sleep(delay)


def save_batch(conn, updates):
    # Each batch commits independently. If a COMMIT succeeds but its response is
    # lost, retrying is safe: already-saved embeddings are never overwritten.
    with conn.transaction():
        with conn.cursor() as cur:
            cur.executemany(
                'UPDATE articles SET embedding=%s WHERE id=%s AND embedding IS NULL',
                updates,
            )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--limit', type=int, default=25000)
    parser.add_argument('--batch-size', type=int, default=32)
    args = parser.parse_args()
    if args.limit < 1 or args.batch_size < 1:
        parser.error('Both limits must be positive')
    db = Database()
    try:
        # Choose the cohort BEFORE filtering missing embeddings. Reruns do not
        # select the next 25k articles and silently expand semantic coverage.
        ids = [r[0] for r in db.run(lambda conn: conn.execute('''WITH longest AS (
            SELECT id FROM articles WHERE id > 0 ORDER BY word_count DESC,id LIMIT %s
        ), cohort AS (
            SELECT id FROM longest UNION SELECT id FROM articles
            WHERE title IN ('Bioluminescence','Volcano')
        ) SELECT a.id FROM articles a JOIN cohort c USING(id)
          WHERE a.embedding IS NULL ORDER BY a.id''', (args.limit,)).fetchall(),
          'selecting missing embeddings')]
        print(f'{len(ids):,} missing embeddings in selected cohort '
              f'(up to {args.limit + 2:,} articles).', flush=True)
        if not ids:
            print('The selected cohort is already embedded.', flush=True)
            return
        # Avoid holding an idle database connection during the model download.
        db.close()
        print('Loading the local embedding model...', flush=True)
        model = new_model()
        started = time.perf_counter()
        for start in range(0, len(ids), args.batch_size):
            batch_ids = ids[start:start+args.batch_size]
            rows = db.run(lambda conn: conn.execute(
                'SELECT id,title,body FROM articles WHERE id=ANY(%s) ORDER BY id',
                (batch_ids,)).fetchall(), 'reading an article batch')
            vectors = model.encode([document_text(r[1],r[2]) for r in rows],
                                   normalize_embeddings=True, batch_size=args.batch_size)
            updates = [(v, row[0]) for row,v in zip(rows,vectors)]
            db.run(lambda conn: save_batch(conn, updates), 'saving an embedding batch')
            done = min(start+args.batch_size,len(ids))
            print(f'{done:,}/{len(ids):,} in {time.perf_counter()-started:.1f}s', flush=True)
        print('All selected embeddings saved. Updating planner statistics...', flush=True)
        db.run(lambda conn: conn.execute('ANALYZE articles'), 'updating planner statistics')
        print('Embedding job complete.', flush=True)
    finally:
        db.close()


if __name__ == '__main__':
    main()
