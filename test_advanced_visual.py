import unittest
from advanced_visual import simulate,at_least_one
class AdvancedTests(unittest.TestCase):
 def test_multi(self):
  a={'Dark':'D/+','Philippine Blue':'+/pb'};r=simulate(a,a,{'Dark':'D/D','Philippine Blue':'pb/pb'});self.assertEqual(len(r),9);self.assertAlmostEqual(sum(x[1] for x in r),1);self.assertEqual(r[0][1],.0625);self.assertIsNone(r[0][3])
 def test_missing(self):
  with self.assertRaises(ValueError):simulate({'Dark':'D/D'},{'Albino':'a/a'})
 def test_at_least(self):self.assertAlmostEqual(at_least_one(.5,2),.75)
 def test_reference(self):self.assertEqual(simulate({'Dark':'D/D'},{'Dark':'D/D'})[0][3],'black')
