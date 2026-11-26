"""Pedigree kinship and explicit genotype-target planning."""
from functools import lru_cache
from genetics import cross

def kinship(fish):
    # Validate pedigree before recursive calculations.
    done=set(); active=set()
    def visit(x):
        if not x or x not in fish or x in done:return
        if x in active:raise ValueError('Cirkulär stamtavla: '+x)
        active.add(x)
        d=fish[x]
        for k in ('sire','dam'):visit(d.get(k))
        active.remove(x);done.add(x)
    for x in fish:visit(x)
    @lru_cache(None)
    def depth(x):
        if not x or x not in fish:return -1
        d=fish[x];return 1+max(depth(d.get('sire')),depth(d.get('dam')))
    @lru_cache(None)
    def phi(a,b):
        if not a or not b or a not in fish or b not in fish:return 0.
        if a==b:
            d=fish[a];return (1+phi(d.get('sire'),d.get('dam')))/2
        if (depth(a),a)<(depth(b),b):return phi(b,a)
        d=fish[a];return (phi(d.get('sire'),b)+phi(d.get('dam'),b))/2
    return phi

def target_probability(a,b,targets):
    p=1.; missing=[]
    for locus,target in targets.items():
        if locus not in a or locus not in b:missing.append(locus);continue
        p*=cross(a[locus],b[locus]).get('/'.join(sorted(target.split('/'))),0.)
    return (None if missing else p),missing

def rank(fish,profiles,targets):
    phi=kinship(fish);out=[]
    for i,a in enumerate(fish):
        for b in list(fish)[i+1:]:
            sexes=[fish[x].get('sex','').lower().strip() for x in (a,b)]
            sexes=[{'hane':'m','male':'m','hona':'f','female':'f'}.get(x,'?') for x in sexes]
            if sexes[0]==sexes[1] and sexes[0]!='?':continue
            p,missing=target_probability(profiles.get(a,{}),profiles.get(b,{}),targets)
            out.append((a,b,p,phi(a,b),missing,'?' in sexes))
    return sorted(out,key=lambda r:(r[2] is None,-(r[2] or 0),r[3],r[5]))
