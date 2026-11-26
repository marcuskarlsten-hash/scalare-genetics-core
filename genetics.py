from collections import Counter
from itertools import product

def cross(a,b):
    a,b=a.split('/'),b.split('/')
    if len(a)!=2 or len(b)!=2 or not all(a+b): raise ValueError('Ange två alleler per förälder, t.ex. D/+')
    return {k:v/4 for k,v in sorted(Counter('/'.join(sorted(x)) for x in product(a,b)).items())}

def posterior(priors, observed):
    """Hypoteser: (namn, prior, sannolikheter för observerade kategorier)."""
    from math import log,exp
    scores=[]
    for name,p,dist in priors:
        if p<0 or any(v<0 for v in observed.values()): raise ValueError('Negativ vikt eller antal')
        score=log(p) if p else float('-inf')
        for k,n in observed.items():
            if n: score+=n*log(dist[k]) if dist.get(k,0)>0 else float('-inf')
        scores.append((name,score))
    m=max((s for _,s in scores),default=float('-inf'))
    if m==float('-inf'): return {}
    z=sum(exp(s-m) for _,s in scores)
    return {n:exp(s-m)/z for n,s in scores}
