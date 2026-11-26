import unittest
from planning import kinship,rank,target_probability
class Planning(unittest.TestCase):
 def test_siblings(self):
  f={'a':{},'b':{},'c':{'sire':'a','dam':'b'},'d':{'sire':'a','dam':'b'}}
  self.assertEqual(kinship(f)('c','d'),.25)
 def test_parent(self):
  self.assertEqual(kinship({'a':{},'b':{'sire':'a'}})('a','b'),.25)
 def test_targets(self):
  self.assertEqual(target_probability({'D':'D/+'},{'D':'D/+'},{'D':'D/D'}),(.25,[]))
 def test_unknown(self):
  self.assertEqual(target_probability({}, {}, {'D':'D/D'}),(None,['D']))
 def test_sex(self):
  self.assertEqual(rank({'a':{'sex':'hane'},'b':{'sex':'male'}},{},{'D':'D/D'}),[])
