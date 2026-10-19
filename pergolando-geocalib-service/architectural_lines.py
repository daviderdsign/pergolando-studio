"""Vanishing directions from separate architectural edges anchored to user lines.
No learned semantics: ambiguous/weak groups are rejected, not asserted correct.
"""
import cv2
import numpy as np


def estimate_vanishing_family(rgb, anchor_px, K, prior_direction, angle_limit_deg=22, min_segment_fraction=.055, min_support=3, prior_angle_deg=30, min_spread_fraction=.10, detected_segments=None):
    if anchor_px is None or len(anchor_px) != 2:
        return None
    h,w=rgb.shape[:2];scale=max(w,h)
    a,b=np.asarray(anchor_px,dtype=float)
    direction=b-a;length=np.linalg.norm(direction)
    if length<15:return None
    direction/=length
    center=np.array([w/2,h/2])
    def normalized(p):return np.r_[(p-center)/scale,1.]
    anchor=np.cross(normalized(a),normalized(b));anchor/=np.linalg.norm(anchor[:2])
    detected=detected_segments if detected_segments is not None else cv2.createLineSegmentDetector(cv2.LSD_REFINE_STD).detect(cv2.cvtColor(rgb,cv2.COLOR_RGB2GRAY))[0]
    if detected is None:return None
    edges=[]
    for raw in detected[:,0]:
        c,d=raw[:2].astype(float),raw[2:].astype(float);delta=d-c;size=np.linalg.norm(delta)
        if size<max(30,min_segment_fraction*scale):continue
        if abs(np.dot(delta/size,direction))<np.cos(np.deg2rad(angle_limit_deg)):continue
        line=np.cross(normalized(c),normalized(d));line/=np.linalg.norm(line[:2])
        if np.dot(line[:2],anchor[:2])<0:line=-line
        # Same physical edge or its two contrast borders count only once.
        if any(abs(np.dot(line[:2],x[0][:2]))>.9998 and abs(line[2]-x[0][2])*scale<6 for x in edges):continue
        edges.append((line,(c+d)/2,delta/size,size,c,d))
    if len(edges)<min_support:return None
    Kinv=np.linalg.inv(K)
    def pixel_vp(v):return np.array([v[0]*scale+center[0]*v[2],v[1]*scale+center[1]*v[2],v[2]])
    def errors(v):
        result=[]
        for line,mid,unit,size,c,d in edges:
            ray=v[:2]-((mid-center)/scale)*v[2]
            norm=np.linalg.norm(ray)
            result.append(abs(ray[0]*unit[1]-ray[1]*unit[0])/max(norm,1e-12))
        return np.array(result)
    best=None
    for line,*_ in edges:
        if abs(line[2]-anchor[2])*scale<.04*scale:continue
        vp=np.cross(anchor,line)
        if np.linalg.norm(vp)<1e-10:continue
        vp/=np.linalg.norm(vp)
        ray=Kinv@pixel_vp(vp);ray/=np.linalg.norm(ray)
        prior=np.asarray(prior_direction);prior/=np.linalg.norm(prior)
        if abs(np.dot(ray,prior))<np.cos(np.deg2rad(prior_angle_deg)):continue
        err=errors(vp);mask=err<np.sin(np.deg2rad(1))
        supports=[edges[i] for i in np.flatnonzero(mask)]
        if len(supports)<min_support:continue
        offsets=[x[0][2] for x in supports]
        if (max(offsets)-min(offsets))*scale<min_spread_fraction*scale:continue
        score=sum(min(x[3],.4*scale) for x in supports)
        if best is None or score>best[0]:best=(score,vp,mask)
    if best is None:return None
    score,vp,mask=best
    rows=[anchor*np.sqrt(length*3)]
    rows.extend(edges[i][0]*np.sqrt(edges[i][3]) for i in np.flatnonzero(mask))
    _,_,vh=np.linalg.svd(np.array(rows));vp=vh[-1]
    # Preserve the user's explicitly chosen family after refinement.
    anchor_ray=vp[:2]-((a+b)/2-center)/scale*vp[2]
    anchor_error=abs(anchor_ray[0]*direction[1]-anchor_ray[1]*direction[0])/max(np.linalg.norm(anchor_ray),1e-12)
    if anchor_error>np.sin(np.deg2rad(1)):return None
    err=errors(vp);support=np.flatnonzero(err<np.sin(np.deg2rad(1)))
    if len(support)<min_support:return None
    pixel=pixel_vp(vp);ray=Kinv@pixel;ray/=np.linalg.norm(ray)
    samples=[]
    for skip in range(4):
        subset=[i for j,i in enumerate(support) if j%4!=skip]
        if len(subset)<3:continue
        rows=[anchor*np.sqrt(length*3)]+[edges[i][0]*np.sqrt(edges[i][3]) for i in subset]
        _,_,vh=np.linalg.svd(np.array(rows));samples.append(pixel_vp(vh[-1]))
    return {"ray":ray,"vp":pixel,"vp_samples":samples,"count":len(support),"segments":[[edges[i][4].tolist(),edges[i][5].tolist()] for i in support],"angular_rms_deg":float(np.degrees(np.sqrt(np.mean(err[support]**2))))}


def architectural_directions(rgb, floor_px, vertical_px, K, rotation, depth_px=None):
    found=[]
    for axis,anchor in [(0,floor_px),(1,vertical_px),(2,depth_px)]:
        family=estimate_vanishing_family(rgb,anchor,K,rotation[:,axis],angle_limit_deg=75 if axis==2 else 22)
        if family is not None:found.append((axis,family))
    return found


def orthogonal_focal(families, K):
    """Estimate square-pixel focal from two supported orthogonal vanishing points.
    Reject near-infinite, implausible or unstable intersections.
    """
    groups=dict(families)
    if 0 not in groups or 1 not in groups:return None
    if any(g["count"]<6 or g["angular_rms_deg"]>.6 for g in [groups[0],groups[1]]):return None
    center=np.array([K[0,2],K[1,2]]);ratio=K[1,1]/K[0,0]
    def focal(a,b):
        if abs(a[2])<1e-9 or abs(b[2])<1e-9:return None
        x=a[:2]/a[2]-center;y=b[:2]/b[2]-center
        if max(np.linalg.norm(x),np.linalg.norm(y))>40*max(center):return None
        f2=-(x[0]*y[0]+x[1]*y[1]/ratio**2)
        return float(np.sqrt(f2)) if f2>0 else None
    nominal=focal(groups[0]["vp"],groups[1]["vp"])
    if nominal is None or not .65*K[0,0]<nominal<1.5*K[0,0]:return None
    estimates=[focal(a,b) for a in groups[0]["vp_samples"] for b in groups[1]["vp_samples"]]
    if len(estimates)<8 or any(v is None for v in estimates):return None
    low,high=np.quantile(estimates,[.1,.9])
    if (high-low)/nominal>.2:return None
    return {"fx":nominal,"relative_spread":float((high-low)/nominal)}


def depth_family_from_prior(rgb,K,prior):
    """Depth evidence independent of an imprecise user depth segment.
    Associate observed edges with the direction orthogonal to the other axes.
    """
    h,w=rgb.shape[:2];scale=max(w,h);center=np.array([w/2,h/2])
    vp=K@prior
    detected=cv2.createLineSegmentDetector(cv2.LSD_REFINE_STD).detect(cv2.cvtColor(rgb,cv2.COLOR_RGB2GRAY))[0]
    if detected is None:return None
    rows=[];segments=[];offsets=[]
    for raw in detected[:,0]:
        a,b=raw[:2].astype(float),raw[2:].astype(float);delta=b-a;length=np.linalg.norm(delta)
        if length<max(30,.045*scale):continue
        mid=(a+b)/2;ray=vp[:2]-mid*vp[2]
        angular=abs(ray[0]*delta[1]-ray[1]*delta[0])/max(np.linalg.norm(ray)*length,1e-12)
        if angular>np.sin(np.deg2rad(2)):continue
        line=np.cross(np.r_[(a-center)/scale,1],np.r_[(b-center)/scale,1]);line/=np.linalg.norm(line[:2])
        if any(abs(np.dot(line[:2],r[:2]/np.linalg.norm(r[:2])))>.9998 and min(abs(line[2]-o),abs(line[2]+o))*scale<6 for r,o in zip(rows,offsets)):continue
        rows.append(line*np.sqrt(length));offsets.append(line[2]);segments.append([a.tolist(),b.tolist()])
    if len(rows)<3 or np.ptp(offsets)*scale<.1*scale:return None
    _,_,vh=np.linalg.svd(np.array(rows));v=vh[-1]
    pixel=np.r_[v[:2]*scale+center*v[2],v[2]]
    ray=np.linalg.inv(K)@pixel;ray/=np.linalg.norm(ray)
    if abs(np.dot(ray,prior))<np.cos(np.deg2rad(8)):return None
    errors=[]
    for a,b in segments:
        a,b=np.array(a),np.array(b);delta=b-a;mid=(a+b)/2
        direction=pixel[:2]-mid*pixel[2]
        errors.append(abs(direction[0]*delta[1]-direction[1]*delta[0])/max(np.linalg.norm(direction)*np.linalg.norm(delta),1e-12))
    rms=float(np.degrees(np.sqrt(np.mean(np.array(errors)**2))))
    if rms>1.2:return None
    return {"vp":pixel,"ray":ray,"count":len(rows),"segments":segments,"angular_rms_deg":rms,"vp_samples":[]}

