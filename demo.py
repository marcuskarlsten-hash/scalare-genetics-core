"""Synthetic, isolated example breeding data. Never touches the production database."""
import json, sqlite3, secrets
from pathlib import Path

def seed(path):
    with sqlite3.connect(path) as c:
        c.executescript('CREATE TABLE users(id INTEGER PRIMARY KEY,name TEXT UNIQUE,salt TEXT,pw TEXT); CREATE TABLE sessions(token TEXT PRIMARY KEY,uid INTEGER); CREATE TABLE records(uid INTEGER,kind TEXT,id TEXT,data TEXT,PRIMARY KEY(uid,kind,id)); CREATE TABLE photos(uid INTEGER,fish TEXT,id TEXT,mime TEXT,blob BLOB,PRIMARY KEY(uid,id));')
        c.execute('INSERT INTO users VALUES(1,?,?,?)',('Demo',secrets.token_hex(16),secrets.token_hex(32)))
        def put(kind,id,**data):
            c.execute('INSERT INTO records VALUES(1,?,?,?)',(kind,id,json.dumps(data,ensure_ascii=False)))
        for i in range(1,5):put('tanks',f'AK-{i:05}',name=f'Demoakvarium {i}',volume='120',available='ja' if i>2 else 'nej')
        put('groups','AG-00001',name='Black Lace – exempel',origin='Fiktiva data')
        put('goals','M-00001',name='Dubbel Dark',targets='Dark=D/D',traits='Svart pigmentering')
        put('lines','L-00001',name='Demolinje',goal='M-00001')
        for i,sex,g,img in [(1,'Hane','D/+','lace'),(2,'Hona','D/+','lace'),(3,'Okänt','D/D','black'),(4,'Okänt','+/+','silver')]:
            id=f'SC-{i:05}'
            put('fish',id,name=f'Demofisk {i} – {g}',sex=sex,group='AG-00001',tank='AK-00001' if i<3 else 'AK-00002',sire='' if i<3 else 'SC-00001',dam='' if i<3 else 'SC-00002',generation='P' if i<3 else 'F1',brood='' if i<3 else 'K-00001',notes='Fiktiv individ; illustrativ bild')
            put('evidence',f'GP-{i:05}',name=id,locus='Dark',genotype=g,confidence='Bekräftad',source='Fiktiv demogenotyp')
            c.execute('INSERT INTO photos VALUES(1,?,?,?,?)',(id,f'DEMO-{i}','image/jpeg',(Path(__file__).parent/'assets'/f'{img}.jpg').read_bytes()))
        put('broods','K-00001',name='Exempelkull',sire='SC-00001',dam='SC-00002',line='L-00001',generation='F1',count='2',traits='Illustrativa registreringar, ej verklig kull')
