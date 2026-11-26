import unittest,io
from PIL import Image
from phenotype_preview import preview,eye_region
class PreviewTests(unittest.TestCase):
 def test_blue(self):
  a=preview({'Dark':'D/D'});b=preview({'Dark':'D/D','Philippine Blue':'pb/pb'});self.assertEqual(a.size,b.size);self.assertNotEqual(a.tobytes(),b.tobytes())
 def test_unknown(self):self.assertIsNone(preview({'Dark':'D/D','Albino':'a/a'}))
 def test_eye(self):
  b=io.BytesIO();Image.new('RGB',(20,20),(180,20,20)).save(b,format='PNG');self.assertEqual(eye_region(b.getvalue(),(.1,.1,.9,.9)),1)
 def test_bounds(self):
  with self.assertRaises(ValueError):eye_region(b'',(1,0,0,1))
