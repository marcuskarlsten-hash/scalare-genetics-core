"""Conditional multilocus forecasts; no inference from strain names or pixels."""
from collections import defaultdict
from itertools import product
from catalog import validate_genotype
from genetics import cross
from math import prod

def simulate(a,b,targets=None):
    if not a or set(a)!=set(b) or len(a)>6: raise ValueError('Ange samma 1–6 lokus för båda föräldrarna')
    loci=sorted(a)
    distributions=[cross(validate_genotype(k,a[k]),validate_genotype(k,b[k])) for k in loci]
    rows=[]
    for items in product(*(d.items() for d in distributions)):
        profile=dict(zip(loci,(g for g,p in items)))
        p=prod(p for g,p in items)
        dark=profile.get('Dark'); blue=profile.get('Philippine Blue'); stripe=profile.get('Stripeless/Zebra')
        label={'D/D':'Dubbel Dark','+/D':'Black Lace','+/+':'Silver'}.get(dark,'Grundfärg ej modellerad')
        if blue=='pb/pb': label+=' + Philippine Blue'; label+= ' (Pinoy-kandidat)' if dark in ('D/D','+/D') else ''
        if stripe=='S/S':label+=' + Stripeless (dubbel dos)'
        elif stripe=='+/S':label+=' + Stripeless (enkel dos)'
        elif stripe and 'Z' in stripe:label+=' + Zebra-allel'
        if profile.get('Albino')=='a/a':label+=' + Albino'
        # Only original unmodified reference illustrations are justified.
        asset={'D/D':'black','+/D':'lace','+/+':'silver'}.get(dark) if all(k=='Dark' or v=='+/+' for k,v in profile.items()) else None
        score=sum(profile.get(k)==validate_genotype(k,v) for k,v in (targets or {}).items())/len(targets) if targets else None
        rows.append((profile,p,label,asset,score))
    return sorted(rows,key=lambda r:(-(r[4] or 0),-r[1],str(r[0])))

def at_least_one(p,n):
    if not 0<=p<=1 or not isinstance(n,int) or n<0:raise ValueError('Ogiltig sannolikhet eller kullstorlek')
    return 1-(1-p)**n
