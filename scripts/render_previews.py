"""Regenerate the README preview images.

Usage: pip install pymupdf pillow && python3 scripts/render_previews.py
"""
import fitz, sys, os
from PIL import Image, ImageDraw, ImageFont, ImageOps
os.chdir(sys.argv[1] if len(sys.argv)>1 else os.path.join(os.path.dirname(__file__),'..'))
d=fitz.open('Mushaf — Madinah QCF v4 Hafs.pdf')
out='docs/images'; os.makedirs(out,exist_ok=True)
def pdfidx(n): return n-1 if n<=2 else 2*n-4  # 0-based PDF page for mushaf page n
def crop(im,pad=40):
    bb=ImageOps.invert(im.convert('L')).point(lambda v:255 if v>20 else 0).getbbox()
    return im.crop((max(bb[0]-pad,0),max(bb[1]-pad,0),min(bb[2]+pad,im.width),min(bb[3]+pad,im.height)))
# 1) PDF screenshots
shots={}
for n in [1,2,3,302,604]:
    pix=d[pdfidx(n)].get_pixmap(dpi=150)
    im=Image.frombytes('RGB',(pix.width,pix.height),pix.samples)
    im=crop(im); im.save(f'{out}/page-{n:03d}.png',optimize=True); shots[n]=im
# spread of pages 2-3
a,b=shots[3],shots[2]; h=max(a.height,b.height)
sp=Image.new('RGB',(a.width+b.width+40,h),'white'); sp.paste(a,(0,(h-a.height)//2)); sp.paste(b,(a.width+40,(h-b.height)//2))
sp.save(f'{out}/spread-002-003.png',optimize=True)
# 2) Re-typeset pages directly from the TTF files using the PDF's glyph stream
def typeset(n,name,scale=4):
    pg=d[pdfidx(n)]; W,H=int(pg.rect.width*scale),int(pg.rect.height*scale)
    im=Image.new('RGB',(W,H),'white'); dr=ImageDraw.Draw(im)
    for b in pg.get_text('dict')['blocks']:
        for l in b.get('lines',[]):
            for s in l['spans']:
                if not s['font'].startswith('QCF4'): continue
                f=ImageFont.truetype(f"fonts/{s['font']}.ttf", int(s['size']*scale))
                x0,y0,x1,y1=l['bbox']; w=dr.textlength(s['text'],font=f)
                dr.text(((x0+x1)/2*scale-w/2, s['origin'][1]*scale), s['text'], font=f, fill=(20,20,20), anchor='ls')
    crop(im,60).save(f'{out}/{name}.png',optimize=True)
typeset(1,'font-render-al-fatiha'); typeset(604,'font-render-page-604')
# 3) Surah-name glyph specimen from QCF4_QBSML (first 12 surahs, right-to-left)
f=ImageFont.truetype('fonts/QCF4_QBSML.ttf',80); cols,rows=4,3
bbs=[f.getbbox(chr(0xf100+i)) for i in range(cols*rows)]
cw=max(b[2]-b[0] for b in bbs)+60; ch=max(b[3]-b[1] for b in bbs)+50
im=Image.new('RGB',(cols*cw,rows*ch),'white'); dr=ImageDraw.Draw(im)
for i in range(cols*rows):
    r,c=divmod(i,cols)
    dr.text(((cols-1-c)*cw+cw/2, r*ch+ch/2), chr(0xf100+i), font=f, fill=(20,20,20), anchor='mm')
crop(im).save(f'{out}/font-specimen-surah-names.png',optimize=True)
print(sorted(os.listdir(out)))
