"""Load the fixed 2023 Simple English Wikipedia snapshot without overwriting rows."""
import argparse
import hashlib
import time
from pathlib import Path
import psycopg
import pyarrow.parquet as pq
from huggingface_hub import hf_hub_download
from settings import database_url

REVISION = '3e1f92c331f318af862b87e2319ed5dc26d80f5d'
FILENAME = '20231101.simple/train-00000-of-00001.parquet'
SHA256 = '31bded16768a47c286becd292079122f5d7d4397a17b87d4250a00ccd581e6f0'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--limit', type=int, default=None, help='Small rehearsal load')
    parser.add_argument('--parquet', type=Path, help='Use an already downloaded file')
    args = parser.parse_args()
    if args.limit is not None and args.limit < 1:
        parser.error('--limit must be positive')
    path = args.parquet or Path(hf_hub_download(
        repo_id='wikimedia/wikipedia', repo_type='dataset', revision=REVISION,
        filename=FILENAME))
    if not args.parquet:
        with path.open('rb') as file:
            digest = hashlib.file_digest(file, 'sha256').hexdigest()
        if digest != SHA256:
            raise RuntimeError('Dataset checksum mismatch')
    started = time.perf_counter()
    copied = 0
    with psycopg.connect(database_url()) as conn:
        conn.execute('CREATE TEMP TABLE incoming (id bigint, url text, title text, body text, word_count int) ON COMMIT DROP')
        with conn.cursor().copy('COPY incoming (id,url,title,body,word_count) FROM STDIN') as copy:
            for batch in pq.ParquetFile(path).iter_batches(batch_size=2000, columns=['id','url','title','text']):
                for row in batch.to_pylist():
                    body = row['text'].replace('\x00', '')
                    copy.write_row((int(row['id']), row['url'], row['title'].replace('\x00',''), body, len(body.split())))
                    copied += 1
                    if args.limit and copied >= args.limit:
                        break
                if args.limit and copied >= args.limit:
                    break
        inserted = conn.execute('''INSERT INTO articles(id,url,title,body,word_count)
            SELECT id,url,title,body,word_count FROM incoming
            ON CONFLICT(id) DO NOTHING''').rowcount
    with psycopg.connect(database_url(), autocommit=True) as conn:
        conn.execute('ANALYZE articles')
        total = conn.execute('SELECT count(*) FROM articles').fetchone()[0]
    print(f'Read {copied:,}; inserted {inserted:,}; total {total:,}; {time.perf_counter()-started:.1f}s')


if __name__ == '__main__':
    main()