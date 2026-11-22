import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from source import parse_pco
class SourceTests(unittest.TestCase):
 def test_malformed_source_columns_fail_closed(self):
  with self.assertRaises(ValueError):parse_pco(b'<table id="results"><tbody><tr><td>2026-0001</td></tr></tbody></table>')
