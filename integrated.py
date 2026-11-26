"""Conservative profile resolution and planning; no genotype inferred from strain names."""
from intelligence import normalize, ancestry
from planning import kinship
from genetics import cross
from itertools import combinations
from math import prod, log1p, expm1
import json

def profiles(fish, evidence, loci):
    index={}
    for key,d in evidence:
        index.setdefault((d.get('name'),d.get('locus')),[]).append((key,d))
    cache={}
    def resolve(id,locus,stack=()):
        key=(id,locus)
        if key in cache:return cache[key]
        if id not in fish or id in stack:return {},'Saknad eller cirkulär härkomst'
        confirmed=set(); inferred=[]; invalid=False
        for eid,d in index.get(key,[]):
            status=d.get('confidence','').strip().casefold()
            try:
                if status in ('bekräftad','confirmed'):
                    confirmed.update(normalize(locus,{d['genotype']:1}))
                elif d.get('source')=='Automatisk testkorsningsanalys':
                    inferred.append(normalize(locus,json.loads(d['notes'].split(' | ',1)[0])))
            except (ValueError,TypeError,KeyError,AttributeError):invalid=True
        if invalid or len(confirmed)>1 or len(inferred)>1:r=({},'Motstridiga eller ogiltiga profiluppgifter')
        elif confirmed:r=({next(iter(confirmed)):1.},'Registrerad bekräftad genotyp')
        elif inferred:r=(inferred[0],'Villkorad testkorsningsmodell; ej DNA-verifierad')
        else:
            d=fish[id]; a,_=resolve(d.get('sire'),locus,stack+(id,)); b,_=resolve(d.get('dam'),locus,stack+(id,))
            # Avoid compounding uncertain pedigrees: ancestry only from point profiles.
            if len(a)==len(b)==1 and next(iter(a.values()))==next(iter(b.values()))==1:
                r=(ancestry(locus,a,b),'Härkomstmodell från föräldraprofiler')
            else:r=({},'Otillräckligt underlag')
        cache[key]=r;return r
    return {id:{l:resolve(id,l) for l in loci} for id in fish}

def chance(p,n):
    if not isinstance(n,int) or n<1 or not 0<=p<=1:raise ValueError('Ogiltig kullstorlek eller sannolikhet')
    return 1. if p==1 else -expm1(n*log1p(-p))

def proposals(fish, resolved, targets, n, max_f):
    if not targets or n<1 or not 0<=max_f<=1:raise ValueError('Ogiltigt mål eller gräns')
    targets={l:next(iter(normalize(l,{g:1}))) for l,g in targets.items()}
    phi=kinship(fish);out=[]
    for a,b in combinations(fish,2):
        sex=lambda x:{'hane':'m','male':'m','hona':'f','female':'f'}.get(fish[x].get('sex','').strip().lower(),'?')
        if sex(a)==sex(b)!='?':continue
        f=phi(a,b)
        if f>max_f:continue
        ps=[]; missing=[]
        for l,g in targets.items():
            x=resolved[a][l][0];y=resolved[b][l][0]
            if not x or not y:missing.append(l);continue
            ps.append(sum(p*q*cross(u,v).get(g,0) for u,p in x.items() for v,q in y.items()))
        p=None if missing else prod(ps)
        # Shared unknown parent genotypes correlate siblings; do not use iid formula there.
        fixed=not missing and all(len(resolved[i][l][0])==1 for i in (a,b) for l in targets)
        if f>0 and not fixed:
            p=None; missing.append('Beroende genotyper i släktträd')
        q=chance(p,n) if fixed else None
        if p is not None and not fixed and len(targets)==1 and f==0:
            from release_tools import brood_probability
            l,g=next(iter(targets.items())); _,q=brood_probability(l,resolved[a][l][0],resolved[b][l][0],g,n)
        out.append(dict(a=a,b=b,p=p,at_least_one=q,f=f,missing=missing,sex_unknown='?' in (sex(a),sex(b))))
    return sorted(out,key=lambda r:(r['p'] is None,-(r['p'] or 0),r['f'],r['a'],r['b']))

def allocate(rows, tanks):
    """Greedy disjoint pairs, one explicitly available tank each; not global optimum."""
    used=set();result=[]
    for r in rows:
        if len(result)>=len(tanks):break
        if r['p'] is None or r['p']<=0 or r['sex_unknown'] or {r['a'],r['b']}&used:continue
        result.append({**r,'tank':tanks[len(result)]});used.update((r['a'],r['b']))
    return result
