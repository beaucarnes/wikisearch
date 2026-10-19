"""Database integration checks. Inserts roll back; requires the completed schema/indexes."""
import numpy as np
import psycopg
from psycopg.rows import dict_row
from pgvector.psycopg import register_vector
from settings import ROOT,database_url

def main():
    with psycopg.connect(database_url(),autocommit=True,row_factory=dict_row) as conn:
        register_vector(conn)
        conn.execute("SET default_text_search_config='english'")
        vector=np.zeros(384,dtype=np.float32);vector[0]=1
        with conn.transaction(force_rollback=True):
            conn.execute('''INSERT INTO articles(id,url,title,body,word_count,embedding)
             VALUES(-99,'https://example.com','quokkatapir smoke',
             'quokkatapir volcanic ash new orleans',5,%s)''',(vector,))
            params={'q':'quokkatapir','limit':10,'candidates':20,
                    'kw_weight':0.5,'vec_weight':0.5,'embedding':vector}
            for mode in ('keyword','semantic','hybrid'):
                sql=(ROOT/'sql'/f'search_{mode}.sql').read_text()
                rows=conn.execute(sql,params,prepare=True).fetchall()
                assert any(r['id']==-99 for r in rows), f'{mode}: fixture missing'
            found=conn.execute("SELECT id FROM articles WHERE search_text @@ phraseto_tsquery('english','new orleans') AND id=-99").fetchone()
            assert found is not None
        assert conn.execute('SELECT id FROM articles WHERE id=-99').fetchone() is None
    print('PASS: prepared keyword, semantic, hybrid, phrase filter, read-your-writes and rollback')

if __name__ == '__main__': main()
