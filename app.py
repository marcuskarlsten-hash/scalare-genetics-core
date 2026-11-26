import sqlite3, json, html, secrets, hashlib, hmac, os, re, base64
from contextlib import closing, contextmanager
from pathlib import Path
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlsplit
from genetics import cross, posterior
ROOT=Path(os.environ.get('SCALARE_DATA',str(Path(__file__).parent/'data'))); ROOT.mkdir(parents=True,exist_ok=True)
DB=ROOT/'scalare.sqlite3'
SCHEMA={
 'fish':('Fiskar','SC', [('name','Namn / variant'),('sex','Kön'),('origin','Ursprung'),('sire_strain','Faderns stam (uppgift)'),('dam_strain','Moderns stam (uppgift)'),('origin_source','Källa till härkomst'),('group','Avelsgrupp (ID)'),('tank','Akvarium (ID)'),('sire','Far (SC-ID)'),('dam','Mor (SC-ID)'),('brood','Kull (ID)'),('generation','Generation (om känd)'),('traits','Observerade egenskaper'),('notes','Anteckningar')]),
 'groups':('Avelsgrupper','AG',[('name','Namn'),('origin','Ursprung'),('notes','Anteckningar')]),
 'tanks':('Akvarier','AK',[('name','Namn'),('volume','Volym liter'),('available','Ledigt för avel (ja/nej)'),('notes','Anteckningar')]),
 'lines':('Avelslinjer','L',[('name','Namn'),('goal','Avelsmål (ID)'),('notes','Strategi')]),
 'goals':('Avelsmål','M',[('name','Namn'),('traits','Önskade egenskaper och prioriteringar'),('targets','Målgenotyper (lokus=allel/allel)'),('notes','Kriterier för stabilitet och hälsa')]),
 'broods':('Kullar / korsningar','K',[('name','Namn'),('sire','Far (SC-ID)'),('dam','Mor (SC-ID)'),('line','Linje (ID)'),('generation','Generation'),('date','Lekdatum'),('count','Antal avkommor'),('traits','Observerad fördelning'),('notes','Anteckningar')]),
 'genes':('Genbibliotek','G',[('name','Lokus / anlag'),('alleles','Alleler'),('inheritance','Nedärvningsmodell'),('source','Källa'),('notes','Evidens och begränsningar')]),
 'evidence':('Genetiska profiler','GP',[('name','Individ eller grupp (ID)'),('locus','Lokus (G-ID eller namn)'),('genotype','Hypotes / genotyp'),('confidence','Status / säkerhetsgrad'),('source','Bevis / testkorsning'),('notes','Anteckningar')])}

@contextmanager
def db():
 with closing(sqlite3.connect(DB,timeout=10)) as c, c:
  c.row_factory=sqlite3.Row
  yield c
with db() as c:
 c.executescript('CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY,name TEXT UNIQUE,salt TEXT,pw TEXT); CREATE TABLE IF NOT EXISTS sessions(token TEXT PRIMARY KEY,uid INTEGER); CREATE TABLE IF NOT EXISTS records(uid INTEGER,kind TEXT,id TEXT,data TEXT,PRIMARY KEY(uid,kind,id)); CREATE TABLE IF NOT EXISTS photos(uid INTEGER,fish TEXT,id TEXT,mime TEXT,blob BLOB,PRIMARY KEY(uid,id));')
def esc(s): return html.escape(str(s),quote=True)
def pw_hash(p,s): return hashlib.pbkdf2_hmac('sha256',p.encode(),bytes.fromhex(s),300000).hex()
def records(c,uid,kind): return [(r['id'],json.loads(r['data'])) for r in c.execute('SELECT * FROM records WHERE uid=? AND kind=? ORDER BY id',(uid,kind))]
def get(c,uid,kind,id):
 r=c.execute('SELECT data FROM records WHERE uid=? AND kind=? AND id=?',(uid,kind,id)).fetchone(); return json.loads(r[0]) if r else None
def nextid(c,uid,kind):
 ids=[int(i.rsplit('-',1)[1]) for i,_ in records(c,uid,kind)]; return f'{SCHEMA[kind][1]}-{max(ids,default=0)+1:05d}'
def validate(c,uid,kind,d,id):
 refs={'fish':{'group':'groups','tank':'tanks','sire':'fish','dam':'fish','brood':'broods'},'broods':{'sire':'fish','dam':'fish','line':'lines'},'lines':{'goal':'goals'}}
 for field,target in refs.get(kind,{}).items():
  val=d.get(field,'');
  if val and (not get(c,uid,target,val) or (target==kind and val==id)): raise ValueError('Ogiltig referens: '+field)
 if kind=='fish':
  def ancestors(x,seen):
   if x==id: raise ValueError('Cirkulär stamtavla')
   if not x or x in seen:return
   seen.add(x); q=get(c,uid,'fish',x) or {}; ancestors(q.get('sire'),seen); ancestors(q.get('dam'),seen)
  for x in (d.get('sire'),d.get('dam')): ancestors(x,set())
 if kind in ('fish','broods') and d.get('sire') and d.get('sire')==d.get('dam'): raise ValueError('Föräldrar måste vara olika individer')
 if kind=='broods' and not d.get('generation'):
  a=get(c,uid,'fish',d.get('sire')) or {}; b=get(c,uid,'fish',d.get('dam')) or {}
  # Generation alone is insufficient to identify a filial relationship across lines.
  d['generation']='Ej fastställd'

def pedigree(c,uid,id,depth=0,seen=None):
 if not id or depth>8:return ''
 seen=set() if seen is None else seen
 if id in seen:return '<li>'+esc(id)+' (återkommande)</li>'
 d=get(c,uid,'fish',id) or {}; seen=seen|{id}
 return '<li>'+esc(id+' '+d.get('name',''))+'<ul>'+pedigree(c,uid,d.get('sire'),depth+1,seen)+pedigree(c,uid,d.get('dam'),depth+1,seen)+'</ul></li>'
STYLE='''body{font:16px system-ui;background:#f4f7f6;color:#19352e;margin:0} header{background:#173f35;color:white;padding:22px} main{max-width:1100px;margin:auto;padding:20px} nav{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:20px} a{color:#17634f} nav a,button{background:#17634f;color:white;padding:9px 13px;border:0;border-radius:6px;text-decoration:none;cursor:pointer} section{background:white;border:1px solid #d6e2dd;border-radius:10px;padding:20px;margin:14px 0} label{display:block;margin:10px 0} input,textarea,select{display:block;width:100%;box-sizing:border-box;padding:8px;border:1px solid #9db5ac;border-radius:5px;font:inherit} textarea{min-height:60px} table{width:100%;border-collapse:collapse} td,th{text-align:left;padding:9px;border-bottom:1px solid #ddd;overflow-wrap:anywhere} .cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:10px}.cards section{margin:0} img{max-width:220px;max-height:180px} small{color:#52665e} .error{color:#a42626}'''
class Handler(BaseHTTPRequestHandler):
 def auth(self,c):
  cookie=self.headers.get('Cookie',''); m=re.search(r'(?:^|;\s*)sgc=([a-f0-9]+)',cookie); token=m.group(1) if m else ''; r=c.execute('SELECT uid FROM sessions WHERE token=?',(token,)).fetchone(); return (r[0] if r else None,token)
 def send(self,body,status=200,headers=None,mime='text/html; charset=utf-8'):
  body=body.encode() if isinstance(body,str) else body; self.send_response(status); self.send_header('Content-Type',mime); self.send_header('Content-Length',str(len(body))); self.send_header('X-Content-Type-Options','nosniff'); self.send_header('Content-Security-Policy',"default-src 'self'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; img-src 'self' data:; frame-ancestors 'none'")
  for k,v in (headers or {}).items(): self.send_header(k,v)
  self.end_headers(); self.wfile.write(body)
 def page(self,body,uid=None,token=''):
  nav=''.join(f'<a href="/?kind={k}">{esc(v[0])}</a>' for k,v in SCHEMA.items()) if uid else ''
  if uid: nav='<a href="/">Översikt</a>'+nav+'<a href="/simulate">Genetikmotor</a><a href="/advice">Avelsråd</a><a href="/export">Export</a><form method="post" action="/logout"><input type="hidden" name="csrf" value="'+token+'"><button>Logga ut</button></form>'
  self.send('<!doctype html><html lang="sv"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Scalare Genetics Core</title><style>'+STYLE+'</style><header><h1>Scalare Genetics Core</h1> Avelsregister · Genetik · Linjeutveckling</header><main><nav>'+nav+'</nav>'+body+'</main></html>')
 def redirect(self,path='/',cookie=None): self.send('',303,{'Location':path,**({'Set-Cookie':cookie} if cookie else {})})
 def form(self,kind,token,d=None,id=''):
  d=d or {}; return '<form method="post" action="/save"><input type="hidden" name="csrf" value="'+token+'"><input type="hidden" name="kind" value="'+kind+'"><input type="hidden" name="id" value="'+esc(id)+'">'+''.join('<label>'+esc(label)+'<textarea name="'+key+'" '+('required' if key=='name' else '')+'>'+esc(d.get(key,''))+'</textarea></label>' for key,label in SCHEMA[kind][2])+'<button>Spara</button></form>'
 def do_GET(self):
  u=urlsplit(self.path); q={k:v[0] for k,v in parse_qs(u.query).items()}
  with db() as c:
   uid,t=self.auth(c)
   if not uid:
    return self.page('<section><h2>Logga in eller skapa konto</h2><form method="post" action="/login"><label>Användarnamn<input name="name" required></label><label>Lösenord (minst 10 tecken vid registrering)<input name="password" type="password" required></label><button name="mode" value="login">Logga in</button> <button name="mode" value="register">Skapa konto</button></form></section>')
   if u.path=='/export':
    data={k:dict(records(c,uid,k)) for k in SCHEMA}; data['photos']=[{'fish':r['fish'],'id':r['id'],'mime':r['mime'],'base64':base64.b64encode(r['blob']).decode()} for r in c.execute('SELECT * FROM photos WHERE uid=?',(uid,))]; return self.send(json.dumps(data,ensure_ascii=False,indent=2),headers={'Content-Disposition':'attachment; filename="scalare-export.json"'},mime='application/json')
   if u.path=='/photo':
    r=c.execute('SELECT mime,blob FROM photos WHERE uid=? AND id=?',(uid,q.get('id'))).fetchone(); return self.send(r['blob'],mime=r['mime']) if r else self.send('Saknas',404)
   if u.path=='/simulate':
    result='';
    if q.get('a') and q.get('b'):
     try: result='<p>'+ ' · '.join(esc(k)+': '+f'{v:.0%}' for k,v in cross(q['a'],q['b']).items())+'</p>'
     except ValueError as e: result='<p class="error">'+esc(e)+'</p>'
    return self.page('<section><h2>Korsningssimulator – ett lokus</h2><p>Angivna diploida genotyper; ingen automatisk fenotypgissning. Exempel D/+ × D/+.</p><form><label>Förälder A<input name="a" value="'+esc(q.get('a','D/+'))+'"></label><label>Förälder B<input name="b" value="'+esc(q.get('b','D/+'))+'"></label><button>Beräkna</button></form>'+result+'</section>',uid,t)
   if u.path=='/advice':
    fs=records(c,uid,'fish'); pairs=[]
    def anc(id,depth=0):
     if not id or depth>8:return set()
     d=get(c,uid,'fish',id) or {}; return {id}|anc(d.get('sire'),depth+1)|anc(d.get('dam'),depth+1)
    for i,(a,da) in enumerate(fs):
     for b,dd in fs[i+1:]:
      overlap=anc(a)&anc(b); pairs.append((len(overlap),a,b,da.get('name',''),dd.get('name','')))
    pairs.sort(); rows=''.join('<tr><td>'+esc(a+' '+an)+'</td><td>'+esc(b+' '+bn)+'</td><td>'+str(n)+'</td></tr>' for n,a,b,an,bn in pairs[:100]); return self.page('<section><h2>Preliminärt parurval</h2><p>Sorterat efter antal gemensamma kända individer i stamtavlan, inte faktisk inavelsgrad. Okänt släktskap innebär inte obesläktade fiskar. Kontrollera kön, hälsa, mål och genetik före korsning.</p><table><tr><th>Fisk A</th><th>Fisk B</th><th>Överlapp</th></tr>'+rows+'</table></section>',uid,t)
   kind=q.get('kind'); id=q.get('id','')
   if kind in SCHEMA:
    if id:
     d=get(c,uid,kind,id)
     if d is None:return self.send('Saknas',404)
     body='<section><h2>'+esc(id+' '+d.get('name',''))+'</h2>'+self.form(kind,t,d,id)+'</section>'
     if kind=='fish':
      photos=''.join('<img src="/photo?id='+esc(r[0])+'">' for r in c.execute('SELECT id FROM photos WHERE uid=? AND fish=?',(uid,id)))
      body+='<section><h2>Fotografier</h2>'+photos+'<form method="post" action="/upload"><input type="hidden" name="csrf" value="'+t+'"><input type="hidden" name="fish" value="'+esc(id)+'"><input type="hidden" name="image" id="image"><input type="file" accept="image/jpeg,image/png,image/webp" onchange="let f=this.files[0];if(f.size>5000000){alert(\'Max 5 MB\');this.value=\'\';return}let r=new FileReader();r.onload=()=>document.getElementById(\'image\').value=r.result;r.readAsDataURL(f)"><button>Lägg till foto</button></form><h2>Stamtavla</h2><ul>'+pedigree(c,uid,id)+'</ul></section>'
     return self.page(body,uid,t)
    rows=''.join('<tr><td><a href="/?kind='+kind+'&id='+esc(i)+'">'+esc(i)+'</a></td><td>'+esc(d.get('name',''))+'</td><td>'+esc(d.get('generation',d.get('notes',''))[:100])+'</td></tr>' for i,d in records(c,uid,kind)); return self.page('<section><h2>'+SCHEMA[kind][0]+'</h2><table><tr><th>ID</th><th>Namn</th><th>Info</th></tr>'+rows+'</table></section><section><h2>Ny registrering</h2>'+self.form(kind,t)+'</section>',uid,t)
   return self.page('<h2>Din odling</h2><div class="cards">'+''.join('<section><a href="/?kind='+k+'">'+v[0]+'</a><h2>'+str(len(records(c,uid,k)))+'</h2></section>' for k,v in SCHEMA.items())+'</div><section>Registrera avelsdjur, definiera egna mål och dokumentera genetiska bevis. Okända genotyper ska förbli okända tills underlag finns.</section>',uid,t)
 def do_POST(self):
  try:
   n=int(self.headers.get('Content-Length','0'))
   if n>10000000:return self.send('För stor begäran',413)
   p={k:v[0] for k,v in parse_qs(self.rfile.read(n).decode(),keep_blank_values=True).items()}; path=urlsplit(self.path).path
   with db() as c:
    uid,t=self.auth(c)
    if path=='/login':
     name=p.get('name','').strip(); password=p.get('password',''); r=c.execute('SELECT * FROM users WHERE name=?',(name,)).fetchone()
     if p.get('mode')=='register':
      if not name or len(password)<10 or r:raise ValueError('Ogiltigt eller upptaget namn, eller för kort lösenord')
      salt=secrets.token_hex(16); uid=c.execute('INSERT INTO users(name,salt,pw) VALUES(?,?,?)',(name,salt,pw_hash(password,salt))).lastrowid
     else:
      if not r or not hmac.compare_digest(r['pw'],pw_hash(password,r['salt'])):raise ValueError('Fel inloggning')
      uid=r['id']
     token=secrets.token_hex(32); c.execute('INSERT INTO sessions VALUES(?,?)',(token,uid)); c.commit();return self.redirect(cookie='sgc='+token+'; HttpOnly; SameSite=Strict; Path=/')
    if not uid or not hmac.compare_digest(t,p.get('csrf','')):return self.send('Åtkomst nekad',403)
    if path=='/logout':c.execute('DELETE FROM sessions WHERE token=?',(t,));c.commit();return self.redirect(cookie='sgc=; Max-Age=0; Path=/')
    if path=='/save':
     kind=p.get('kind'); fields=SCHEMA[kind][2]; d={k:p.get(k,'').strip() for k,_ in fields}; c.execute('BEGIN IMMEDIATE'); id=p.get('id') or nextid(c,uid,kind)
     if p.get('id') and get(c,uid,kind,id) is None:raise ValueError('Okänd post')
     if not d['name']:raise ValueError('Namn krävs')
     validate(c,uid,kind,d,id); c.execute('INSERT OR REPLACE INTO records VALUES(?,?,?,?)',(uid,kind,id,json.dumps(d,ensure_ascii=False)));c.commit();return self.redirect('/?kind='+kind+'&id='+id)
    if path=='/upload':
     fish=p.get('fish'); raw=p.get('image',''); m=re.fullmatch(r'data:(image/(?:jpeg|png|webp));base64,(.+)',raw)
     if not get(c,uid,'fish',fish) or not m:raise ValueError('Ogiltig fisk eller bild')
     blob=base64.b64decode(m[2],validate=True); mime=m[1]; valid=(mime=='image/jpeg' and blob.startswith(b'\xff\xd8')) or (mime=='image/png' and blob.startswith(b'\x89PNG\r\n\x1a\n')) or (mime=='image/webp' and blob[:4]==b'RIFF' and blob[8:12]==b'WEBP')
     if not valid or len(blob)>5000000:raise ValueError('Ogiltig bild eller för stor')
     c.execute('INSERT INTO photos VALUES(?,?,?,?,?)',(uid,fish,secrets.token_hex(16),mime,blob));c.commit();return self.redirect('/?kind=fish&id='+fish)
    return self.send('Saknas',404)
  except (ValueError,KeyError,sqlite3.Error) as e:self.page('<section class="error">'+esc(str(e))+' <a href="/">Tillbaka</a></section>')
if __name__=='__main__':
 host=os.environ.get('SCALARE_HOST','127.0.0.1'); port=int(os.environ.get('SCALARE_PORT','8765')); print(f'Öppna http://{host}:{port}',flush=True); ThreadingHTTPServer((host,port),Handler).serve_forever()
