"""Render ts_headline output as text segments, never trusted HTML."""
import re
from urllib.parse import urlsplit

START = 'WIKISEARCHSTARTTOKEN'
STOP = 'WIKISEARCHSTOPTOKEN'


def snippet_parts(value):
    highlighted = False
    parts = []
    for text in re.split(f'({START}|{STOP})', value or ''):
        if text == START:
            highlighted = True
        elif text == STOP:
            highlighted = False
        elif text:
            parts.append({'text': text, 'highlight': highlighted})
    return parts


def safe_url(value):
    try:
        parsed = urlsplit(value)
        return value if parsed.scheme in ('http', 'https') and parsed.netloc else None
    except ValueError:
        return None
