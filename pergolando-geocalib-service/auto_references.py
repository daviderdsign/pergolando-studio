"""Fast, local geometric reference proposals. Scores are heuristic, not probabilities."""
import base64
import io
import cv2
import numpy as np
from PIL import Image, ImageOps


def detect_references(payload):
    encoded=payload.get('fotoBase64','')
    if not isinstance(encoded,str) or not encoded:
        raise ValueError('fotoBase64 mancante')
    if encoded.startswith('data:'):
        encoded=encoded.split(',',1)[1]
    with Image.open(io.BytesIO(base64.b64decode(encoded,validate=True))) as image:
        image=ImageOps.exif_transpose(image).convert('RGB')
        image.thumbnail((1200,1200))
        rgb=np.asarray(image)
    h,w=rgb.shape[:2]
    gray=cv2.cvtColor(rgb,cv2.COLOR_RGB2GRAY)
    detected=cv2.createLineSegmentDetector(cv2.LSD_REFINE_STD).detect(gray)[0]
    empty={'punti':[],'puntiProfondita':[],'affidabilita':'incerta','messaggio':'Non trovo un riferimento chiaro. Segna la riga muro-pavimento con due tocchi.'}
    if detected is None:
        return empty
    segments=[]
    for raw in detected[:,0]:
        a,b=raw[:2].astype(float),raw[2:].astype(float)
        if a[0]>b[0]: a,b=b,a
        length=np.linalg.norm(b-a)
        if length>=max(18,.035*w): segments.append((a,b,length))
    candidates=[]
    # Collinear fragments are joined only across limited gaps, so a wall edge
    # interrupted by a post can be recovered without spanning arbitrary rails.
    flat=[v for v in segments if abs(v[1][1]-v[0][1])<.25*max(1,v[1][0]-v[0][0]) and .43*h<(v[0][1]+v[1][1])/2<.85*h]
    for a,b,length in flat:
        direction=(b-a)/length;normal=np.array([-direction[1],direction[0]])
        group=[(a,b,length)]
        lo,hi=a[0],b[0]
        for _ in range(3):
            for c,d,l in flat:
                if abs(np.dot(normal,d-c))/l>.035: continue
                if max(abs(np.dot(normal,c-a)),abs(np.dot(normal,d-a)))>max(3,.009*h): continue
                if c[0]>hi+.12*w or d[0]<lo-.12*w: continue
                if not any(np.array_equal(c,x[0]) and np.array_equal(d,x[1]) for x in group): group.append((c,d,l))
                lo=min(lo,c[0]);hi=max(hi,d[0])
        if hi-lo<.25*w: continue
        slope=(b[1]-a[1])/(b[0]-a[0]);p=np.array([lo,a[1]+slope*(lo-a[0])]);q=np.array([hi,a[1]+slope*(hi-a[0])])
        # A relatively smooth facade above a more textured floor is useful
        # evidence, but never a semantic guarantee that this is the wall base.
        xs=np.linspace(lo,hi,40).astype(int);ys=(p[1]+slope*(xs-lo)).astype(int)
        above=[];below=[]
        for x,y in zip(xs,ys):
            radius=max(8,int(.045*h));x=int(np.clip(x,3,w-4))
            if y-radius<0 or y+radius>=h: continue
            above.append(np.std(gray[y-radius:y-3,x-3:x+4]));below.append(np.std(gray[y+3:y+radius,x-3:x+4]))
        texture=float(np.mean(below)-np.mean(above)) if above else 0
        score=(hi-lo)/w + .35*np.clip(texture/20,-1,1)-.8*abs((p[1]+q[1])/(2*h)-.62)
        candidates.append((score,p,q,len(group),texture))
    if not candidates: return empty
    score,p,q,count,texture=max(candidates,key=lambda v:v[0])
    if score<.28: return empty
    # Depth proposals must span the visible floor and have horizontal motion;
    # near-vertical posts and wall edges are deliberately excluded.
    slope=(q[1]-p[1])/(q[0]-p[0]);depth=[]
    for a,b,length in segments:
        if a[1]>b[1]: a,b=b,a
        dx,dy=b-a
        if dy<.15*h or abs(dx)<.025*w or abs(dx)>1.5*dy: continue
        floor_y=p[1]+slope*(a[0]-p[0])
        if a[1]<floor_y-.035*h or a[1]>floor_y+.22*h or b[1]<floor_y+.17*h: continue
        if not (a[0]<.28*w or a[0]>.72*w): continue
        edge_score=length/h-.5*abs(a[1]-floor_y)/h
        depth.append((edge_score,a,b))
    hough=cv2.HoughLinesP(cv2.Canny(gray,60,140),1,np.pi/720,30,minLineLength=max(45,int(.14*h)),maxLineGap=max(12,int(.05*h)))
    if hough is not None:
        for raw in hough[:,0]:
            a,b=raw[:2].astype(float),raw[2:].astype(float)
            if a[1]>b[1]: a,b=b,a
            dx,dy=b-a;floor_y=p[1]+slope*(a[0]-p[0])
            if dy<.15*h or abs(dx)<.02*w or abs(dx)>1.5*dy: continue
            if a[1]<floor_y-.035*h or a[1]>floor_y+.22*h or b[1]<floor_y+.17*h: continue
            if not (a[0]<.28*w or a[0]>.72*w): continue
            depth.append((np.linalg.norm(b-a)/h-.5*abs(a[1]-floor_y)/h,a,b))
    direction=[]
    if depth:
        _,a,b=max(depth,key=lambda v:v[0]);direction=[a,b]
    def norm(points): return [{'xNorm':float(np.clip(v[0]/w,0,1)),'yNorm':float(np.clip(v[1]/h,0,1))} for v in points]
    # Nearby competing edges indicate ambiguity. Always require the seller to
    # confirm the visible red segment and its actual measured length.
    competitors=[v for v in candidates if abs((v[1][1]+v[2][1]-p[1]-q[1])/2)>.06*h and v[0]>score-.1]
    reliable=score>.65 and texture>3 and not competitors
    return {'punti':norm([p,q]),'puntiProfondita':norm(direction),'affidabilita':'da_confermare' if reliable else 'incerta','messaggio':('Ho proposto la riga sul muro'+(' e il bordo del terrazzo' if direction else '')+'. Controlla i tratti colorati e inserisci la lunghezza della riga rossa.' if reliable else 'Ho trovato dei bordi possibili. Controlla o correggi i tratti colorati prima di inserire la misura della riga rossa.')}