import os, sys, json, sqlite3, secrets, hmac, io
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
os.environ.setdefault('SCALARE_DATA',str(Path(os.getenv('LOCALAPPDATA',str(Path.home()/'.local/share')))/'ScalareGenetics'))
import app as core
from genetics import cross
from breeding import test_cross, multi_cross, generation

class Desktop(tk.Tk):
 def __init__(self):
  super().__init__(); self.title('Scalare Genetics Core 0.14.0'); self.geometry('1120x760'); self.minsize(800,550); self.uid=None; self.demo_tmp=None; self.real_db=core.DB
  self.style=ttk.Style(self); self.style.theme_use('clam'); self.style.configure('TButton',padding=7); self.style.configure('Title.TLabel',font=('Segoe UI',20,'bold')); self.login()
 def clear(self):
  for w in self.winfo_children(): w.destroy()
 def login(self):
  if self.demo_tmp is not None:
   core.DB=self.real_db; self.demo_tmp.cleanup(); self.demo_tmp=None
  self.title('Scalare Genetics Core 0.14.0')
  self.clear(); self.uid=None; f=ttk.Frame(self,padding=40); f.pack(expand=True); ttk.Label(f,text='Scalare Genetics Core',style='Title.TLabel').pack(pady=15)
  ttk.Label(f,text='Lokalt användarkonto').pack(); name=ttk.Entry(f,width=35); name.pack(pady=6); ttk.Label(f,text='Lösenord').pack(); pw=ttk.Entry(f,show='•',width=35); pw.pack(pady=6)
  def auth(create=False):
   try:
    n=name.get().strip(); p=pw.get()
    with core.db() as c:
     r=c.execute('SELECT * FROM users WHERE name=?',(n,)).fetchone()
     if create:
      if not n or len(p)<10 or r: raise ValueError('Namn måste vara ledigt och lösenord minst 10 tecken.')
      s=secrets.token_hex(16); self.uid=c.execute('INSERT INTO users(name,salt,pw) VALUES(?,?,?)',(n,s,core.pw_hash(p,s))).lastrowid
     else:
      if not r or not hmac.compare_digest(r['pw'],core.pw_hash(p,r['salt'])): raise ValueError('Fel inloggning')
      self.uid=r['id']
    self.home()
   except Exception as e: messagebox.showerror('Inloggning',str(e))
  ttk.Button(f,text='Logga in',command=auth).pack(fill='x',pady=4); ttk.Button(f,text='Skapa konto',command=lambda:auth(True)).pack(fill='x')
  ttk.Button(f,text='Prova demoläge',command=self.open_demo).pack(fill='x',pady=12)
 def open_demo(self):
  import tempfile
  from demo import seed
  try:
   self.demo_tmp=tempfile.TemporaryDirectory(prefix='scalare-demo-'); p=Path(self.demo_tmp.name)/'demo.sqlite3'; seed(p); core.DB=p; self.uid=1; self.title('Scalare Genetics Core – DEMO (fiktiva data)'); self.home()
  except Exception as e:
   self.login(); messagebox.showerror('Demo',str(e))
 def home(self,kind='fish'):
  self.clear(); navwrap=ttk.Frame(self); navwrap.pack(side='left',fill='y'); nc=tk.Canvas(navwrap,width=205,highlightthickness=0); ns=ttk.Scrollbar(navwrap,orient='vertical',command=nc.yview); ns.pack(side='right',fill='y'); nc.pack(side='left',fill='y'); nc.configure(yscrollcommand=ns.set); nav=ttk.Frame(nc,padding=8); nw=nc.create_window((0,0),window=nav,anchor='nw'); nav.bind('<Configure>',lambda e:nc.configure(scrollregion=nc.bbox('all'))); nc.bind('<Configure>',lambda e:nc.itemconfigure(nw,width=e.width)); self.main=ttk.Frame(self,padding=18); self.main.pack(side='left',fill='both',expand=True)
  ttk.Label(nav,text='SCALARE',font=('Segoe UI',16,'bold')).pack(pady=12)
  for k,v in core.SCHEMA.items(): ttk.Button(nav,text=v[0],command=lambda k=k:self.home(k)).pack(fill='x',pady=2)
  for label,fn in [('Genetiskt pass & avelsplan',self.integrated_ui),('Visuell korsning',self.visual_ui),('Flera genlokus',self.multi_visual_ui),('Korsningssimulator',self.simulator),('Testkorsning',self.test_cross_ui),('Kartlägg individ',self.mapping_ui),('Generationshjälp',self.generation_ui),('Avelsråd',self.advice),('Målstyrda korsningar',self.target_ui),('Härkomst & testval',self.intelligence_ui),('Genbibliotek',self.catalog_ui),('F1/F2-planering',self.future_ui),('F1–F10 urvalsplan',self.pathway_ui),('Exportera mitt konto',self.export_account),('Återställ säkerhetskopia',self.restore_backup),('Säkerhetskopia',self.backup),('Logga ut',self.login)]: ttk.Button(nav,text=label,command=fn).pack(fill='x',pady=2)
  self.listing(kind)
 def integrated_ui(self):
  from integrated import profiles,proposals,allocate
  from future import parse_profile
  self.reset('Genetiskt pass och avelsplan')
  with core.db() as c:
   fish=dict(core.records(c,self.uid,'fish')); evidence=core.records(c,self.uid,'evidence'); goals=dict(core.records(c,self.uid,'goals')); tanks=dict(core.records(c,self.uid,'tanks'))
  goal=tk.StringVar(); ttk.Label(self.main,text='Sparat avelsmål (valfritt)').pack(anchor='w'); selector=ttk.Combobox(self.main,textvariable=goal,values=list(goals),state='readonly');selector.pack(fill='x')
  target=tk.StringVar(value='Dark=D/D'); ttk.Label(self.main,text='Målgenotyper').pack(anchor='w');ttk.Entry(self.main,textvariable=target).pack(fill='x');selector.bind('<<ComboboxSelected>>',lambda e:target.set(goals[goal.get()].get('targets','')))
  bar=ttk.Frame(self.main);bar.pack(fill='x'); n=tk.StringVar(value='100'); limit=tk.StringVar(value='12.5');ttk.Label(bar,text='Kullstorlek').pack(side='left');ttk.Entry(bar,textvariable=n,width=8).pack(side='left');ttk.Label(bar,text='Max beräknad inavel (%)').pack(side='left');ttk.Entry(bar,textvariable=limit,width=8).pack(side='left')
  out=tk.Text(self.main,wrap='word');out.pack(fill='both',expand=True)
  def run():
   try:
    t=parse_profile(target.get()); pr=profiles(fish,evidence,t); rows=proposals(fish,pr,t,int(n.get()),float(limit.get())/100)
    occupied={d.get('tank') for d in fish.values()}; free=[k for k,d in tanks.items() if d.get('available','').strip().lower() in ('ja','yes') and k not in occupied]; plan=allocate(rows,free)
    lines=['VILLKORAD PROGNOS – oberoende lokus och föräldraprofiler; okända grundare antas obesläktade. Kontrollera hälsa, släktskap och fertilitet.','GENETISKA PASS']
    for id,ls in pr.items():
     lines.append(id+' '+fish[id].get('name',''))
     for l,(dist,source) in ls.items():lines.append('  '+l+': '+(', '.join(f'{g} {p:.1%}' for g,p in dist.items()) or 'Okänd')+' – '+source)
    lines.append('\nRANGORDNADE PAR')
    for r in rows[:500]:
     p='Okänd' if r['p'] is None else f"{r['p']:.2%}"; q='Ej beräknad' if r['at_least_one'] is None else f"{r['at_least_one']:.2%}"
     lines.append(f"{r['a']} × {r['b']}: mål {p}; minst en {q}; inavel {r['f']:.2%}"+(' / kön okänt' if r['sex_unknown'] else ''))
    lines.append('\nFÖRSLAG PÅ PARALLELLA KORSNINGAR (ett ledigt akvarium per par; preliminärt)')
    lines.extend(f"{r['tank']}: {r['a']} × {r['b']}" for r in plan);lines.append('Inga lämpliga lediga platser eller par.' if not plan else 'Kontrollera även utrymme för yngel innan start.')
    out.delete('1.0','end');out.insert('end','\n'.join(lines))
   except Exception as e:messagebox.showerror('Avelsplan',str(e))
  def export():
   p=filedialog.asksaveasfilename(defaultextension='.txt',filetypes=[('Text','*.txt')]);
   if p:Path(p).write_text(out.get('1.0','end'),encoding='utf-8')
  ttk.Button(bar,text='Analysera',command=run).pack(side='left');ttk.Button(bar,text='Exportera',command=export).pack(side='left')
 def intelligence_ui(self):
  from intelligence import ancestry,recommend
  self.reset('Härkomst och genetiska testkorsningar')
  ttk.Label(self.main,text='Villkorad modell: ange kända eller antagna genotyper och vikter. Stamnamn är inte genetiska bevis.',wraplength=700).pack(anchor='w')
  fields={}
  for key,label,value in [('locus','Genlokus','Dark'),('father','Fader: genotyp:vikt, separerade med komma','+/D:1'),('mother','Moder: genotyp:vikt','+/D:1'),('testers','Möjliga testfiskars genotyper','+/+, +/D, D/D'),('affected','Genotyper som ger observerad egenskap','D/D')]:
   ttk.Label(self.main,text=label).pack(anchor='w');v=tk.StringVar(value=value);fields[key]=v;ttk.Entry(self.main,textvariable=v).pack(fill='x')
  output=tk.Text(self.main,height=15,wrap='word');output.pack(fill='both',expand=True)
  def parse(s):
   pairs=[x.strip().rsplit(':',1) for x in s.split(',')];return {g.strip():float(p) for g,p in pairs}
  def run():
   try:
    f={k:v.get().strip() for k,v in fields.items()};d=ancestry(f['locus'],parse(f['father']),parse(f['mother']));rows=recommend(f['locus'],d,[x.strip() for x in f['testers'].split(',')],[x.strip() for x in f['affected'].split(',')]);output.delete('1.0','end');output.insert('end','Möjliga genotyper hos avkomman (modellberoende):\n'+'\n'.join(f'{g}: {p:.1%}' for g,p in d.items())+'\n\nTestval för en individ ur avkomman (per bedömd avkomma):\n'+'\n'.join(f'{g}: {bits:.3f} bit; observerad egenskap {p:.1%}' for g,bits,p in rows)+'\n\nAntaganden: oberoende föräldraprofiler, korrekt fenotypregel och lika överlevnad. Kontrollera tillgänglighet och släktskap separat.')
   except Exception as e:messagebox.showerror('Genetisk modell',str(e))
  ttk.Button(self.main,text='Beräkna härkomst och rangordna testfiskar',command=run).pack(anchor='w')
 def reset(self,title):
  for w in self.main.winfo_children():w.destroy()
  ttk.Label(self.main,text=title,style='Title.TLabel').pack(anchor='w',pady=(0,12))
 def listing(self,k):
  self.reset(core.SCHEMA[k][0]); bar=ttk.Frame(self.main); bar.pack(fill='x'); ttk.Button(bar,text='+ Ny registrering',command=lambda:self.edit(k)).pack(side='left'); query=tk.StringVar(); ttk.Entry(bar,textvariable=query).pack(side='right'); ttk.Label(bar,text='Sök: ').pack(side='right')
  if k=='fish':ttk.Button(bar,text='+ Registrera från foto',command=self.photo_new).pack(side='left',padx=4)
  tree=ttk.Treeview(self.main,columns=('id','name','info'),show='headings'); tree.pack(fill='both',expand=True,pady=12)
  for key,label,width in [('id','ID',110),('name','Namn',240),('info','Information',300)]:tree.heading(key,text=label);tree.column(key,width=width)
  def refresh(*_):
   tree.delete(*tree.get_children()); q=query.get().casefold()
   with core.db() as c:
    for id,d in core.records(c,self.uid,k):
     if q in (id+' '+json.dumps(d,ensure_ascii=False)).casefold():tree.insert('', 'end',iid=id,values=(id,d.get('name',''),d.get('generation') or d.get('notes','')))
  query.trace_add('write',refresh);refresh()
  def selected():
   if tree.selection(): self.edit(k,tree.selection()[0])
  tree.bind('<Double-1>',lambda e:selected()); ttk.Button(bar,text='Öppna',command=selected).pack(side='left',padx=6)
 def edit(self,k,id=None):
  with core.db() as c:d=core.get(c,self.uid,k,id) if id else {}
  self.reset((id or 'Ny registrering')+' · '+core.SCHEMA[k][0]); outer=ttk.Frame(self.main);outer.pack(fill='both',expand=True); canvas=tk.Canvas(outer,highlightthickness=0); scroll=ttk.Scrollbar(outer,orient='vertical',command=canvas.yview);scroll.pack(side='right',fill='y');canvas.pack(side='left',fill='both',expand=True);canvas.configure(yscrollcommand=scroll.set); form=ttk.Frame(canvas); win=canvas.create_window((0,0),window=form,anchor='nw');form.bind('<Configure>',lambda e:canvas.configure(scrollregion=canvas.bbox('all')));canvas.bind('<Configure>',lambda e:canvas.itemconfigure(win,width=e.width)); fields={}
  for key,label in core.SCHEMA[k][2]:
   ttk.Label(form,text=label).pack(anchor='w',pady=(8,0)); v=tk.StringVar(value=d.get(key,'')); fields[key]=v; ttk.Entry(form,textvariable=v).pack(fill='x')
  def save():
   try:
    data={**d, **{key:v.get().strip() for key,v in fields.items()}}
    if not data['name'] and k=='fish':data['name']='Okänd variant'
    if not data['name']:raise ValueError('Namn krävs')
    with core.db() as c:
     c.execute('BEGIN IMMEDIATE'); key=id or core.nextid(c,self.uid,k); core.validate(c,self.uid,k,data,key);c.execute('INSERT OR REPLACE INTO records VALUES(?,?,?,?)',(self.uid,k,key,json.dumps(data,ensure_ascii=False)))
    self.edit(k,key)
   except Exception as e:messagebox.showerror('Spara',str(e))
  bar=ttk.Frame(self.main);bar.pack(fill='x');ttk.Button(bar,text='Spara',command=save).pack(side='left');ttk.Button(bar,text='Tillbaka',command=lambda:self.listing(k)).pack(side='left')
  if k=='fish' and id:
   ttk.Button(bar,text='Lägg till foto',command=lambda:self.photo(id)).pack(side='left');ttk.Button(bar,text='Stamtavla',command=lambda:self.pedigree(id)).pack(side='left')
   ttk.Button(bar,text='Visa foton',command=lambda:self.photos(id)).pack(side='left');ttk.Button(bar,text='Bildanalys',command=lambda:self.image_ui(id)).pack(side='left')
 def photo_new(self):
  p=filedialog.askopenfilename(filetypes=[('Bilder','*.jpg *.jpeg *.png *.webp')]);
  if not p:return
  try:
   from PIL import Image
   blob=Path(p).read_bytes()
   if len(blob)>5_000_000:raise ValueError('Max 5 MB')
   im=Image.open(io.BytesIO(blob));fmt=im.format;im.verify();mime={'JPEG':'image/jpeg','PNG':'image/png','WEBP':'image/webp'}[fmt]
   with core.db() as c:
    c.execute('BEGIN IMMEDIATE');key=core.nextid(c,self.uid,'fish');c.execute('INSERT INTO records VALUES(?,?,?,?)',(self.uid,'fish',key,json.dumps({'name':'Okänd variant'})));c.execute('INSERT INTO photos VALUES(?,?,?,?,?)',(self.uid,key,secrets.token_hex(16),mime,blob))
   self.edit('fish',key)
  except Exception as e:messagebox.showerror('Registrering',str(e))
 def photo(self,id):
  p=filedialog.askopenfilename(filetypes=[('Bilder','*.jpg *.jpeg *.png *.webp')]);
  if not p:return
  try:
   from PIL import Image
   blob=Path(p).read_bytes(); im=Image.open(io.BytesIO(blob));fmt=im.format;im.verify();mime={'JPEG':'image/jpeg','PNG':'image/png','WEBP':'image/webp'}[fmt]
   if len(blob)>5_000_000:raise ValueError('Max 5 MB')
   with core.db() as c:c.execute('INSERT INTO photos VALUES(?,?,?,?,?)',(self.uid,id,secrets.token_hex(16),mime,blob))
   self.photos(id)
  except Exception as e:messagebox.showerror('Bild',str(e))
 def photos(self,id):
  from PIL import Image,ImageTk
  w=tk.Toplevel(self);w.title('Fotografier '+id); images=[];w.images=images
  with core.db() as c: rows=list(c.execute('SELECT blob FROM photos WHERE uid=? AND fish=?',(self.uid,id)))
  if not rows:ttk.Label(w,text='Inga fotografier').pack()
  for i,r in enumerate(rows):
   im=Image.open(io.BytesIO(r[0]));im.thumbnail((220,180));img=ImageTk.PhotoImage(im);images.append(img);ttk.Label(w,image=img).grid(row=i//3,column=i%3,padx=5,pady=5)
 def image_ui(self,id):
  from visual import measure,ancestry_scenarios
  from PIL import Image,ImageTk
  self.reset('Bildanalys · '+id)
  ttk.Label(self.main,text='Vit bakgrund, hel fisk i sidovy. Mäter färgpixlar och motivets proportioner, inte gener eller metallskimmer.',wraplength=650).pack(anchor='w')
  with core.db() as c:
   rows=list(c.execute('SELECT id,blob FROM photos WHERE uid=? AND fish=?',(self.uid,id))); d=core.get(c,self.uid,'fish',id); prior,reason=ancestry_scenarios(c,self.uid,id)
  ttk.Label(self.main,text='Härkomst: '+d.get('sire_strain','')+' × '+d.get('dam_strain','')+'\n'+reason+' '+str(prior),wraplength=650).pack(anchor='w')
  if not rows:ttk.Button(self.main,text='Lägg till foto',command=lambda:self.photo(id)).pack();return
  choice=tk.StringVar(value=rows[0][0]);ttk.Combobox(self.main,textvariable=choice,values=[r[0] for r in rows],state='readonly').pack(fill='x')
  preview=ttk.Label(self.main);preview.pack(); result=ttk.Label(self.main);result.pack(anchor='w'); current={}
  def analyze():
   current.clear(); result.config(text=''); blob=dict((r[0],r[1]) for r in rows)[choice.get()]
   im=Image.open(io.BytesIO(blob));im.thumbnail((330,220));preview.image=ImageTk.PhotoImage(im);preview.config(image=preview.image)
   try:
    current.update(measure(blob));current['photo_id']=choice.get(); result.config(text='Mörka pixlar: {:.1%} · blå pixlar: {:.1%}\nMotivets höjd/bredd: {:.2f}'.format(current['dark_fraction'],current['blue_fraction'],current['height_width']))
   except ValueError as e:result.config(text=str(e))
  def save():
   if not current or current['photo_id']!=choice.get():return
   with core.db() as c:
    d=core.get(c,self.uid,'fish',id);d.setdefault('image_measurements',{})[choice.get()]=dict(current);c.execute('UPDATE records SET data=? WHERE uid=? AND kind=? AND id=?',(json.dumps(d,ensure_ascii=False),self.uid,'fish',id))
   messagebox.showinfo('Bildanalys','Mätning sparad separat från genetiska bevis.')
  def eye():
   from phenotype_preview import eye_region
   from PIL import ImageOps
   try:
    blob=dict((r[0],r[1]) for r in rows)[choice.get()]; selected=choice.get();im=ImageOps.exif_transpose(Image.open(io.BytesIO(blob))).convert('RGB');im.thumbnail((700,450));w=tk.Toplevel(self);w.title('Markera ögat – dra en rektangel');c=tk.Canvas(w,width=im.width,height=im.height);c.pack();c.image=ImageTk.PhotoImage(im);c.create_image(0,0,image=c.image,anchor='nw');start=[]
    def down(e):start[:]=[e.x,e.y]
    def up(e):
     if not start:return
     x1,x2=sorted([start[0],e.x]);y1,y2=sorted([start[1],e.y]);bounds=(max(0,x1)/im.width,max(0,y1)/im.height,min(im.width,x2)/im.width,min(im.height,y2)/im.height)
     try:
      value=eye_region(blob,bounds)
      if messagebox.askyesno('Ögonmätning',f'Röda pixlar i markerat område: {value:.1%}. Inte en genotyp. Spara observation?',parent=w):
       with core.db() as db:
        d=core.get(db,self.uid,'fish',id);d.setdefault('eye_measurements',{})[selected]={'bounds':bounds,'red_fraction':value};db.execute('UPDATE records SET data=? WHERE uid=? AND kind=? AND id=?',(json.dumps(d,ensure_ascii=False),self.uid,'fish',id))
       w.destroy()
     except ValueError as ex:messagebox.showerror('Ögonmätning',str(ex),parent=w)
    c.bind('<ButtonPress-1>',down);c.bind('<ButtonRelease-1>',up)
   except Exception as e:messagebox.showerror('Ögonmätning',str(e))
  ttk.Button(self.main,text='Analysera foto',command=analyze).pack(anchor='w');ttk.Button(self.main,text='Spara mätning',command=save).pack(anchor='w');ttk.Button(self.main,text='Markera och mät ögonfärg',command=eye).pack(anchor='w');analyze()
 def visual_ui(self):
  from visual import ancestry_scenarios,mixed_forecast
  from PIL import Image,ImageTk
  self.reset('Visuell korsningssimulator')
  ttk.Label(self.main,text='Dark-lokus: illustrativa fenotyper för + och D. Andra anlag kan ändra utseendet.',wraplength=650).pack(anchor='w')
  with core.db() as c:fish=core.records(c,self.uid,'fish')
  choices=['']+[k+' | '+d.get('name','') for k,d in fish]; fields=[]
  for label in ('Förälder A','Förälder B'):
   ttk.Label(self.main,text=label).pack(anchor='w'); f=tk.StringVar();ttk.Combobox(self.main,textvariable=f,values=choices,state='readonly').pack(fill='x'); g=tk.StringVar();ttk.Label(self.main,text='Alternativt scenario (t.ex. D/+; lämna tomt för register)').pack(anchor='w');ttk.Entry(self.main,textvariable=g).pack(fill='x');fields.append((f,g))
  result=ttk.Frame(self.main);result.pack(fill='both',expand=True);status=ttk.Label(self.main,wraplength=650);status.pack(anchor='w')
  def calc():
   for w in result.winfo_children():w.destroy()
   try:
    from catalog import validate_genotype
    ds=[];reasons=[]
    with core.db() as c:
     for f,g in fields:
      if g.get().strip():ds.append({validate_genotype('Dark',g.get().strip()):1});reasons.append('Manuellt scenario')
      else:
       d,r=ancestry_scenarios(c,self.uid,f.get().split(' | ')[0]);ds.append(d);reasons.append(r)
    if fields[0][0].get() and fields[0][0].get()==fields[1][0].get():raise ValueError('Välj olika individer')
    rows=mixed_forecast(*ds);status.config(text=' / '.join(reasons)+' | Oberoende osäkerhet mellan föräldrar; lika överlevnad. Bilder är exempel, inte exakta prognoser.')
    for i,(g,p,n,img) in enumerate(rows):
     cell=ttk.Frame(result,padding=5);cell.grid(row=i//3,column=i%3,sticky='n');ttk.Label(cell,text=f'{n} · {p:.1%}\n{g}',wraplength=175).pack()
     if img:
      asset=Path(__file__).parent/'assets'/(img+'.jpg');im=Image.open(asset);im.thumbnail((175,145));label=ttk.Label(cell);label.image=ImageTk.PhotoImage(im);label.config(image=label.image);label.pack()
   except Exception as e:status.config(text=str(e))
  ttk.Button(self.main,text='Simulera',command=calc).pack(anchor='w',pady=6)
 def multi_visual_ui(self):
  from advanced_visual import simulate,at_least_one
  from future import parse_profile,forecast
  self.reset('Visuell genetik · flera lokus')
  ttk.Label(self.main,text='Villkorad prognos: oberoende lokus, lika överlevnad. Stamnamn är inte genotypbevis.',wraplength=650).pack(anchor='w')
  fields=[]
  for label,default in [('Förälder A','Dark=D/+, Philippine Blue=+/pb'),('Förälder B','Dark=D/+, Philippine Blue=+/pb'),('Mål (valfritt)','Dark=D/D, Philippine Blue=pb/pb'),('Kullstorlek','50')]:
   ttk.Label(self.main,text=label).pack(anchor='w');e=ttk.Entry(self.main);e.insert(0,default);e.pack(fill='x');fields.append(e)
  status=ttk.Label(self.main,wraplength=650);status.pack(anchor='w')
  tree=ttk.Treeview(self.main,columns=('profile','prob','name','score'),show='headings',height=10)
  for k,t,w in [('profile','Genotyp',245),('prob','Sannolikhet',90),('name','Egenskaper (hypotes)',240),('score','Målmatch',85)]:tree.heading(k,text=t);tree.column(k,width=w)
  tree.pack(fill='both',expand=True)
  from phenotype_preview import preview
  from PIL import ImageTk
  picture=ttk.Label(self.main);picture.pack(anchor='w')
  hint=ttk.Label(self.main,text='Välj en rad för illustration. Blå färg är en schematisk överlagring, inte verifierad fenotyp.',wraplength=650);hint.pack(anchor='w')
  profiles={}
  def show(event=None):
   sel=tree.selection(); im=preview(profiles[sel[0]]) if sel and sel[0] in profiles else None
   if im is None:picture.config(image='',text='Ingen bildmodell för denna kombination');picture.image=None;return
   im.thumbnail((210,150));picture.image=ImageTk.PhotoImage(im);picture.config(image=picture.image,text='')
  tree.bind('<<TreeviewSelect>>',show)
  def calc():
   tree.delete(*tree.get_children());profiles.clear();show()
   try:
    a,b=[parse_profile(e.get()) for e in fields[:2]];t=parse_profile(fields[2].get()) if fields[2].get().strip() else {};n=int(fields[3].get());rows=simulate(a,b,t)
    for g,p,label,asset,score in rows:
     key=tree.insert('', 'end',values=(', '.join(k+'='+v for k,v in g.items()),f'{p:.2%}',label,'—' if score is None else f'{score:.0%}'));profiles[key]=g
    if t:
     f=forecast(a,b,t);status.config(text=' · '.join(k+f': {v:.2%}' for k,v in f.items())+f' | Minst en målgenotyp i F1-kull: {at_least_one(f["F1"],n):.2%}')
    else:status.config(text=f'{len(rows)} genotypkombinationer')
   except Exception as e:status.config(text=str(e))
  ttk.Button(self.main,text='Beräkna',command=calc).pack(anchor='w');calc()
 def pedigree(self,id):
  w=tk.Toplevel(self);w.title('Stamtavla');tree=ttk.Treeview(w);tree.pack(fill='both',expand=True)
  with core.db() as c:
   def add(x,parent,depth):
    if not x or depth>12:return
    d=core.get(c,self.uid,'fish',x) or {}; node=tree.insert(parent,'end',text=x+' '+d.get('name',''),open=True)
    for key in ('sire','dam'):add(d.get(key),node,depth+1)
   add(id,'',0)
 def simulator(self):
  self.reset('Korsningssimulator');ttk.Label(self.main,text='Ett lokus · ange två alleler per förälder, t.ex. D/+').pack(anchor='w');a=ttk.Entry(self.main);b=ttk.Entry(self.main);a.insert(0,'D/+');b.insert(0,'D/+');a.pack(fill='x',pady=6);b.pack(fill='x',pady=6);r=ttk.Label(self.main,text='');r.pack(anchor='w',pady=12)
  def calc():
   try:r.config(text='\n'.join(f'{k}: {v:.1%}' for k,v in cross(a.get(),b.get()).items()))
   except ValueError as e:r.config(text=str(e))
  ttk.Button(self.main,text='Beräkna',command=calc).pack(anchor='w')
 def test_cross_ui(self):
  self.reset('Genetisk testkorsning'); ttk.Label(self.main,text='En allel, enkel dominans/recessivitet. Lika priorer; 1 % klassificeringsfel.').pack(anchor='w')
  fields=[]
  for label,default in [('Muterad allel','a'),('Testarens genotyp','a/a'),('Antal med egenskap','12'),('Antal utan egenskap','12')]:
   ttk.Label(self.main,text=label).pack(anchor='w'); e=ttk.Entry(self.main);e.insert(0,default);e.pack(fill='x');fields.append(e)
  mode=tk.StringVar(value='recessiv');ttk.Combobox(self.main,textvariable=mode,values=['recessiv','dominant'],state='readonly').pack(anchor='w',pady=8)
  result=ttk.Label(self.main,text='');result.pack(anchor='w',pady=10)
  def calc():
   try:
    a,t,x,y=[e.get() for e in fields]; d=test_cross(a,t,int(x),int(y),mode.get()=='recessiv');result.config(text='\n'.join(f'{k}: {v:.2%}' for k,v in sorted(d.items(),key=lambda z:-z[1])))
   except ValueError as e:result.config(text=str(e))
  ttk.Button(self.main,text='Beräkna hypoteser',command=calc).pack(anchor='w')
  ttk.Label(self.main,text='Villkorad sannolikhet, inte genetiskt bevis. Registrera resultat och kull-ID i genetiska profiler.',wraplength=600).pack(anchor='w',pady=12)
 def mapping_ui(self):
  from evidence_engine import save_observation
  self.reset('Genetisk kartläggning från kullar')
  ttk.Label(self.main,text='Testarens genotyp måste vara känd. Samma kull ersätts vid rättelse.',wraplength=650).pack(anchor='w')
  with core.db() as c:
   fish=[k for k,d in core.records(c,self.uid,'fish')]; broods=[k for k,d in core.records(c,self.uid,'broods')]
  fields=[]
  for label,default,choices in [('Fisk-ID','',fish),('Kull-ID','',broods),('Lokus','Albino',None),('Muterad allel','a',None),('Testarens genotyp','a/a',None),('Med egenskap','0',None),('Utan egenskap','0',None),('Modell','recessiv',['recessiv','dominant'])]:
   ttk.Label(self.main,text=label).pack(anchor='w'); v=tk.StringVar(value=default);fields.append(v)
   w=ttk.Combobox(self.main,textvariable=v,values=choices,state='readonly') if choices is not None else ttk.Entry(self.main,textvariable=v);w.pack(fill='x')
  result=ttk.Label(self.main,wraplength=650);result.pack(anchor='w',pady=8)
  def calc():
   try:
    f,b,l,a,t,x,y,m=[v.get() for v in fields]
    with core.db() as c: r=save_observation(c,self.uid,f,l,a,b,t,int(x),int(y),m=='recessiv')
    result.config(text='Sparad hypotes: '+', '.join(f'{k}: {v:.2%}' for k,v in r.items()))
   except Exception as e:messagebox.showerror('Kartläggning',str(e))
  ttk.Button(self.main,text='Analysera och spara',command=calc).pack(anchor='w')
 def generation_ui(self):
  self.reset('Generationshjälp');ttk.Label(self.main,text='Kontrollera gemensamt ursprung och linje innan beteckningen används.').pack(anchor='w')
  mode=tk.StringVar(value='new');ttk.Combobox(self.main,textvariable=mode,values=['new','filial','backcross','unknown'],state='readonly').pack(anchor='w')
  ttk.Label(self.main,text='new = ny definierad korsning; filial = samma linje; backcross = återkorsning till verifierad föräldralinje').pack(anchor='w')
  a=ttk.Entry(self.main);b=ttk.Entry(self.main)
  for label,e in [('Generation A',a),('Generation B',b)]:ttk.Label(self.main,text=label).pack(anchor='w');e.pack(fill='x')
  result=ttk.Label(self.main);result.pack(anchor='w',pady=12)
  def calc():
   try:result.config(text=generation(mode.get(),a.get(),b.get()))
   except ValueError as e:result.config(text=str(e))
  ttk.Button(self.main,text='Föreslå beteckning',command=calc).pack(anchor='w')
 def advice(self):
  self.reset('Preliminärt avelsråd');ttk.Label(self.main,text='Gemensamma kända förfäder – inte inavelsgrad eller genetisk målmatchning.').pack(anchor='w');tree=ttk.Treeview(self.main,columns=('a','b','n'),show='headings');tree.pack(fill='both',expand=True)
  for k,t in [('a','Fisk A'),('b','Fisk B'),('n','Gemensamma individer')]:tree.heading(k,text=t)
  with core.db() as c:
   fs=core.records(c,self.uid,'fish'); ds=dict(fs)
   def anc(x,seen):
    if not x or x in seen:return
    seen.add(x);d=ds.get(x,{})
    for k in ('sire','dam'):anc(d.get(k),seen)
   sets={}
   for x,_ in fs:sets[x]=set();anc(x,sets[x])
   pairs=sorted((len(sets[a]&sets[b]),a,b) for i,(a,_) in enumerate(fs) for b,_ in fs[i+1:])
   for n,a,b in pairs[:100]:tree.insert('','end',values=(a+' '+ds[a]['name'],b+' '+ds[b]['name'],n))
 def target_ui(self):
  from planning import rank
  self.reset('Målstyrda korsningar')
  ttk.Label(self.main,text='Ange målgenotyper som lokus=allel/allel, separerade med komma.').pack(anchor='w')
  target=ttk.Entry(self.main);target.pack(fill='x');target.insert(0,'Dark=D/D')
  tree=ttk.Treeview(self.main,columns=('a','b','p','f','info'),show='headings');tree.pack(fill='both',expand=True)
  for k,t in [('a','Fisk A'),('b','Fisk B'),('p','Målsannolikhet'),('f','Inavelsgrad*'),('info','Osäkerhet')]:tree.heading(k,text=t);tree.column(k,width=135)
  def calc():
   try:
    targets=dict(x.strip().split('=',1) for x in target.get().split(','));
    if any(not k or len(v.split('/'))!=2 or not all(v.split('/')) for k,v in targets.items()):raise ValueError('Ogiltigt mål')
    with core.db() as c:
     fish=dict(core.records(c,self.uid,'fish'));profiles={}; conflicts=set()
     for _,d in core.records(c,self.uid,'evidence'):
      if d.get('confidence','').strip().lower() not in ('bekräftad','confirmed'):continue
      a,k,v=d.get('name'),d.get('locus'),d.get('genotype','')
      if a not in fish or len(v.split('/'))!=2:continue
      v='/'.join(sorted(v.split('/')));old=profiles.setdefault(a,{}).get(k)
      if old and old!=v:conflicts.add((a,k))
      profiles[a][k]=v
     for a,k in conflicts:profiles[a].pop(k,None)
    rows=rank(fish,profiles,targets);tree.delete(*tree.get_children())
    for a,b,p,f,missing,sex in rows[:500]:tree.insert('','end',values=(a,b,'Okänd' if p is None else f'{p:.2%}',f'{f:.2%}',', '.join(missing)+(' / kön okänt' if sex else '')))
   except Exception as e:messagebox.showerror('Avelsmål',str(e))
  ttk.Button(self.main,text='Rangordna par',command=calc).pack(anchor='w')
  ttk.Label(self.main,text='* Antager obesläktade grundare; ofullständig stamtavla kan underskatta inavel. Oberoende lokus, endast bekräftade profiler. Kontrollera hälsa och fertilitet.',wraplength=650).pack(anchor='w')
 def catalog_ui(self):
  from catalog import LOCI
  self.reset('Genetiskt referensbibliotek')
  ttk.Label(self.main,text='Referensmodeller – inte DNA-verifierade individprofiler.').pack(anchor='w')
  tree=ttk.Treeview(self.main,columns=('locus','alleles','note'),show='headings');tree.pack(fill='both',expand=True)
  for k,t in [('locus','Lokus'),('alleles','Alleler'),('note','Modell')]:tree.heading(k,text=t)
  for k,(a,n,u) in LOCI.items():tree.insert('','end',iid=k,values=(k,', '.join(a),n))
  source=tk.StringVar();ttk.Entry(self.main,textvariable=source,state='readonly').pack(fill='x')
  tree.bind('<<TreeviewSelect>>',lambda e:source.set(LOCI[tree.selection()[0]][2]) if tree.selection() else None)
 def future_ui(self):
  from future import forecast,parse_profile
  self.reset('Planering över två generationer')
  fields=[]
  for label,value in [('Förälder A','Dark=D/D, Philippine Blue=+/+'),('Förälder B','Dark=+/+, Philippine Blue=pb/pb'),('Mål','Dark=D/D, Philippine Blue=pb/pb')]:
   ttk.Label(self.main,text=label).pack(anchor='w');e=ttk.Entry(self.main);e.insert(0,value);e.pack(fill='x');fields.append(e)
  result=ttk.Label(self.main);result.pack(anchor='w',pady=12)
  def calc():
   try:result.config(text='\n'.join(f'{k}: {v:.2%}' for k,v in forecast(*(parse_profile(e.get()) for e in fields)).items()))
   except ValueError as e:result.config(text=str(e))
  ttk.Button(self.main,text='Jämför vägar',command=calc).pack(anchor='w')
  ttk.Label(self.main,text='F2: slumpmässiga F1-syskon. BC1: F1 tillbaka till A eller B. Oberoende lokus och lika överlevnad. Inte ett råd att använda närbesläktade fiskar; kontrollera inavel och hälsa.',wraplength=650).pack(anchor='w',pady=12)
 def pathway_ui(self):
  from pathway import plan
  from future import parse_profile
  self.reset('Urvalsplan över flera generationer')
  ttk.Label(self.main,text='Villkorad genotypsimulering av syskonurval; ingen rekommendation att genomföra inavel. Kön, hälsa och överlevnad ingår inte. Begränsad sökning, inte globalt optimum.',wraplength=730).pack(anchor='w')
  fields=[]
  for label,value in [('Förälder A','Dark=D/D, Philippine Blue=+/+'),('Förälder B','Dark=+/+, Philippine Blue=pb/pb'),('Mål','Dark=D/D, Philippine Blue=pb/pb'),('Generationer (1–10)','5'),('Bedömda avkommor per kull','100')]:
   ttk.Label(self.main,text=label).pack(anchor='w');e=ttk.Entry(self.main);e.insert(0,value);e.pack(fill='x');fields.append(e)
  out=tk.Text(self.main,wrap='word');out.pack(fill='both',expand=True)
  def run():
   try:
    rows=plan(*(parse_profile(e.get()) for e in fields[:3]),int(fields[3].get()),int(fields[4].get()))
    lines=[]
    for r in rows:
     lines.append(f"F{r['generation']}: mål per avkomma {r['per_offspring']:.2%}; villkorad urvalsväg (nedre gräns) {r['path_probability']:.2%}")
     for h in r['history']:lines.append(f"  Urval F{h['generation']}: {h['selected']} — minst {h['selection_lower_bound']:.2%}")
     lines.append('')
    out.delete('1.0','end');out.insert('end','\n'.join(lines))
   except Exception as e:messagebox.showerror('Urvalsplan',str(e))
  ttk.Button(self.main,text='Beräkna urvalsvägar',command=run).pack(anchor='w')
 def export_account(self):
  from release_tools import export_account,atomic_json
  p=filedialog.asksaveasfilename(defaultextension='.json',filetypes=[('JSON','*.json')]);
  if not p:return
  try:
   with core.db() as c:data=export_account(c,self.uid)
   atomic_json(p,data);messagebox.showinfo('Export','Dina uppgifter och foton är exporterade. Inga lösenord ingår.')
  except Exception as e:messagebox.showerror('Export',str(e))
 def restore_backup(self):
  if self.demo_tmp is not None: messagebox.showinfo('Demo','Återställning är avstängd i demoläget.'); return
  from release_tools import restore
  if not messagebox.askyesno('Återställ','Ersätter samtliga lokala konton och data. En kopia av nuvarande databas sparas först. Fortsätt?'):return
  p=filedialog.askopenfilename(filetypes=[('SQLite','*.sqlite3')]);
  if not p:return
  try:
   restore(p,core.DB);self.login();messagebox.showinfo('Återställ','Databasen återställd. Logga in igen.')
  except Exception as e:messagebox.showerror('Återställ',str(e))
 def backup(self):
  if not messagebox.askyesno('Säkerhetskopia','Kopian innehåller samtliga lokala konton och bilder. Fortsätt?'):return
  p=filedialog.asksaveasfilename(defaultextension='.sqlite3',filetypes=[('SQLite','*.sqlite3')]);
  if not p:return
  try:
   if Path(p).resolve()==core.DB.resolve():raise ValueError('Välj en annan fil än den aktiva databasen.')
   from release_tools import snapshot
   snapshot(core.DB,p)
   messagebox.showinfo('Säkerhetskopia','Kopia sparad.')
  except Exception as e:messagebox.showerror('Säkerhetskopia',str(e))
if __name__=='__main__':
 if '--smoke-test' in sys.argv:
  import tempfile
  from demo import seed
  with tempfile.TemporaryDirectory() as d:
   core.DB=Path(d)/'smoke.sqlite3';seed(core.DB);win=Desktop();win.update();win.uid=1;win.home();win.update();win.multi_visual_ui();win.update();win.destroy()
  marker=Path(sys.argv[sys.argv.index('--smoke-test')+1]);marker.write_text('OK',encoding='utf-8')
 else: Desktop().mainloop()
