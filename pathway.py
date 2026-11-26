"""Conditional single-line planning with explicit selection and bounded search.
No prediction of actual mating success, sex ratio, relatedness or survival.
"""
from itertools import product, combinations_with_replacement
from math import prod
from catalog import validate_genotype
from genetics import cross
from integrated import chance


def plan(a,b,target,generations=5,kull=100,beam=12):
    if not target or not 1<=len(target)<=4 or not 1<=generations<=10 or not 1<=beam<=30 or not 1<=kull<=100000:
        raise ValueError('1–4 lokus, 1–10 generationer, 1–30 sökvägar, 1–100000 avkommor')
    loci=sorted(target)
    def key(d):return tuple(validate_genotype(l,d[l]) for l in loci)
    if not all(l in a and l in b for l in loci):raise ValueError('Föräldragenotyper saknas')
    A,B,T=key(a),key(b),key(target)
    def distribution(x,y):
        return [(tuple(g for g,p in row),prod(p for g,p in row)) for row in product(*(cross(i,j).items() for i,j in zip(x,y)))]
    def score(g):return sum(sum(min(x.count(z),y.count(z)) for z in set(y))/2 for x,y in zip((s.split('/') for s in g),(s.split('/') for s in T)))/len(T)
    # Path probability is a product of conditional selection events, not actual breeding success.
    states=[(A,B,1.,[])]; reports=[]
    for gen in range(1,generations+1):
        nexts={}; best=None
        for x,y,weight,history in states:
            d=dict(distribution(x,y)); p=d.get(T,0.); hit=weight*chance(p,kull)
            row=dict(generation=gen,per_offspring=p,path_probability=hit,parents=[dict(zip(loci,x)),dict(zip(loci,y))],history=history)
            if best is None or hit>best['path_probability']:best=row
            if gen==generations:continue
            # Select at most 12 genotype types per brood by proximity and frequency.
            candidates=sorted(d,key=lambda g:(-score(g),-d[g],g))[:12]
            for u,v in combinations_with_replacement(candidates,2):
                # Conservative lower bound via separate halves of brood; guarantees distinct individuals.
                q=chance(d[u],kull//2)*chance(d[v],kull-kull//2) if kull>=2 else 0.
                if not q:continue
                w=weight*q; pair=(u,v)
                h=history+[dict(generation=gen,selected=[dict(zip(loci,u)),dict(zip(loci,v))],selection_lower_bound=q)]
                if pair not in nexts or w>nexts[pair][2]:nexts[pair]=(u,v,w,h)
        reports.append(best)
        states=sorted(nexts.values(),key=lambda s:-(s[2]*(.01+score(s[0])+score(s[1]))))[:beam]
        if not states:break
    return reports
