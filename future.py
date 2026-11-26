"""Conditional F1/F2/backcross forecasts for known parental genotypes.
F2 samples random independent F1 siblings, not selected survivors.
Assumes independent loci, equal viability, and no linkage.
"""
from collections import defaultdict
from genetics import cross
from catalog import validate_genotype
from math import prod

def forecast(a,b,targets):
    if not targets: raise ValueError('Minst ett mål krävs')
    result={k:1.0 for k in ('F1','F2','BC1-A','BC1-B')}
    for locus,t in targets.items():
        if locus not in a or locus not in b: raise ValueError('Saknad genotyp: '+locus)
        x,y,t=[validate_genotype(locus,g) for g in (a[locus],b[locus],t)]
        f1=cross(x,y)
        result['F1']*=f1.get(t,0)
        result['F2']*=sum(p*q*cross(g,h).get(t,0) for g,p in f1.items() for h,q in f1.items())
        result['BC1-A']*=sum(p*cross(g,x).get(t,0) for g,p in f1.items())
        result['BC1-B']*=sum(p*cross(g,y).get(t,0) for g,p in f1.items())
    return result

def parse_profile(s):
    result={}
    for item in s.split(','):
        k,v=map(str.strip,item.split('=',1))
        if not k or k in result: raise ValueError('Tomt eller duplicerat lokus')
        result[k]=validate_genotype(k,v)
    return result
