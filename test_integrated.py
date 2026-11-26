import unittest
from integrated import profiles,proposals,allocate,chance
class Integration(unittest.TestCase):
 def setUp(self):
  self.fish={'a':{'sex':'hane'},'b':{'sex':'hona'},'c':{'sire':'a','dam':'b','sex':'hona'}}
  self.e=[('1',dict(name='a',locus='Dark',genotype='+/D',confidence='confirmed')),('2',dict(name='b',locus='Dark',genotype='+/D',confidence='confirmed'))]
 def test_ancestry(self):
  self.assertEqual(profiles(self.fish,self.e,['Dark'])['c']['Dark'][0]['D/D'],.25)
 def test_conflict(self):
  self.e.append(('3',dict(name='a',locus='Dark',genotype='D/D',confidence='confirmed')));self.assertFalse(profiles(self.fish,self.e,['Dark'])['a']['Dark'][0])
 def test_plan(self):
  r=proposals(self.fish,profiles(self.fish,self.e,['Dark']),{'Dark':'D/D'},10,.125);self.assertEqual(len(r),1);self.assertAlmostEqual(r[0]['p'],.25);self.assertAlmostEqual(r[0]['at_least_one'],1-.75**10);self.assertEqual(allocate(r,['tank'])[0]['tank'],'tank')
 def test_uncertain_siblings(self):
  r=proposals(self.fish,profiles(self.fish,self.e,['Dark']),{'Dark':'D/D'},10,1);self.assertIsNone(next(x for x in r if x['b']=='c')['at_least_one'])
 def test_missing(self):
  r=proposals(self.fish,profiles(self.fish,[],['Dark']),{'Dark':'D/D'},10,1);self.assertIsNone(r[0]['p']);self.assertEqual(allocate(r,['t']),[])
 def test_chance(self):self.assertEqual(chance(1,1),1);self.assertEqual(chance(0,100),0)
