"""Metric camera calibration from three vanishing directions and a ground scale."""
import numpy as np

def line(segment):
    a,b=np.asarray(segment,dtype=float)
    if np.linalg.norm(a-b)<5:raise ValueError('Allunga il riferimento: gli estremi sono troppo vicini.')
    return np.cross(np.r_[a,1.],np.r_[b,1.])

def vanishing(pair):
    v=np.cross(line(pair[0]),line(pair[1]));n=np.linalg.norm(v)
    if n<1e-10:raise ValueError('I due riferimenti coincidono. Scegli bordi separati.')
    return v/n

def intrinsics(vps,w,h,focal35=None):
    note='Camera ricavata dalle tre fughe.';estimated=False
    if all(abs(v[2])>1e-8 for v in vps):
        points=[v[:2]/v[2] for v in vps];pairs=[(0,1),(0,2),(1,2)]
        A=np.array([[-(points[i]+points[j])[0],-(points[i]+points[j])[1],1.] for i,j in pairs]);b=np.array([-np.dot(points[i],points[j]) for i,j in pairs])
        try:
            cx,cy,q=np.linalg.solve(A,b);f2=q-cx*cx-cy*cy
            if f2>0 and np.isfinite(f2) and -.5*w<cx<1.5*w and -.5*h<cy<1.5*h and .1*max(w,h)<np.sqrt(f2)<8*max(w,h):
                return np.array([[np.sqrt(f2),0,cx],[0,np.sqrt(f2),cy],[0,0,1.]]),note,estimated
        except np.linalg.LinAlgError:pass
    # Near-infinite vanishing points or weak intersections need a focal prior.
    cx,cy=w/2,h/2;f=focal35*np.hypot(w,h)/np.hypot(36,24) if focal35 else max(w,h)
    if abs(vps[0][2])>1e-8 and abs(vps[2][2])>1e-8:
        p=vps[0][:2]/vps[0][2]-[cx,cy];q=vps[2][:2]/vps[2][2]-[cx,cy];f2=-np.dot(p,q)
        if f2>0 and .1*max(w,h)<np.sqrt(f2)<8*max(w,h):f=np.sqrt(f2)
    return np.array([[f,0,cx],[0,f,cy],[0,0,1.]]),'Focale indicativa: fughe quasi parallele o riferimenti da verificare.',True

def solve_camera(payload,w,h,focal35=None):
    selected=payload['selected']
    if len(selected)!=6 or any(s is None for s in selected):raise ValueError('Servono sei bordi: due per ciascuna direzione.')
    points=np.asarray(selected,dtype=float)
    if points.shape!=(6,2,2) or not np.all(np.isfinite(points)):raise ValueError('Riferimenti non validi.')
    vps=[vanishing(selected[i:i+2]) for i in [0,2,4]]
    K,note,estimated=intrinsics(vps,w,h,focal35)
    if payload.get("focalPriorOnly"):
        f=float(focal35)*np.hypot(w,h)/np.hypot(36,24) if focal35 else max(w,h)
        K=np.array([[f,0,w/2],[0,f,h/2],[0,0,1.]])
        estimated=True
    inverse=np.linalg.inv(K)
    origin=np.asarray(payload.get('origin',[w*.35,h*.8]),dtype=float)
    if origin.shape!=(2,) or not np.all(np.isfinite(origin)):raise ValueError('Posizione della base non valida.')
    def sign_for(ray,axis,positive=True):
        v=K@ray;derivative=v[:2]-origin*v[2]
        return ray if (derivative[axis]>=0)==positive else -ray
    x=inverse@vps[0];x/=np.linalg.norm(x);x=sign_for(x,0)
    y=inverse@vps[1];y/=np.linalg.norm(y);y=sign_for(y,1)
    y-=x*np.dot(x,y)
    if np.linalg.norm(y)<.01:raise ValueError('La fuga verticale coincide con quella del fronte.')
    y/=np.linalg.norm(y);z=np.cross(x,y);z/=np.linalg.norm(z);R=np.column_stack([x,y,z])
    depth_ray=K@z;depth_sign=1 if (depth_ray[1]-origin[1]*depth_ray[2])<0 else -1
    H=float(payload.get('cameraHeightCm',170));verified=False
    reference=payload.get('reference');measure=payload.get('referenceCm')
    def ground_unit(pixel):
        ray=R.T@(inverse@np.r_[pixel,1.])
        if ray[1]<=1e-7:raise ValueError('Scegli la base e il riferimento sul pavimento, sotto l’orizzonte.')
        return ray/ray[1]
    if reference is not None and measure is not None:
        ref=np.asarray(reference,dtype=float);measure=float(measure)
        if ref.shape!=(2,2) or not np.all(np.isfinite(ref)) or not 1<=measure<=100000:raise ValueError('Riferimento metrico non valido.')
        elevation=float(payload.get('referenceHeightCm',0))
        if not np.isfinite(elevation) or not 0<=elevation<=100000:raise ValueError('Altezza del segmento non valida.')
        rays=[R.T@(inverse@np.r_[pixel,1.]) for pixel in ref]
        if any(abs(ray[1])<1e-7 for ray in rays) or rays[0][1]*rays[1][1]<=0:raise ValueError('Il segmento attraversa l’orizzonte: scegli un bordo orizzontale su uno stesso piano.')
        if elevation==0 and rays[0][1]<0:raise ValueError('Questo segmento è sopra l’orizzonte: non è a terra. Indica la sua altezza reale dal pavimento, oppure misura un bordo a terra.')
        length=np.linalg.norm(rays[1]/rays[1][1]-rays[0]/rays[0][1])
        if length<1e-5:raise ValueError('Allunga il riferimento metrico.')
        H=elevation+np.sign(rays[0][1])*measure/length;verified=True
    if not np.isfinite(H) or not 5<=H<=10000:raise ValueError('Scala non plausibile: verifica il segmento misurato.')
    C=np.array([0.,-H,0.]);floor=C+ground_unit(origin)*H
    return {'K':K.tolist(),'R':R.tolist(),'C':C.tolist(),'floor':floor.tolist(),'depthSign':depth_sign,'cameraHeightCm':H,'scaleVerified':verified,'intrinsicsEstimated':estimated,'vanishingPoints':[v.tolist() for v in vps],'note':note}

def box_vertices(camera,dimensions,translation):
    L,P,H=map(float,dimensions);tx,up,tz=map(float,translation)
    if not all(np.isfinite([L,P,H,tx,up,tz])) or not all(1<=n<=100000 for n in [L,P,H]):raise ValueError('Dimensioni non valide.')
    base=np.array(camera['floor'])+[tx,-up,tz];sign=camera['depthSign']
    vertices=[base+[x,y,z] for x,y,z in [(0,0,0),(L,0,0),(L,0,sign*P),(0,0,sign*P),(0,-H,0),(L,-H,0),(L,-H,sign*P),(0,-H,sign*P)]]
    return np.array(vertices)

def project(vertices,camera):
    R=np.array(camera['R']);K=np.array(camera['K']);C=np.array(camera['C']);cam=(R@(np.asarray(vertices)-C).T).T
    if np.any(cam[:,2]<=.001):raise ValueError('Il volume attraversa la camera: spostalo più lontano.')
    homogeneous=(K@cam.T).T
    return homogeneous[:,:2]/homogeneous[:,2:3]


def solve_camera_with_metric_fallback(payload,width,height,focal35=None):
    """Reject a bad measurement without discarding otherwise valid camera geometry."""
    try:
        return solve_camera(payload,width,height,focal35)
    except ValueError as error:
        if payload.get('reference') is None:
            raise
        unmeasured={k:v for k,v in payload.items() if k not in ('reference','referenceCm')}
        result=solve_camera(unmeasured,width,height,focal35)
        result['metricWarning']='Riferimento misurato non utilizzato: '+str(error)+' Il volume resta visibile con scala stimata. Segna entrambi gli estremi sul pavimento oppure rimuovi il riferimento.'
        result['note']+=' '+result['metricWarning']
        return result
