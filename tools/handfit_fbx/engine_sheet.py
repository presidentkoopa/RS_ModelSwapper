"""Engine sheet (round 6 layout): side, eye view and close-up, each at rest (trigger frame) and firing (squeeze frame),
picked from gate3.py frame dumps by the probe's tic log (LANEC FRAME n t tic / LANEC T ... hand RQFG <frame>).
usage: engine_sheet.py <side tag> <eye tag> <close tag> <out.png> [rest_frame fire_frame]
  tags = gate3.py tags (rigout/logs/lanec3_<tag>.log, rigout/shots/<tag>/); frames = RQFG frame index (flamer: 2 rest, 3 fire).
Was run inline for sheets/flamethrower_engine_r6.png; the tic windows below are that run's."""
import re,glob,os,sys,numpy as np
from PIL import Image, ImageDraw
import paths
def pick(t,want,lo,hi):
    txt=open(os.path.join(paths.RIGOUT,'logs',f'lanec3_{t}.log'),errors='replace').read()
    fm=np.array([(int(a),int(b)) for a,b in re.findall(r'LANEC FRAME (\d+) t (\d+)',txt)])
    hand={int(a):(int(b),int(c)) for a,b,c in re.findall(r'LANEC T (\d+) gun \S+ hand RQFG (\d+) sup \S+ \S+ stab \S+ gf (-?\d+)',txt)}
    out=[]
    for f in sorted(glob.glob(os.path.join(paths.RIGOUT,'shots',t,'*.ppm'))):
        n=int(os.path.basename(f)[1:6]); tc=np.interp(n,fm[:,0],fm[:,1])
        if lo<=tc<=hi and abs(tc-round(tc))<0.3 and hand.get(int(round(tc)),(-1,))[0]==want: out.append((f,int(round(tc)),'ABCDEFGH'[hand[int(round(tc))][1]]))
    return out
def main(ts,te,tc_,png,rest=2,fire=3):
    sr=pick(ts,rest,350,390)[-1]; sf=pick(ts,fire,338,346)[-1]
    er=pick(te,rest,350,390)[-1]; ef=pick(te,fire,338,346)[-1]
    cr=pick(tc_,rest,350,390)[-1]; cf=pick(tc_,fire,300,346)[0]
    crop=(60,140,330,410)
    items=[(sr,'SIDE, at rest (trigger), tic %d, gun frame %s',None),(sf,'SIDE, FIRING (squeeze), tic %d, gun frame %s',None),
           (er,'EYE VIEW (as the owner), at rest, tic %d, gun frame %s',None),(ef,'EYE VIEW, FIRING, tic %d, gun frame %s',None),
           (cr,'CLOSE-UP fingers on the lever, rest, tic %d, gun frame %s',crop),(cf,'CLOSE-UP, FIRING: fingers pull the lever up, tic %d, gun frame %s',crop)]
    W=480; S=Image.new('RGB',(W*2,W*3))
    for i,((f,tc,gf),lab,cp) in enumerate(items):
        im=Image.open(f); im=im.crop(cp).resize((W,W),Image.LANCZOS) if cp else im
        S.paste(im,((i%2)*W,(i//2)*W)); d=ImageDraw.Draw(S); d.rectangle(((i%2)*W,(i//2)*W,(i%2)*W+W,(i//2)*W+16),fill=(0,0,0)); d.text(((i%2)*W+5,(i//2)*W+2),'QZD 17.3: '+lab%(tc,gf),fill=(255,255,0))
    S.save(png); print(items)
if __name__=='__main__':
    a=sys.argv[1:]; main(a[0],a[1],a[2],a[3],*[int(v) for v in a[4:6]])
