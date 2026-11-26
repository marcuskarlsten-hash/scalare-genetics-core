import unittest,tempfile,sqlite3
from contextlib import closing
from pathlib import Path
from demo import seed
class DemoTest(unittest.TestCase):
 def test_seed(self):
  with tempfile.TemporaryDirectory() as d:
   path=Path(d)/'demo.sqlite3';seed(path)
   with closing(sqlite3.connect(path)) as c, c:
    self.assertEqual(c.execute("select count(*) from records where kind='fish'").fetchone()[0],4)
    self.assertEqual(c.execute('select count(*) from photos').fetchone()[0],4)
 def test_demo_ui_isolation(self):
  from desktop import Desktop,core
  old=core.DB
  with tempfile.TemporaryDirectory() as d:
   real=Path(d)/'real.sqlite3'; seed(real); core.DB=real
   win=Desktop()
   try:
    win.open_demo();win.update();self.assertNotEqual(core.DB,real);self.assertEqual(win.uid,1)
    win.visual_ui();win.update();win.login();win.update();self.assertEqual(core.DB,real)
   finally:
    win.destroy();core.DB=old
