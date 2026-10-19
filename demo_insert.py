"""Insert original course content into the running local API using ADMIN_TOKEN."""
import json
import os
from urllib.request import Request,urlopen
import settings  # loads the project's .env

payload={'title':'quokkatapir search demo',
         'url':'https://example.com',
         'body':'quokkatapir is the original course demo article. PostgreSQL stores its text and vector together. Keyword and hybrid search can find the committed article without copying it to another search server.'}
if __name__ == '__main__':
    token=os.getenv('ADMIN_TOKEN','')
    if not token or token.startswith('replace-this'):
        raise SystemExit('Configure a random ADMIN_TOKEN in .env first.')
    request=Request('http://127.0.0.1:8000/articles',data=json.dumps(payload).encode(),
                    headers={'Content-Type':'application/json','X-Admin-Token':token},method='POST')
    with urlopen(request,timeout=180) as response:
        print(response.read().decode())
