"""Local perspective diagnostics, separate from quotation and rendering services."""
import base64,io,json,hashlib
from datetime import datetime
from pathlib import Path
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
import cv2,numpy as np
from PIL import Image,ImageOps
from auto_references import detect_references
from architectural_lines import estimate_vanishing_family,depth_family_from_prior
ROOT=Path(__file__).resolve().parent

def analyze(payload):
    data=payload['photo'].split(',',1)[-1]
    raw_photo=base64.b64decode(data,validate=True)
    original_id=hashlib.sha256(raw_photo).hexdigest()[:20]
    archive=ROOT.parent/'output/perspective-inputs'/original_id;archive.mkdir(parents=True,exist_ok=True)
    with Image.open(io.BytesIO(raw_photo)) as photo:
        extension={'JPEG':'jpg','PNG':'png','WEBP':'webp'}.get(photo.format,'img')
        (archive/('foto-originale.'+extension)).write_bytes(raw_photo)
        photo=ImageOps.exif_transpose(photo).convert('RGB');photo.thumbnail((1600,1600));rgb=np.asarray(photo)
    h,w=rgb.shape[:2];K=np.array([[w,0,w/2],[0,w,h/2],[0,0,1.]])
    detected=cv2.createLineSegmentDetector(cv2.LSD_REFINE_STD).detect(cv2.cvtColor(rgb,cv2.COLOR_RGB2GRAY))[0]
    segments=[]
    if detected is not None:
        for raw in detected[:,0]:
            a,b=raw[:2].astype(float),raw[2:].astype(float)
            if np.linalg.norm(b-a)>max(24,.025*w):segments.append([a.tolist(),b.tolist()])
    segments.sort(key=lambda s:-np.linalg.norm(np.array(s[1])-s[0]));segments=segments[:250]
    proposal=detect_references({'fotoBase64':payload['photo']})
    floor=[[p['xNorm']*w,p['yNorm']*h] for p in proposal['punti']]
    vertical=sorted([s for s in segments if abs(s[1][0]-s[0][0])<.25*abs(s[1][1]-s[0][1])],key=lambda s:-np.linalg.norm(np.array(s[1])-s[0]))
    families=[]
    for axis,anchor,prior in [(0,floor,[1.,0,0]),(1,vertical[0] if vertical else [],[0,1.,0])]:
        f=estimate_vanishing_family(rgb,anchor,K,np.array(prior))
        if f is not None:families.append((axis,f))
    def depth_proposal(groups):
        by_axis=dict(groups)
        if 0 not in by_axis or 1 not in by_axis:return None
        expected=np.cross(by_axis[0]['ray'],by_axis[1]['ray']);expected/=np.linalg.norm(expected)
        return depth_family_from_prior(rgb,K,expected)
    depth=depth_proposal(families)
    # Retain complete proposals that already have support in all three directions.
    # Expand yaw search only when the conservative proposal is incomplete.
    if depth is None:
        wider=estimate_vanishing_family(rgb,floor,K,np.array([1.,0,0]),prior_angle_deg=70)
        if wider is not None:
            families=[item for item in families if item[0]!=0]+[(0,wider)]
            depth=depth_proposal(families)
    if depth is not None:families.append((2,depth))
    selected=[None]*6
    for axis,f in families:
        candidates=f['segments'];first=max(candidates,key=lambda s:np.linalg.norm(np.array(s[1])-s[0]))
        second=max(candidates,key=lambda s:np.linalg.norm((np.array(s[0])+s[1])/2-(np.array(first[0])+first[1])/2))
        slot={0:0,1:2,2:4}[axis]
        if axis==0 and len(floor)==2:
            a,b=np.asarray(floor,dtype=float);unit=(b-a)/np.linalg.norm(b-a);normal=np.array([-unit[1],unit[0]])
            def separation(s):return abs(np.dot((np.array(s[0])+s[1])/2-a,normal))
            # Do not accept two contrast edges or fragments of the same physical edge.
            separate=[s for s in candidates if separation(s)>.04*min(w,h)]
            second=first if separation(first)>.04*min(w,h) else max(separate,key=lambda s:separation(s)+.2*np.linalg.norm(np.array(s[1])-s[0])) if separate else None
            selected[slot]=floor;selected[slot+1]=second
        else:selected[slot]=first;selected[slot+1]=second
    if selected[0] is None and len(floor)==2:selected[0]=floor
    if selected[2] is None and vertical:selected[2]=vertical[0]
    if not (archive/'proposta-iniziale.json').exists():
        (archive/'proposta-iniziale.json').write_text(json.dumps({'id':original_id,'width':w,'height':h,'selected':selected,'counts':[(axis,f['count']) for axis,f in families]},ensure_ascii=False,indent=2),encoding='utf-8')
    stream=io.BytesIO();photo.save(stream,format='JPEG',quality=94)
    return {'originalId':original_id,'width':w,'height':h,'image':'data:image/jpeg;base64,'+base64.b64encode(stream.getvalue()).decode(),'segments':segments,'selected':selected,'counts':[(axis,f['count']) for axis,f in families]}

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path=='/demo':
            candidates=[ROOT.parent/'output/calibration-diagnostics/foto-originale.png',ROOT.parent.parent/'Pergolando/3d/test_photos/sfondo.png']
            path=next((p for p in candidates if p.exists()),None)
            if path is None:self.send_error(404);return
            data=path.read_bytes();self.send_response(200);self.send_header('Content-Type','image/png');self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data);return
        if self.path not in ['/','/health']:self.send_error(404);return
        data=b'{"status":"ok"}' if self.path=='/health' else (ROOT/'perspective_lab.html').read_bytes()
        self.send_response(200);self.send_header('Content-Type','application/json' if self.path=='/health' else 'text/html; charset=utf-8');self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data)
    def do_POST(self):
        if self.path not in ['/analyze','/save-case']:self.send_error(404);return
        size=int(self.headers.get('Content-Length',0))
        if not 0<size<30000000:self.send_error(413);return
        try:
            payload=json.loads(self.rfile.read(size))
            if self.path=='/save-case':
                target=ROOT.parent/'output/perspective-cases'/datetime.now().strftime('%Y%m%d-%H%M%S-%f');target.mkdir(parents=True)
                for key,name in [('image','verifica.png'),('photo','foto.jpg')]:
                    encoded=payload.pop(key);raw=base64.b64decode(encoded.split(',',1)[-1],validate=True)
                    with Image.open(io.BytesIO(raw)) as check:check.verify()
                    (target/name).write_bytes(raw)
                (target/'riferimenti.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')
                answer={'saved':str(target)}
            else:answer=analyze(payload)
            data=json.dumps(answer).encode();status=200
        except Exception as e:data=json.dumps({'error':str(e)}).encode();status=400
        self.send_response(status);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data)

if __name__=='__main__':
    print('Laboratorio prospettiva: http://127.0.0.1:8766/',flush=True)
    ThreadingHTTPServer(('127.0.0.1',8766),Handler).serve_forever()
