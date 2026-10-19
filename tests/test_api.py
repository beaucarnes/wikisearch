import copy
import unittest
from contextlib import contextmanager
from unittest.mock import patch
from fastapi.testclient import TestClient
import app as api

class FakeConnection:
    def __init__(self): self.calls=[]
    def execute(self,sql,params):
        self.calls.append((sql,params))
        return self
    def fetchall(self):
        return [{'id':1,'title':'Article','url':'javascript:alert(1)','word_count':10,
                 'score':-2.0,'snippet':'<img src=x> WIKISEARCHSTARTTOKENashWIKISEARCHSTOPTOKEN'}]

class FakePool:
    def __init__(self): self.conn=FakeConnection()
    @contextmanager
    def connection(self): yield self.conn

class ApiTests(unittest.TestCase):
    def setUp(self):
        self.pool=FakePool();api.app.state.pool=self.pool
        # No lifespan here: these tests deliberately isolate HTTP handling from a live DB.
        self.client=TestClient(api.app)
    def test_query_is_bound_and_snippets_remain_text(self):
        query="'); DROP TABLE articles; --"
        response=self.client.get('/search',params={'q':query,'mode':'keyword'})
        self.assertEqual(response.status_code,200)
        sql,params=self.pool.conn.calls[-1]
        self.assertNotIn(query,sql);self.assertEqual(params['q'],query)
        row=response.json()['results'][0]
        self.assertIsNone(row['url'])
        self.assertEqual(row['snippet_parts'][0]['text'],'<img src=x> ')
        self.assertTrue(row['snippet_parts'][1]['highlight'])
    def test_blank_query_rejected(self):
        self.assertEqual(self.client.get('/search',params={'q':'   '}).status_code,422)
        self.assertEqual(self.pool.conn.calls,[])
    def test_mode_and_limit_rejected(self):
        self.assertEqual(self.client.get('/search',params={'q':'ash','mode':'sql'}).status_code,422)
        self.assertEqual(self.client.get('/search',params={'q':'ash','limit':999}).status_code,422)
    def test_zero_weight_does_not_embed(self):
        with patch.object(api,'encode',side_effect=AssertionError('Must not embed')):
            response=self.client.get('/search',params={'q':'ash','semantic_weight':0})
        self.assertEqual(response.json()['mode'],'keyword')
    def test_hybrid_weights_and_vector_bound(self):
        with patch.object(api,'encode',return_value=[1,0,0]):
            response=self.client.get('/search',params={'q':'ash','semantic_weight':0.7})
        self.assertEqual(response.status_code,200)
        params=self.pool.conn.calls[-1][1]
        self.assertAlmostEqual(params['kw_weight'],0.3)
        self.assertEqual(params['embedding'],[1,0,0])
    def test_insert_requires_token(self):
        with patch.dict('os.environ',{'ADMIN_TOKEN':'a-real-test-token'}):
            response=self.client.post('/articles',json={'title':'a','body':'b','url':'https://example.com'})
        self.assertEqual(response.status_code,401)
        self.assertEqual(self.pool.conn.calls,[])

if __name__ == '__main__': unittest.main()
