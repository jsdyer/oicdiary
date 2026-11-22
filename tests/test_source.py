import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from source import parse_pco
class SourceTests(unittest.TestCase):
 def test_malformed_source_columns_fail_closed(self):
  with self.assertRaises(ValueError):parse_pco(b'<table id="results"><tbody><tr><td>2026-0001</td></tr></tbody></table>')

class PaginationTests(unittest.TestCase):
 def test_numbered_tail_pages_are_not_lost_when_next_hint_is_absent(self):
  raw=b'<ul class="pagination"><li><a href="results.php?pageNum=27&amp;lang=en">27</a></li><li class="active"><a href="results.php?pageNum=28&amp;lang=en">28</a></li><li><a href="results.php?pageNum=29&amp;lang=en">29</a></li><li><a href="results.php?pageNum=33&amp;lang=en">33</a></li></ul>'
  self.assertEqual(parse_pco(raw)[1],'https://orders-in-council.canada.ca/results.php?pageNum=29&lang=en')
 def test_last_numbered_page_ends_capture(self):
  raw=b'<ul class="pagination"><li><a href="results.php?pageNum=32&amp;lang=en">32</a></li><li class="active"><a href="results.php?pageNum=33&amp;lang=en">33</a></li></ul>'
  self.assertIsNone(parse_pco(raw)[1])
