"""Local visual measurements and explicitly conditional single-locus forecasts."""
from collections import defaultdict
from itertools import product
import io, math
from PIL import Image, ImageOps
from genetics import cross
from catalog import validate_genotype


def measure(blob):
    """Approximate foreground on a white background; not a genotype classifier."""
    with Image.open(io.BytesIO(blob)) as src:
        im=ImageOps.exif_transpose(src).convert('RGB')
    im.thumbnail((400,400))
    w,h=im.size
    pixels=list(im.getdata())
    def white(p): return min(p)>=235 and max(p)-min(p)<=20
    border=[pixels[y*w+x] for y in range(h) for x in range(w) if x in (0,w-1) or y in (0,h-1)]
    quality=sum(map(white,border))/len(border)
    if quality<.90: raise ValueError('Vit, jämn bakgrund krävs för denna mätmetod. Beskär eller fotografera om.')
    fg=[(i%w,i//w,p) for i,p in enumerate(pixels) if not white(p)]
    if not fg or len(fg)<.02*w*h: raise ValueError('För liten eller ingen tydlig fiskyta.')
    if any(x in (0,w-1) or y in (0,h-1) for x,y,p in fg): raise ValueError('Motivet når bildkanten; använd en hel sidovy med marginal.')
    n=len(fg)
    return {'dark_fraction':sum(max(p)<85 for _,_,p in fg)/n,
            'blue_fraction':sum(p[2]>p[0]+20 and p[2]>p[1]+8 for _,_,p in fg)/n,
            'foreground_fraction':n/(w*h),'border_white':quality,
            'height_width':(max(y for x,y,p in fg)-min(y for x,y,p in fg)+1)/(max(x for x,y,p in fg)-min(x for x,y,p in fg)+1)}


def forecast_dark(a,b):
    """Single Dark locus only, no claim about modifiers or other loci."""
    a=validate_genotype('Dark',a); b=validate_genotype('Dark',b)
    names={'D/D':('Dubbel Dark','black'),'+/D':('Black Lace','lace'),'+/+':('Silver','silver')}
    return [(g,p,*names.get(g,('Fenotyp ej modellerad',None))) for g,p in cross(a,b).items()]


def confirmed(c,uid,fish,locus):
    import app
    vals=set()
    for _,d in app.records(c,uid,'evidence'):
        if d.get('name')==fish and d.get('locus')==locus and d.get('confidence','').lower() in ('bekräftad','confirmed'):
            vals.add(validate_genotype(locus,d['genotype']))
    return next(iter(vals)) if len(vals)==1 else None


def ancestry_scenarios(c,uid,fish):
    """Only registered, confirmed parental Dark genotypes generate probabilities."""
    import app
    d=app.get(c,uid,'fish',fish) or {}
    own=confirmed(c,uid,fish,'Dark')
    if own:return {own:1.0},'Registrerad bekräftad genotyp'
    if d.get('sire') and d.get('dam'):
        a=confirmed(c,uid,d['sire'],'Dark'); b=confirmed(c,uid,d['dam'],'Dark')
        if a and b:return cross(a,b),'Villkorad på registrerade föräldrars genotyper'
    return {},'Otillräckliga genetiska data; stamnamn är inte genotypbevis'


def mixed_forecast(a,b):
    if not a or not b: raise ValueError('Genotyp saknas. Välj ett uttryckligt scenario eller registrera genetiska bevis.')
    out=defaultdict(float); meta={}
    for (ga,pa),(gb,pb) in product(a.items(),b.items()):
        for g,p,n,img in forecast_dark(ga,gb):out[g]+=pa*pb*p;meta[g]=(n,img)
    return [(g,p,*meta[g]) for g,p in sorted(out.items())]
