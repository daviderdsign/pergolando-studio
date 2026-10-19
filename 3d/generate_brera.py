"""Pratic Brera single-module EEVEE photo render, using approved source meshes."""
import bpy,math,json,sys,argparse
from mathutils import Vector,Matrix
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))

def stretch(v,lo,hi,a,b):
 end=.2
 if v<=lo+end:return a+v-lo
 if v>=hi-end:return b+v-hi
 return a+end+(v-lo-end)*(b-a-2*end)/(hi-lo-2*end)

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--config-json',required=True);parser.add_argument('--output',required=True)
 args=parser.parse_args(sys.argv[sys.argv.index('--')+1:]);cfg=json.loads(args.config_json)
 L,P,H=[float(cfg[k])*.01 for k in ('L_cm','P_cm','H_cm')]
 if min(L,P,H)<=.5:raise ValueError('Dimensions too small for preserved ends')
 if cfg.get('nModuli',1)!=1:raise ValueError('Only single module supported')
 sources={n:bpy.data.objects[n] for n in ('Travi','Montante')}
 sources['Lama']=bpy.data.objects.get('Lama') or bpy.data.objects['Lamelle']
 for o in list(bpy.context.scene.objects):
  if o not in sources.values():bpy.data.objects.remove(o,do_unlink=True)
 collection=bpy.data.collections.new('Brera_Render');bpy.context.scene.collection.children.link(collection)
 mat=bpy.data.materials.get('Brera_Metallo_Colore_App') or bpy.data.materials.new('Brera_Metallo_Colore_App');mat.use_nodes=True
 rgb=cfg.get('colorRgb',[.6,.6,.6]);linear=[c/12.92 if c<=.04045 else ((c+.055)/1.055)**2.4 for c in rgb]
 bsdf=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED');bsdf.inputs['Base Color'].default_value=(*linear,1);bsdf.inputs['Metallic'].default_value=1;bsdf.inputs['Roughness'].default_value=.7
 def make(src,name,targets,offset,pivot=None):
  obj=src.copy();obj.data=src.data.copy();obj.animation_data_clear();obj.name=name;collection.objects.link(obj);obj.matrix_world=Matrix.Identity(4);obj.location=(0,0,0);obj.rotation_euler=(0,0,0);obj.scale=(1,1,1)
  vs=[src.matrix_basis@v.co for v in src.data.vertices];bb=[(min(v[i] for v in vs),max(v[i] for v in vs)) for i in range(3)]
  for vert,p in zip(obj.data.vertices,vs):
   for axis,(a,b) in targets.items():p[axis]=stretch(p[axis],*bb[axis],a,b)
   p+=Vector(offset)
   if pivot is not None:p-=Vector(pivot)
   vert.co=p
  if pivot is not None:obj.location=pivot
  obj.data.materials.clear();obj.data.materials.append(mat);obj.hide_render=False;obj.hide_viewport=False;obj.data.update();return obj
 # Front=Y0, rear=YP: matches photo grid/OpenCV world exactly.
 roof=H-.18500017
 make(sources['Travi'],'Brera_Travi',{0:(-L/2,L/2),1:(0,P)},(0,0,roof))
 for i,(x,y) in enumerate([(x,y) for x in (-L/2+.0625,L/2-.0625) for y in (.0625,P-.0625)],1):make(sources['Montante'],f'Brera_Montante_{i}',{2:(0,roof)},(x,y,0))
 pitch=.3 if cfg.get('opzioneTecnica','H20')=='H30' else .2
 n=max(1,math.floor((P-.4)/pitch+1e-6));blade=sources['Lama'];vs=[blade.matrix_basis@v.co for v in blade.data.vertices]
 yc=(min(v.y for v in vs)+max(v.y for v in vs))/2;zl=min(v.z for v in vs)
 state=cfg.get('statoLamelle','chiuse');angle={'chiuse':0,'aperte':-135,'impacchettate':-90}[state]
 for i in range(n):
  y=P/2+(n-1)/2*pitch-i*pitch-yc+.015
  if state=='impacchettate':y+=i*(pitch-.02)
  z=H-zl-.125
  obj=make(blade,f'Brera_Lama_{i+1:02}',{0:(-L/2+.125,L/2-.125)},(0,y,z),(0,y,z));obj.rotation_euler.x=math.radians(angle)
  if pitch==.3:
   ys=[v.co.y for v in obj.data.vertices];lo,hi=min(ys),max(ys);end=.03
   for v in obj.data.vertices:
    value=v.co.y
    if value<=lo+end:v.co.y=value-.05
    elif value>=hi-end:v.co.y=value+.05
    else:v.co.y=lo-.05+end+(value-lo-end)*(hi-lo+.1-2*end)/(hi-lo-2*end)
   obj.data.update()
  obj['passo_lama_cm']=pitch*100
  obj['opzione_tecnica']=cfg.get('opzioneTecnica','H20')
 scene=bpy.context.scene;scene.render.engine='BLENDER_EEVEE';scene.render.film_transparent=True
 scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA';scene.render.resolution_percentage=100
 world=bpy.data.worlds.new('Brera_World');world.use_nodes=True;world.node_tree.nodes['Background'].inputs['Color'].default_value=(.6,.6,.6,1);world.node_tree.nodes['Background'].inputs['Strength'].default_value=.8;scene.world=world
 for loc,power,size in [((0,P/2,H+5),1800,7),((L,-P,H+2),1200,5)]:
  data=bpy.data.lights.new('Brera_Softbox','AREA');data.energy=power;data.shape='DISK';data.size=size;obj=bpy.data.objects.new(data.name,data);collection.objects.link(obj);obj.location=loc;obj.rotation_euler=(Vector((0,P/2,H/2))-obj.location).to_track_quat('-Z','Y').to_euler()
 camdata=bpy.data.cameras.new('Brera_Camera');cam=bpy.data.objects.new('Brera_Camera',camdata);collection.objects.link(cam);scene.camera=cam
 if cfg.get('camera'):
  c=cfg['camera'];rv=Vector(c['rvec']);R=Matrix.Rotation(rv.length,3,rv.normalized() if rv.length>1e-9 else Vector((1,0,0)));inv=R.transposed();convert=Matrix(((1,0,0),(0,0,1),(0,-1,0)))
  cam.location=convert@(-(inv@(Vector(c['tvec'])*.01)));cam.rotation_euler=(convert@inv@Matrix(((1,0,0),(0,-1,0),(0,0,-1)))).to_euler();camdata.sensor_fit='HORIZONTAL';camdata.angle=math.radians(c['fovDeg']);scene.render.resolution_x=c['imageWidthPx'];scene.render.resolution_y=c['imageHeightPx']
  from photo_intrinsics import apply_photo_intrinsics
  apply_photo_intrinsics(scene,camdata,c)
 else:
  cam.location=(L*1.3,-P*1.5,H*2);cam.rotation_euler=(Vector((0,P/2,H/2))-cam.location).to_track_quat('-Z','Y').to_euler();camdata.type='ORTHO';camdata.ortho_scale=max(L,P,H)*1.7;scene.render.resolution_x=1200;scene.render.resolution_y=900
 for o in collection.objects:
  if o.type=='MESH':o.location+=Vector((float(cfg.get('offsetXCm',0))*.01,float(cfg.get('offsetZCm',0))*.01,0))
 bpy.context.view_layer.update()
 if cfg.get('technicalViews'):
  sys.path.insert(0,str(Path(__file__).parent))
  from technical_views import render_technical_views
  render_technical_views(args.output,cfg)
  return
 bpy.context.view_layer.update();scene.render.filepath=args.output;bpy.ops.render.render(write_still=True)
 if cfg.get('includeShadows') and cfg.get('camera'):
  sys.path.insert(0,str(Path(__file__).parent))
  from eevee_shadows import render_floor_shadows
  render_floor_shadows(scene,args.output,cfg)
 print(json.dumps({'engine':scene.render.engine,'dimensions_m':[L,P,H],'lame':n,'passo_cm':pitch*100,'stato':state,'metallic':1,'roughness':.7}))
if __name__=='__main__':main()



