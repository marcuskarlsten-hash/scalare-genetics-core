import unittest
from intelligence import ancestry,recommend,normalize
class Intelligence(unittest.TestCase):
 def test_ancestry(self):
  self.assertEqual(ancestry('Dark',{'+/D':1},{'+/D':1}),{'+/+':.25,'+/D':.5,'D/D':.25})
 def test_mixture(self):
  self.assertEqual(ancestry('Dark',{'+/+':1,'D/D':1},{'+/+':1}),{'+/+':.5,'+/D':.5})
 def test_rank(self):
  rows=recommend('Albino',{'+/+':1,'+/a':1},['+/+','a/a'],['a/a']);self.assertEqual(rows[0][0],'a/a');self.assertGreater(rows[0][1],0);self.assertEqual(rows[1][1],0)
 def test_invalid(self):
  for p in [-1,float('nan'),0]:
   with self.assertRaises(ValueError):normalize('Dark',{'D/D':p})
 def test_canonical(self):
  self.assertEqual(normalize('Dark',{'D/+':1,'+/D':1}),{'+/D':1})
