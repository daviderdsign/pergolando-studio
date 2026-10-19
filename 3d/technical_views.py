import bpy,json
from pathlib import Path
from mathutils import Vector

def render_technical_views(output,cfg):
 from generate_flag import render_freestyle
 output=str(Path(output).resolve())
 scene=bpy.context.scene
 objects=[o for o in bpy.context.view_layer.objects if o.type=='MESH' and o.visible_get() and not o.hide_render]
 coords=[o.matrix_world@Vector(v) for o in objects for v in o.bound_box]
 lo=Vector([min(v[i] for v in coords) for i in range(3)]);hi=Vector([max(v[i] for v in coords) for i in range(3)])
 center=(lo+hi)/2;span=max((hi-lo))*1.15
 scene.cycles.samples=1
 scene.render.resolution_x=1400;scene.render.resolution_y=1400;scene.render.resolution_percentage=100
 scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA'
 meta={'spanCm':span*100,'projections':{},'dimensions':{k:cfg.get(k,0) for k in ['L_cm','P_cm','H_cm','deltaH_cm']}}
 for kind,forward,up in [('plan',(0,0,-1),(0,1,0)),('front',(0,1,0),(0,0,1)),('side',(-1,0,0),(0,0,1))]:
  data=bpy.data.cameras.new('Technical_'+kind);data.type='ORTHO';data.sensor_fit='HORIZONTAL';data.ortho_scale=span;data.clip_end=1000
  camera=bpy.data.objects.new(data.name,data);scene.collection.objects.link(camera);camera.location=center-Vector(forward)*50
  camera.rotation_euler=Vector(forward).to_track_quat('-Z', 'Y').to_euler();scene.camera=camera
  if kind=='plan':camera.rotation_euler=(0,0,0)
  bpy.context.view_layer.update()
  rotation=camera.rotation_euler.to_matrix()
  meta['projections'][kind]={'right_axis':list(rotation@Vector((1,0,0))),'up_axis':list(rotation@Vector((0,1,0))),'center_world':list(center),'ortho_scale':span,'resolution_x':1400,'resolution_y':1400,'bbox_min':list(lo),'bbox_max':list(hi)}
  render_freestyle(str(Path(output).with_name('technical-'+kind+'.png')))
  Path(str(Path(output).with_name('technical-'+kind+'.png'))+'.json').write_text(json.dumps(meta['projections'][kind]))
 Path(str(output)+'.technical.json').write_text(json.dumps(meta))
 # Service's mandatory primary output.
 Path(output).write_bytes(Path(output).with_name('technical-plan.png').read_bytes())
