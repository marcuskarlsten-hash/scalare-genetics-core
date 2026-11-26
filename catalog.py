"""Starter reference catalog; not molecular confirmation or phenotype prediction."""
SOURCE='https://www.theangelfishsociety.org/forum/content.php/30-Angelfish-Genetics-Index'
NOTATION='https://finarama.com/genetics/notations.htm'
BLUE='https://angelfins.ca/genetics-calculator/'
LOCI={
 'Dark':(('+','D','M','Gm','g'),'Flera alleler på samma lokus',NOTATION),
 'Stripeless/Zebra':(('+','S','Z'),'S och Z är alleler på samma lokus',NOTATION),
 'Smokey':(('+','Sm'),'Dosberoende uttryck',NOTATION),
 'Halfblack':(('+','h'),'Recessiv modell; uttryck kan variera',NOTATION),
 'Pearlscale':(('+','p'),'Recessiv modell',NOTATION),
 'Streaked':(('+','St'),'Modifierande anlag',NOTATION),
 'Veiled':(('+','V'),'Dosberoende uttryck',SOURCE),
 'Albino':(('+','a'),'Recessiv modell',SOURCE),
 'Philippine Blue':(('+','pb'),'Uppfödarmodell; recessiv',BLUE),
}
def validate_genotype(locus, genotype):
    alleles=genotype.split('/')
    if len(alleles)!=2 or not all(alleles): raise ValueError('Två alleler krävs')
    if locus in LOCI and not set(alleles)<=set(LOCI[locus][0]): raise ValueError('Allel saknas i valt lokus')
    return '/'.join(sorted(alleles))
