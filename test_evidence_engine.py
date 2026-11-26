import unittest
from evidence_engine import infer,save_observation
class EvidenceTests(unittest.TestCase):
 def test_carrier(self):
  r=infer('a',[dict(tester='a/a',affected=20,normal=20,recessive=True)])
  self.assertGreater(r['+/a'],.999)
 def test_multiple(self):
  o=dict(tester='a/a',affected=0,normal=5,recessive=True)
  self.assertGreater(infer('a',[o,o])['+/+'],infer('a',[o])['+/+'])
 def test_wrong_allele(self):
  with self.assertRaises(ValueError):infer('a',[dict(tester='D/D',affected=1,normal=1,recessive=True)])
