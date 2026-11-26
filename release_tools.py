"""Local backup, portable account export and robust probability calculations."""
import base64, json, sqlite3, os, tempfile, math
from contextlib import closing
from pathlib import Path
from itertools import product
from genetics import cross
from intelligence import normalize

def export_account(c,uid):
    import app
    return {'format':'scalare-account-1','records':{k:dict(app.records(c,uid,k)) for k in app.SCHEMA},'photos':[{'fish':r['fish'],'id':r['id'],'mime':r['mime'],'base64':base64.b64encode(r['blob']).decode('ascii')} for r in c.execute('SELECT * FROM photos WHERE uid=?',(uid,))]}

def atomic_json(path,data):
    path=Path(path); fd,tmp=tempfile.mkstemp(dir=path.parent)
    try:
        with os.fdopen(fd,'w',encoding='utf-8') as f:json.dump(data,f,ensure_ascii=False,indent=2)
        os.replace(tmp,path)
    finally:
        if os.path.exists(tmp):os.unlink(tmp)

def snapshot(source,destination):
    source,destination=Path(source),Path(destination)
    if source.resolve()==destination.resolve():raise ValueError('Välj en annan fil än databasen.')
    if not source.is_file():raise ValueError('Databas saknas.')
    fd,tmp=tempfile.mkstemp(dir=destination.parent);os.close(fd)
    try:
        with closing(sqlite3.connect(source)) as s, s,closing(sqlite3.connect(tmp)) as d, d:
            s.backup(d)
            if d.execute('PRAGMA integrity_check').fetchone()[0]!='ok':raise ValueError('Databaskontroll misslyckades.')
        os.replace(tmp,destination)
    finally:
        if os.path.exists(tmp):os.unlink(tmp)

def restore(source,destination):
    source=Path(source);destination=Path(destination)
    if not source.is_file() or source.resolve()==destination.resolve():raise ValueError('Ogiltig säkerhetskopia.')
    with closing(sqlite3.connect(source.resolve().as_uri()+'?mode=ro',uri=True)) as c, c:
        tables={r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        if not {'users','sessions','records','photos'}<=tables or c.execute('PRAGMA integrity_check').fetchone()[0]!='ok':raise ValueError('Inte en giltig Scalare-databas.')
        for table,cols in {'users':{'id','name','salt','pw'},'sessions':{'token','uid'},'records':{'uid','kind','id','data'},'photos':{'uid','fish','id','mime','blob'}}.items():
            if not cols<={r[1] for r in c.execute('PRAGMA table_info('+table+')')}:raise ValueError('Fel databasformat.')
    import uuid
    snapshot(destination,destination.with_name('before-restore-'+uuid.uuid4().hex+'.sqlite3'))
    snapshot(source,destination)

def brood_probability(locus,a,b,target,n):
    """Integrate shared uncertain parental genotypes, not independent marginal siblings."""
    if not isinstance(n,int) or n<1:raise ValueError('Ogiltig kullstorlek')
    a=normalize(locus,a); b=normalize(locus,b);target=next(iter(normalize(locus,{target:1})))
    mean=atleast=0.
    for (x,w),(y,v) in product(a.items(),b.items()):
        p=cross(x,y).get(target,0.);mean+=w*v*p;atleast+=w*v*(1. if p==1 else -math.expm1(n*math.log1p(-p)))
    return mean,atleast
