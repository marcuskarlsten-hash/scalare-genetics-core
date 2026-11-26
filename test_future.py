import unittest
from future import forecast,parse_profile
class FutureTests(unittest.TestCase):
 def test_f2(self):
  r=forecast({'Dark':'D/D'},{'Dark':'+/+'},{'Dark':'D/D'})
  self.assertEqual(r,{'F1':0,'F2':.25,'BC1-A':.5,'BC1-B':0})
 def test_two_loci(self):
  a=parse_profile('Dark=D/D, Philippine Blue=+/+');b=parse_profile('Dark=+/+, Philippine Blue=pb/pb');t=parse_profile('Dark=D/D, Philippine Blue=pb/pb')
  self.assertEqual(forecast(a,b,t)['F2'],.0625)
 def test_invalid(self):
  with self.assertRaises(ValueError):parse_profile('Dark=D/pb')
 def test_unknown(self):
  with self.assertRaises(ValueError):forecast({}, {}, {'Dark':'D/D'})
 def test_custom(self):
  self.assertEqual(parse_profile('New=q/q'),{'New':'q/q'})
