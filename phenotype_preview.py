"""Illustrative colour overlays, not a validated phenotype model."""
from PIL import Image
from pathlib import Path

def preview(profile):
    if set(profile)-{'Dark','Philippine Blue'}: return None
    base={'D/D':'black','+/D':'lace','+/+':'silver'}.get(profile.get('Dark'))
    if not base:return None
    blue=profile.get('Philippine Blue','+/+')
    if blue not in ('+/+','+/pb','pb/pb'):return None
    im=Image.open(Path(__file__).parent/'assets'/(base+'.jpg')).convert('RGB')
    if blue=='pb/pb':
        pixels=[]
        for r,g,b in im.getdata():
            if min(r,g,b)>220 or max(r,g,b)-min(r,g,b)>55: pixels.append((r,g,b));continue
            strength=min(1,(220-max(r,g,b))/70)*.55
            pixels.append((int(r*(1-.22*strength)),min(255,int(g+45*strength)),min(255,int(b+85*strength))))
        im.putdata(pixels)
    return im

def eye_region(blob, bounds):
    """User-selected normalized eye region; redness proxy, not iris diagnosis."""
    import io
    from PIL import ImageOps
    if len(bounds)!=4 or not all(0<=v<=1 for v in bounds) or bounds[0]>=bounds[2] or bounds[1]>=bounds[3]:raise ValueError('Ogiltigt ögonområde')
    with Image.open(io.BytesIO(blob)) as src: im=ImageOps.exif_transpose(src).convert('RGB')
    w,h=im.size; box=tuple(round(v*s) for v,s in zip(bounds,(w,h,w,h)))
    if box[2]-box[0]<3 or box[3]-box[1]<3:raise ValueError('Ögonområdet är för litet')
    pixels=[p for p in im.crop(box).getdata() if min(p)<220 and max(p)>35]
    if not pixels:raise ValueError('Inga användbara pixlar')
    return sum(r>g+25 and r>b+25 for r,g,b in pixels)/len(pixels)
