import unittest, io, sqlite3, json
from PIL import Image,ImageDraw
from visual import measure,forecast_dark,mixed_forecast,ancestry_scenarios
class VisualTests(unittest.TestCase):
 def test_pixels(self):
  im=Image.new('RGB',(100,100),'white');ImageDraw.Draw(im).rectangle((25,25,74,74),fill='black');b=io.BytesIO();im.save(b,format='PNG');r=measure(b.getvalue());self.assertEqual(r['dark_fraction'],1);self.assertEqual(r['height_width'],1)
 def test_background(self):
  b=io.BytesIO();Image.new('RGB',(100,100),'red').save(b,format='PNG');self.assertRaises(ValueError,measure,b.getvalue())
 def test_dark(self):
  self.assertEqual({g:p for g,p,*_ in forecast_dark('D/+','D/+')},{'D/D':.25,'+/D':.5,'+/+':.25})
 def test_unknown(self):
  self.assertRaises(ValueError,mixed_forecast,{}, {'D/D':1})
 def test_other_allele(self):
  self.assertIsNone(forecast_dark('M/M','M/M')[0][3])
 def test_ancestry(self):
  import app
  c=sqlite3.connect(':memory:');c.row_factory=sqlite3.Row;c.execute('CREATE TABLE records(uid,kind,id,data)')
  def put(uid,k,i,d):c.execute('INSERT INTO records VALUES(?,?,?,?)',(uid,k,i,json.dumps(d)))
  put(1,'fish','child',{'sire':'a','dam':'b','sire_strain':'Black'});put(1,'evidence','1',dict(name='a',locus='Dark',confidence='confirmed',genotype='D/D'));put(2,'evidence','2',dict(name='b',locus='Dark',confidence='confirmed',genotype='+/+'))
  self.assertEqual(ancestry_scenarios(c,1,'child')[0],{})
  put(1,'evidence','2',dict(name='b',locus='Dark',confidence='confirmed',genotype='+/+'));self.assertEqual(ancestry_scenarios(c,1,'child')[0],{'+/D':1})
 def test_mixture(self):
  r=mixed_forecast({'D/D':.5,'+/+':.5},{'+/+':1});self.assertEqual({g:p for g,p,*_ in r},{'+/D':.5,'+/+':.5})
