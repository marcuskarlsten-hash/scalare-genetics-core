import unittest
from breeding import *
class Breeding(unittest.TestCase):
 def test_recessive(self): self.assertGreater(test_cross('a','a/a',50,50)['+/a'],.999)
 def test_dominant(self): self.assertGreater(test_cross('D','+/+',50,50,False)['+/D'],.999)
 def test_no_data(self): self.assertAlmostEqual(test_cross('a','a/a',0,0)['+/a'],1/3)
 def test_multi(self):
  d=multi_cross({'A':('a/+','a/+'),'B':('b/+','b/+')}); self.assertEqual(len(d),9);self.assertAlmostEqual(sum(p for _,p in d),1)
 def test_generation(self):
  self.assertEqual(generation('filial','F2','F2'),'F3');self.assertEqual(generation('backcross','BC2'),'BC3')
 def test_invalid(self):
  with self.assertRaises(ValueError):generation('filial','F1','F2')
  with self.assertRaises(ValueError):test_cross('a','b/b',1,2)
