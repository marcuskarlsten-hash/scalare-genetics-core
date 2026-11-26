import unittest, tempfile, os, subprocess, sys, time, urllib.request, urllib.parse, http.cookiejar, socket, json
from genetics import cross, posterior
class Genetics(unittest.TestCase):
 def test_cross(self): self.assertEqual(cross('D/+','D/+'),{'+/+':.25,'+/D':.5,'D/D':.25})
 def test_recessive(self): self.assertEqual(cross('a/a','+/+'),{'+/a':1})
 def test_posterior(self): self.assertEqual(posterior([('a',.5,{'black':1}),('b',.5,{'black':0})],{'black':2}),{'a':1,'b':0})
 def test_invalid(self):
  with self.assertRaises(ValueError):cross('D','+/+')
class Web(unittest.TestCase):
 def test_workflow(self):
  with tempfile.TemporaryDirectory() as d:
   with socket.socket() as s:s.bind(('127.0.0.1',0));port=s.getsockname()[1]
   p=subprocess.Popen([sys.executable,'app.py'],env={**os.environ,'SCALARE_DATA':d,'SCALARE_PORT':str(port)},stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
   try:
    base=f'http://127.0.0.1:{port}'; jar=http.cookiejar.CookieJar(); op=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
    def request(path,data=None):return op.open(base+path, None if data is None else urllib.parse.urlencode(data).encode(),timeout=5).read().decode()
    for i in range(50):
     try:request('/');break
     except OSError:time.sleep(.1)
    request('/login',{'name':'one','password':'longpassword','mode':'register'}); token=next(x.value for x in jar if x.name=='sgc'); self.assertIn('Din odling',request('/'))
    request('/save',{'csrf':token,'kind':'fish','name':'Testfisk'}); self.assertIn('SC-00001',request('/?kind=fish')); request('/save',{'csrf':token,'kind':'fish','name':'Avkomma','sire':'SC-00001'}); self.assertIn('Testfisk',request('/?kind=fish&id=SC-00002'))
    self.assertIn('25%',request('/simulate?a=D%2F%2B&b=D%2F%2B')); self.assertEqual(len(json.loads(request('/export'))['fish']),2)
    request('/logout',{'csrf':token});request('/login',{'name':'two','password':'longpassword','mode':'register'});self.assertEqual(json.loads(request('/export'))['fish'],{})
   finally:p.terminate();p.wait(timeout=5)
if __name__=='__main__':unittest.main()
