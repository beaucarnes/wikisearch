import unittest
from safety import snippet_parts,safe_url,START,STOP

class SafetyTests(unittest.TestCase):
    def test_html_stays_plain_text(self):
        parts=snippet_parts('<script>alert(1)</script> '+START+'ash'+STOP)
        self.assertEqual(parts[0]['text'],'<script>alert(1)</script> ')
        self.assertEqual(parts[1],{'text':'ash','highlight':True})
    def test_rejects_script_urls(self):
        for url in ['javascript:alert(1)','data:text/html,x','//evil.example','https://[']:
            self.assertIsNone(safe_url(url))
    def test_source_link(self):
        self.assertEqual(safe_url('https://simple.wikipedia.org/wiki/Volcano'),'https://simple.wikipedia.org/wiki/Volcano')

if __name__ == '__main__': unittest.main()
