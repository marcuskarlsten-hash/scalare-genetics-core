import unittest,tempfile,sqlite3
from pathlib import Path
from release_tools import snapshot,restore,brood_probability,atomic_json
class Release(unittest.TestCase):
 def test_shared_uncertainty(self):
  p,q=brood_probability('Dark',{'D/D':.5,'+/+':.5},{'D/D':1},'D/D',100)
  self.assertAlmostEqual(p,.5);self.assertAlmostEqual(q,.5)
 def test_fixed(self):
  p,q=brood_probability('Dark',{'D/+':1},{'D/+':1},'D/D',2)
  self.assertAlmostEqual(p,.25);self.assertAlmostEqual(q,.4375)
 def test_snapshot(self):
  with tempfile.TemporaryDirectory() as d:
   a,b=Path(d)/'a',Path(d)/'b'
   with sqlite3.connect(a) as c:c.execute('create table x(y)');c.execute('insert into x values(1)')
   snapshot(a,b)
   with sqlite3.connect(b) as c:self.assertEqual(c.execute('select y from x').fetchone()[0],1)
   with self.assertRaises(ValueError):snapshot(a,a)
   with self.assertRaises(ValueError):restore(a,b)
 def test_json(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'out.json';atomic_json(p,{'x':'å'});self.assertIn('å',p.read_text())
 def test_valid_restore(self):
  with tempfile.TemporaryDirectory() as d:
   a,b=Path(d)/'a',Path(d)/'b'
   for p in (a,b):
    with sqlite3.connect(p) as c:c.executescript('CREATE TABLE users(id,name,salt,pw);CREATE TABLE sessions(token,uid);CREATE TABLE records(uid,kind,id,data);CREATE TABLE photos(uid,fish,id,mime,blob);')
   with sqlite3.connect(a) as c:c.execute("insert into users values(1,'test','x','y')")
   restore(a,b)
   with sqlite3.connect(b) as c:self.assertEqual(c.execute('select name from users').fetchone()[0],'test')
   self.assertEqual(len(list(Path(d).glob('before-restore-*.sqlite3'))),1)
 def test_integrated_uncertain(self):
  from integrated import proposals
  fish={'a':{'sex':'hane'},'b':{'sex':'hona'}}
  r=proposals(fish,{'a':{'Dark':({'D/D':.5,'+/+':.5},'test')},'b':{'Dark':({'D/D':1},'test')}},{'Dark':'D/D'},100,0)[0]
  self.assertAlmostEqual(r['at_least_one'],.5)
