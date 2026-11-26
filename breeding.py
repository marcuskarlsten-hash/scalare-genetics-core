"""Explicit Mendelian models; no phenotype-to-genotype certainty assumed."""
from genetics import cross, posterior
from itertools import product
import re

def test_cross(allele, tester, affected, normal, recessive=True, error=0.01):
    if not allele or allele=='+' or '/' in allele: raise ValueError('Ange en muterad allel, inte + eller en genotyp.')
    if min(affected,normal)<0 or not 0<=error<.5: raise ValueError('Ogiltiga antal eller felmarginal.')
    hypotheses=[]
    for g in ['+/+',f'+/{allele}',f'{allele}/{allele}']:
        dist=cross(g,tester)
        if any(set(k.split('/'))-{'+' ,allele} for k in dist): raise ValueError('Testaren måste ha samma två alleltyper.')
        p=sum(v for k,v in dist.items() if (k.split('/').count(allele)==2 if recessive else allele in k.split('/')))
        p=error+(1-2*error)*p
        hypotheses.append((g,1/3,{'affected':p,'normal':1-p}))
    return posterior(hypotheses,{'affected':affected,'normal':normal})

def multi_cross(loci, limit=4096):
    """Independent assortment only; each locus maps to two parental genotypes."""
    if not loci: raise ValueError('Minst ett lokus krävs.')
    names=list(loci); distributions=[cross(*loci[n]) for n in names]
    from math import prod
    if prod(map(len,distributions))>limit: raise ValueError('För många kombinationer.')
    return [(dict(zip(names,(k for k,p in combo))),prod(p for k,p in combo)) for combo in product(*(d.items() for d in distributions))]

def generation(mode,a='',b=''):
    if mode=='new': return 'F1'
    if mode=='filial':
        if a==b and re.fullmatch(r'F[1-9]\d*',a):return 'F'+str(int(a[1:])+1)
        raise ValueError('Filial korsning kräver samma F-generation och verifierad gemensam linje.')
    if mode=='backcross':
        if a=='F1':return 'BC1'
        if re.fullmatch(r'BC[1-9]\d*',a):return 'BC'+str(int(a[2:])+1)
        raise ValueError('Återkorsning kräver F1 eller tidigare BC-generation och verifierad återkorsningslinje.')
    return 'Ej fastställd'
