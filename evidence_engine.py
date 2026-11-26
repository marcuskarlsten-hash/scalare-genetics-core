"""Persist independent test-cross observations and recompute posterior profiles."""
from genetics import cross, posterior
import json

def infer(allele, observations):
    if not allele or allele=='+' or '/' in allele: raise ValueError('Ogiltig allel')
    hypotheses=[]; counts={}
    for i,o in enumerate(observations):
        for k in ('affected','normal'):
            if type(o[k]) is not int or o[k]<0: raise ValueError('Ogiltigt antal')
            counts[f'{i}:{k}']=o[k]
    for g in ('+/+',f'+/{allele}',f'{allele}/{allele}'):
        dist={}
        for i,o in enumerate(observations):
            children=cross(g,o['tester'])
            if any(set(k.split('/'))-{'+' ,allele} for k in children): raise ValueError('Testarens alleler matchar inte modellen')
            p=sum(v for k,v in children.items() if (k.split('/').count(allele)==2 if o['recessive'] else allele in k.split('/')))
            p=.01+.98*p
            dist[f'{i}:affected']=p;dist[f'{i}:normal']=1-p
        hypotheses.append((g,1/3,dist))
    return posterior(hypotheses,counts)

def save_observation(c,uid,fish,locus,allele,brood,tester,affected,normal,recessive):
    import app
    if not locus.strip() or not app.get(c,uid,'fish',fish): raise ValueError('Ange registrerad fisk och lokus')
    b=app.get(c,uid,'broods',brood)
    if not b or fish not in (b.get('sire'),b.get('dam')): raise ValueError('Fisken måste vara förälder i registrerad kull')
    if not b.get('sire') or not b.get('dam'): raise ValueError('Båda föräldrar måste registreras')
    if affected+normal<=0: raise ValueError('Registrera minst en avkomma')
    c.execute('CREATE TABLE IF NOT EXISTS cross_observations(uid INTEGER, fish TEXT, locus TEXT, brood TEXT, data TEXT, PRIMARY KEY(uid,fish,locus,brood))')
    o=dict(allele=allele,tester=tester,affected=affected,normal=normal,recessive=recessive)
    c.execute('INSERT INTO cross_observations VALUES(?,?,?,?,?) ON CONFLICT(uid,fish,locus,brood) DO UPDATE SET data=excluded.data',(uid,fish,locus,brood,json.dumps(o)))
    obs=[json.loads(r[0]) for r in c.execute('SELECT data FROM cross_observations WHERE uid=? AND fish=? AND locus=?',(uid,fish,locus))]
    if any(x['allele']!=allele or x['recessive']!=recessive for x in obs):raise ValueError('Oförenliga modeller för samma lokus')
    result=infer(allele,obs)
    key=next((k for k,d in app.records(c,uid,'evidence') if d.get('name')==fish and d.get('locus')==locus and d.get('source')=='Automatisk testkorsningsanalys'),None) or app.nextid(c,uid,'evidence')
    best=max(result,key=result.get)
    d=dict(name=fish,locus=locus,genotype=best,confidence='Hypotes',source='Automatisk testkorsningsanalys',notes=json.dumps(result,ensure_ascii=False)+f' | {len(obs)} kullar; lika priorer, 1 % klassificeringsfel; antaget känd testargenotyp.')
    c.execute('INSERT OR REPLACE INTO records VALUES(?,?,?,?)',(uid,'evidence',key,json.dumps(d,ensure_ascii=False)))
    return result
