"""Run the same SQL as the API from the command line."""
import argparse
import psycopg
from psycopg.rows import dict_row
from pgvector.psycopg import register_vector
from settings import ROOT,database_url,new_model

def main():
    p=argparse.ArgumentParser()
    p.add_argument('query')
    p.add_argument('--mode',choices=['keyword','semantic','hybrid'],default='hybrid')
    p.add_argument('--explain',action='store_true')
    args=p.parse_args()
    params={'q':args.query,'limit':10,'candidates':20,'kw_weight':0.5,'vec_weight':0.5}
    if args.mode != 'keyword':
        params['embedding']=new_model().encode(args.query,normalize_embeddings=True)
    sql=(ROOT/'sql'/f'search_{args.mode}.sql').read_text()
    with psycopg.connect(database_url(),autocommit=True,row_factory=dict_row) as conn:
        register_vector(conn)
        conn.execute("SET default_text_search_config='english'")
        if args.explain: sql='EXPLAIN (ANALYZE,BUFFERS) '+sql
        for row in conn.execute(sql,params):
            print(row if args.explain else f"{row['score']:.6f}  {row['title']}")

if __name__ == '__main__': main()
