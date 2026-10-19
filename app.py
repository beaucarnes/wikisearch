import os
import secrets
import time
from contextlib import asynccontextmanager
from threading import Lock
from typing import Literal
import psycopg
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool
from pgvector.psycopg import register_vector
from fastapi import FastAPI, Header, HTTPException, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field, HttpUrl
from settings import ROOT, database_url, document_text, new_model
from safety import snippet_parts, safe_url

QUERIES = {mode: (ROOT/'sql'/f'search_{mode}.sql').read_text() for mode in ('keyword','semantic','hybrid')}
model_lock = Lock()


def configure(conn):
    register_vector(conn)
    conn.execute("SET default_text_search_config = 'english'")
    conn.execute("SET statement_timeout = '20s'")


@asynccontextmanager
async def lifespan(app):
    pool = ConnectionPool(database_url(), min_size=1, max_size=4, open=False,
                          configure=configure, kwargs={'autocommit':True,'row_factory':dict_row})
    pool.open(wait=True)
    app.state.pool = pool
    # Load on first semantic request so keyword search doesn't wait for a model download.
    app.state.model = None
    try:
        yield
    finally:
        pool.close()


app = FastAPI(title='WikiSearch', lifespan=lifespan)


def encode(text):
    with model_lock:
        if app.state.model is None:
            app.state.model = new_model()
        return app.state.model.encode(text, normalize_embeddings=True)


@app.get('/')
def home():
    return FileResponse(ROOT/'index.html')


@app.get('/health')
def health():
    with app.state.pool.connection() as conn:
        return conn.execute('''SELECT count(*) AS articles,
          count(embedding) AS embedded_articles,
          (SELECT extversion FROM pg_extension WHERE extname='pg_textsearch') AS pg_textsearch
          FROM articles''').fetchone()


@app.get('/search')
def search(q: str = Query(min_length=1,max_length=300),
           mode: Literal['keyword','semantic','hybrid'] = 'hybrid',
           limit: int = Query(default=10,ge=1,le=50),
           semantic_weight: float = Query(default=0.5,ge=0,le=1)):
    q = q.strip()
    if not q:
        raise HTTPException(422, 'Type a search query.')
    started = time.perf_counter()
    # Endpoints 0 and 1 are genuine single-retriever modes.
    effective = mode
    if mode == 'hybrid' and semantic_weight in (0,1):
        effective = 'keyword' if semantic_weight == 0 else 'semantic'
    params = {'q':q, 'limit':limit, 'candidates':max(20,limit*2),
              'kw_weight':1-semantic_weight, 'vec_weight':semantic_weight}
    if effective != 'keyword':
        params['embedding'] = encode(q)
    with app.state.pool.connection() as conn:
        rows = conn.execute(QUERIES[effective], params).fetchall()
    for row in rows:
        row['snippet_parts'] = snippet_parts(row.pop('snippet'))
        row['url'] = safe_url(row['url'])
    return {'query':q, 'mode':effective, 'elapsed_ms':round((time.perf_counter()-started)*1000,1),
            'results':rows}


class Article(BaseModel):
    title: str = Field(min_length=1,max_length=300)
    body: str = Field(min_length=1,max_length=100000)
    url: HttpUrl


@app.post('/articles', status_code=201)
def add_article(article: Article, x_admin_token: str | None = Header(default=None)):
    expected = os.getenv('ADMIN_TOKEN','')
    if not expected or expected.startswith('replace-this'):
        raise HTTPException(503, 'Configure ADMIN_TOKEN to enable demo writes.')
    if not x_admin_token or not secrets.compare_digest(x_admin_token,expected):
        raise HTTPException(401, 'Invalid admin token.')
    if not article.title.strip() or not article.body.strip() or '\x00' in article.title+article.body:
        raise HTTPException(422, 'Title and body must contain valid nonempty text.')
    vector = encode(document_text(article.title,article.body))
    with app.state.pool.connection() as conn:
        with conn.transaction():
            row = conn.execute('''INSERT INTO articles(id,url,title,body,word_count,embedding)
                VALUES (nextval('demo_article_id'),%s,%s,%s,%s,%s) RETURNING id,title''',
                (str(article.url), article.title, article.body,len(article.body.split()),vector)).fetchone()
    return row
