"""Run a trusted course SQL file and print every result set (reads .env)."""
import argparse
from pathlib import Path
import psycopg
from settings import database_url

if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('file',type=Path)
    args=parser.parse_args()
    with psycopg.connect(database_url(),autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute(args.file.read_text(),prepare=False)
            while True:
                if cur.description:
                    print(' | '.join(col.name for col in cur.description))
                    for row in cur: print(row)
                elif cur.statusmessage:
                    print(cur.statusmessage)
                if not cur.nextset(): break
