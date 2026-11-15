#!/usr/bin/env python3
"""Make the social preview card (img/social-card.png, 1200x630) shown when the
home page or the archive is shared. Change the screenshots in `pics` (file name
in img/2026/, 1 = Neo Geo capture with black side bars to crop), then run:
    python3 tools/make_card.py
"""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
R=str(Path(__file__).resolve().parent.parent); OUT=R+"/img/social-card.png"
I=R+"/img/2026/"
BG=(245,245,243); INK=(20,20,20); MUTED=(94,94,90); ACC=(47,91,234)
def load(name, ng=False):
    im=Image.open(I+name).convert("RGB")
    if ng:  # Neo Geo: drop black side bars (game is 256 of 320 wide)
        w,h=im.size; b=int(w*32/320); im=im.crop((b,0,w-b,h))
    return im
def tile(im,w,h):
    iw,ih=im.size; s=max(w/iw,h/ih)
    im=im.resize((round(iw*s),round(ih*s)),Image.LANCZOS)
    x=(im.width-w)//2; y=(im.height-h)//2
    return im.crop((x,y,x+w,y+h))
pics=[("cruisn-usa-dc-golden-gate.png",0),("tiger-road-md-statue.png",0),("shadow-warrior-dc-boat.png",0),("tiger-road-ng-day-one-02.png",1),
      ("cruisn-usa-dc-grand-canyon.png",0),("tiger-road-md-mountain.png",0),("shadow-warrior-dc-medkit.png",0),("tiger-road-ng-day-one-03.png",1),
      ("cruisn-usa-dc-redwoods.png",0),("tiger-road-md-master.png",0),("shadow-warrior-dc-gate.png",0),("cruisn-usa-dc-appalachia.png",0)]
imgs=[load(n,ng) for n,ng in pics]
fname=ImageFont.truetype(R+"/assets/fonts/ibm-plex-sans-latin-600-normal.woff2",64)
fsub=ImageFont.truetype(R+"/assets/fonts/jetbrains-mono-latin-400-normal.woff2",28)
fsmall=ImageFont.truetype(R+"/assets/fonts/jetbrains-mono-latin-400-normal.woff2",20)
plats="mega-drive · saturn · dreamcast · neo-geo"

# A: full mosaic 4x3 with a light band across the middle
W,H=1200,630; gap=4
A=Image.new("RGB",(W,H),INK)
cw=(W-gap*3)//4; ch=(H-gap*2)//3
for i,im in enumerate(imgs):
    c,r=i%4,i//4
    A.paste(tile(im,cw,ch),(c*(cw+gap),r*(ch+gap)))
d=ImageDraw.Draw(A)
bh=210; by=(H-bh)//2
d.rectangle((0,by,W,by+bh),fill=BG)
d.text((80,by+38),"hombreimaginario",font=fname,fill=INK)
sub="retro works"; d.text((84,by+122),sub,font=fsub,fill=MUTED)
sw=d.textlength(sub,font=fsub); d.text((84+sw,by+122),"_",font=fsub,fill=ACC)
pw=d.textlength(plats,font=fsmall); d.text((W-80-pw,by+130),plats,font=fsmall,fill=ACC)
A.save(OUT,optimize=True)

print("written", OUT)
