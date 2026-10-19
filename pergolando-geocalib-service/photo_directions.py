"""Six architectural reference lines; no training fixtures or disk I/O in detection."""
import base64,io,math
import cv2,numpy as np
from PIL import Image,ImageOps
from auto_references import detect_references
from architectural_lines import estimate_vanishing_family,depth_family_from_prior
from six_line_camera import solve_camera_with_metric_fallback,vanishing

def read_image(payload):
    raw=base64.b64decode(payload['fotoBase64'].split(',',1)[-1],validate=True)
    with Image.open(io.BytesIO(raw)) as image:
        image=ImageOps.exif_transpose(image).convert('RGB');image.thumbnail((1600,1600));return np.asarray(image)

def detect_six(payload):
    rgb=read_image(payload);h,w=rgb.shape[:2];K=np.array([[w,0,w/2],[0,w,h/2],[0,0,1.]])
    detected=cv2.createLineSegmentDetector(cv2.LSD_REFINE_STD).detect(cv2.cvtColor(rgb,cv2.COLOR_RGB2GRAY))[0];segments=[]
    if detected is not None:
        for raw in detected[:,0]:
            a,b=raw[:2].astype(float),raw[2:].astype(float)
            if np.linalg.norm(a-b)>max(24,.025*w):segments.append([a.tolist(),b.tolist()])
    segments.sort(key=lambda s:-np.linalg.norm(np.asarray(s[1])-s[0]));segments=segments[:250]
    proposal=detect_references({'fotoBase64':payload['fotoBase64']});floor=[[p['xNorm']*w,p['yNorm']*h] for p in proposal['punti']]
    # Snap the coarse floor proposal to an actual long detected pavement edge.
    if len(floor)==2:
        fa,fb=np.asarray(floor);fd=fb-fa;fd/=max(np.linalg.norm(fd),1e-9)
        matches=[]
        for segment in segments:
            a,b=np.asarray(segment);d=b-a;length=np.linalg.norm(d);mid=(a+b)/2
            distance=abs(np.cross(fd,mid-fa))
            if mid[1]>.55*h and length>.18*w and abs(np.dot(d/length,fd))>np.cos(np.deg2rad(12)) and distance<.035*min(w,h):matches.append((length,segment))
        if matches:floor=max(matches,key=lambda entry:entry[0])[1]
    vertical=[s for s in segments if abs(s[1][0]-s[0][0])<.25*abs(s[1][1]-s[0][1])];families=[]
    for axis,anchor,prior in [(0,floor,[1.,0,0]),(1,vertical[0] if vertical else [],[0,1.,0])]:
        family=estimate_vanishing_family(rgb,anchor,K,np.array(prior),detected_segments=detected)
        if family is not None:families.append((axis,family))
    def depth(groups):
        by_axis=dict(groups)
        if 0 not in by_axis or 1 not in by_axis:return None
        expected=np.cross(by_axis[0]['ray'],by_axis[1]['ray']);expected/=np.linalg.norm(expected)
        return depth_family_from_prior(rgb,K,expected)
    third=depth(families)
    if third is None:
        wider=estimate_vanishing_family(rgb,floor,K,np.array([1.,0,0]),prior_angle_deg=70,detected_segments=detected)
        if wider is not None:families=[f for f in families if f[0]!=0]+[(0,wider)];third=depth(families)
    if third is None:
        # Observe the missing family directly rather than forcing a nominal focal prior.
        observed=estimate_vanishing_family(rgb,floor,K,np.array([1.,0,0]),angle_limit_deg=75,prior_angle_deg=90,min_segment_fraction=.025,detected_segments=detected)
        if observed is not None and observed['count']>=6 and observed['angular_rms_deg']<.7:
            families=[f for f in families if f[0]!=0]+[(0,observed)]
        groups=dict(families);options=[]
        if 0 in groups and 1 in groups:
            for anchor in segments[:65]:
                delta=np.asarray(anchor[1])-anchor[0];unit=delta/np.linalg.norm(delta)
                if abs(unit[1])>.85:continue
                family=estimate_vanishing_family(rgb,anchor,K,np.cross(groups[0]['ray'],groups[1]['ray']),angle_limit_deg=20,prior_angle_deg=90,min_segment_fraction=.025,min_support=3,min_spread_fraction=.015,detected_segments=detected)
                if family is None or family['count']<6 or family['angular_rms_deg']>.7:continue
                if any(abs(np.dot(family['ray'],groups[axis]['ray']))>np.cos(np.deg2rad(25)) for axis in [0,1]):continue
                def already_used(segment):
                    a,b=np.asarray(segment);mid=(a+b)/2;unit=(b-a)/np.linalg.norm(b-a)
                    for axis in [0,1]:
                        for old in groups[axis]['segments']:
                            c,d=np.asarray(old);direction=(d-c)/np.linalg.norm(d-c)
                            if abs(np.dot(unit,direction))>.999 and abs(np.cross(direction,mid-c))<8:return True
                    return False
                if sum(already_used(segment) for segment in family['segments'])>.2*len(family['segments']):continue
                options.append(family)
            if options:third=max(options,key=lambda f:sum(np.linalg.norm(np.asarray(s[1])-s[0]) for s in f['segments']))
    if third is not None:families.append((2,third))
    selected=[None]*6
    for axis,family in families:
        candidates=family['segments'];first=max(candidates,key=lambda s:np.linalg.norm(np.array(s[1])-s[0]));second=max(candidates,key=lambda s:np.linalg.norm((np.array(s[0])+s[1])/2-(np.array(first[0])+first[1])/2));slot=axis*2
        if axis==0 and len(floor)==2:
            a,b=np.asarray(floor);normal=np.array([-(b-a)[1],(b-a)[0]]);normal/=np.linalg.norm(normal)
            separation=lambda s:abs(np.dot((np.array(s[0])+s[1])/2-a,normal));separate=[s for s in candidates if separation(s)>.04*min(w,h)]
            second=first if separation(first)>.04*min(w,h) else max(separate,key=lambda s:separation(s)+.2*np.linalg.norm(np.array(s[1])-s[0])) if separate else None
            selected[slot]=floor;selected[slot+1]=second
        else:selected[slot]=first;selected[slot+1]=second
    if selected[0] is None and len(floor)==2:selected[0]=floor
    if selected[2] is None and vertical:selected[2]=vertical[0]

    normalized=[None if segment is None else [{'xNorm':float(np.clip(point[0]/w,0,1)),'yNorm':float(np.clip(point[1]/h,0,1))} for point in segment] for segment in selected]
    count=sum(segment is not None for segment in selected)
    return {'lineeProspettiva':normalized,'punti':normalized[0] or [],'puntiProfondita':normalized[4] or [],'affidabilita':'da_confermare' if count==6 else 'incerta','messaggio':f'{count}/6 linee riconosciute. Controlla i bordi sulla foto; puoi correggerli o rimuoverli.'}

def calibrate_six(payload):
    rgb=read_image(payload);h,w=rgb.shape[:2];flat=payload['puntiFuga']
    inferred_depth=len(flat)==8
    if len(flat) not in (8,12):raise ValueError('Servono almeno due bordi del fronte e due verticali.')
    points=np.array([[float(p['xNorm'])*w,float(p['yNorm'])*h] for p in flat]).reshape(-1,2,2)
    if inferred_depth:
        # Two observed families constrain orientation; missing depth uses a focal prior.
        focal35=payload.get('focaleEquivalente35Mm')
        focal=float(focal35)*np.hypot(w,h)/np.hypot(36,24) if focal35 else max(w,h)
        K=np.array([[focal,0,w/2],[0,focal,h/2],[0,0,1.]])
        inverse=np.linalg.inv(K)
        x=inverse@vanishing(points[:2]);y=inverse@vanishing(points[2:4])
        z=np.cross(x,y)
        if np.linalg.norm(z)<1e-8:raise ValueError('Le direzioni del fronte e delle verticali coincidono.')
        vp=K@(z/np.linalg.norm(z));extra=[]
        for anchor in [points[0].mean(axis=0),points[1].mean(axis=0)]:
            direction=vp[:2]-anchor*vp[2]
            direction/=max(np.linalg.norm(direction),1e-8)
            extra.append([anchor.tolist(),(anchor+direction*max(40,.1*w)).tolist()])
        points=np.concatenate([points,np.asarray(extra)])
    floor=points[0].mean(axis=0)
    # Put the initial rear centre under the visible facade, not under the first floor fragment.
    vertical_vp=np.cross(np.cross(np.r_[points[2,0],1.],np.r_[points[2,1],1.]),np.cross(np.r_[points[3,0],1.],np.r_[points[3,1],1.]))
    facade_mid=np.r_[points[1].mean(axis=0),1.]
    floor_line=np.cross(np.r_[points[0,0],1.],np.r_[points[0,1],1.])
    anchor=np.cross(floor_line,np.cross(vertical_vp,facade_mid))
    if abs(anchor[2])>1e-8:
        candidate=anchor[:2]/anchor[2]
        if np.all(np.isfinite(candidate)) and .03*w<candidate[0]<.97*w and .45*h<candidate[1]<.97*h:floor=candidate
    request={'selected':points.tolist(),'origin':floor.tolist(),'cameraHeightCm':170,'focalPriorOnly':inferred_depth}
    if inferred_depth:request['origin']=[float(floor[0]),max(float(floor[1]),.85*h)]
    length=float(payload.get('lineaLunghezzaCm',0))
    if length>0:
        ref=payload.get('punti')
        request.update(reference=[[p['xNorm']*w,p['yNorm']*h] for p in ref],referenceCm=length,referenceHeightCm=float(payload.get('altezzaRiferimentoCm',0)))
    camera=solve_camera_with_metric_fallback(request,w,h,payload.get('focaleEquivalente35Mm'))
    R=np.asarray(camera['R']);K=np.asarray(camera['K']);sign=camera['depthSign'];basis=np.diag([sign,1,sign]);rotation=R@basis
    depth=float(payload['pRichiestaCm']);offset=np.asarray(camera['floor'])-basis@np.array([0.,0.,depth]);translation=R@(offset-np.asarray(camera['C']))
    rvec=cv2.Rodrigues(rotation)[0].ravel().tolist();fov=math.degrees(2*math.atan(w/(2*K[0,0])))
    warning=camera.get('metricWarning') or (None if camera['scaleVerified'] else 'Scala indicativa: per maggiore precisione misura uno dei bordi orizzontali selezionati.')
    if camera['intrinsicsEstimated']:warning=(warning or '')+' Focale indicativa: controlla la sagoma sulla foto.'
    if inferred_depth:warning='Profondità stimata da fronte e verticali; controlla la sagoma. Puoi aggiungere due bordi di profondità in Correggi prospettiva. '+(warning or '')
    return {'rvec':rvec,'tvec':translation.tolist(),'fovDeg':fov,'fxPx':float(K[0,0]),'fyPx':float(K[1,1]),'cxPx':float(K[0,2]),'cyPx':float(K[1,2]),'imageWidthPx':w,'imageHeightPx':h,'avviso':warning,'origineNormalizzata':{'xNorm':float(floor[0]/w),'yNorm':float(floor[1]/h)},'tettoNormalizzato':[]}
