"""Conditional ancestry and test-cross planning. No strain-name genotype assumptions."""
from collections import defaultdict
from math import log2,isfinite
from genetics import cross
from catalog import validate_genotype

def normalize(locus, weights):
    out=defaultdict(float)
    for g,p in weights.items():
        p=float(p)
        if not isfinite(p) or p<0: raise ValueError('Ogiltig vikt')
        out[validate_genotype(locus,g)]+=p
    total=sum(out.values())
    if not total or not isfinite(total): raise ValueError('Positiva vikter krävs')
    return {g:p/total for g,p in out.items() if p}

def ancestry(locus, father, mother):
    out=defaultdict(float)
    for a,p in normalize(locus,father).items():
        for b,q in normalize(locus,mother).items():
            for g,r in cross(a,b).items():out[g]+=p*q*r
    return dict(sorted(out.items()))

def entropy(weights):
    return -sum(p*log2(p) for p in weights if p>0)

def recommend(locus, hypotheses, testers, affected):
    """Expected information gain (bits) for one scored offspring, conditional on phenotype rule."""
    prior=normalize(locus,hypotheses)
    affected={validate_genotype(locus,g) for g in affected}
    rows=[]
    for tester in testers:
        t=validate_genotype(locus,tester)
        likelihood={g:sum(p for c,p in cross(g,t).items() if c in affected) for g in prior}
        p=sum(prior[g]*likelihood[g] for g in prior)
        gain=entropy([p,1-p])-sum(prior[g]*entropy([q,1-q]) for g,q in likelihood.items())
        rows.append((t,max(0,gain),p))
    return sorted(rows,key=lambda r:(-r[1],r[0]))
