import os
from pathlib import Path
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / '.env')
MODEL_NAME = 'sentence-transformers/all-MiniLM-L6-v2'
# Pin both documents and queries to the same model revision.
MODEL_REVISION = 'c9745ed1d9f207416be6d2e6f8de32d1f16199bf'
DIMENSIONS = 384


def database_url():
    value = os.getenv('DATABASE_URL')
    if not value:
        raise RuntimeError('Set DATABASE_URL in .env first.')
    return value


def document_text(title, body):
    return title + '\n' + body[:1500]


def new_model():
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer(MODEL_NAME, revision=MODEL_REVISION,
                               device=os.getenv('MODEL_DEVICE', 'cpu'))
