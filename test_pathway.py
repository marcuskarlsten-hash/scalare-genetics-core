import unittest
from pathway import plan
class Pathway(unittest.TestCase):
 def test_two_loci(self):
  a={'Dark':'D/D','Philippine Blue':'+/+'};b={'Dark':'+/+','Philippine Blue':'pb/pb'};t={'Dark':'D/D','Philippine Blue':'pb/pb'}
  r=plan(a,b,t,3,100);self.assertEqual(r[0]['per_offspring'],0);self.assertAlmostEqual(r[1]['per_offspring'],1/16);self.assertGreater(r[2]['path_probability'],0)
 def test_fixed(self):
  a={'Dark':'D/D'};r=plan(a,a,a,10,2);self.assertEqual(len(r),10);self.assertTrue(all(x['path_probability']==1 for x in r))
 def test_one_fish(self):
  a={'Dark':'D/D'};self.assertEqual(len(plan(a,a,a,5,1)),1)
 def test_missing(self):
  with self.assertRaises(ValueError):plan({}, {'Dark':'D/D'}, {'Dark':'D/D'})
 def test_bounds(self):
  a={'Dark':'D/D'}
  with self.assertRaises(ValueError):plan(a,a,a,11)
 def test_pedigree_cycle(self):
  from planning import kinship
  with self.assertRaises(ValueError):kinship({'A':{'sire':'B'},'B':{'dam':'A'}})
