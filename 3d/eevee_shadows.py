"""Experimental floor shadow layer from matched Eevee passes."""
import bpy,numpy as np
from pathlib import Path

def render_floor_shadows(scene,output,cfg):
 objects=[o for o in bpy.context.view_layer.objects if o.visible_get() and o.type=='MESH' and not o.hide_render]
 original=bpy.data.images.load(str(output),check_existing=False)
 w,h=original.size;alpha=np.array(original.pixels[:],dtype=np.float32).reshape(h,w,4)[:,:,3]
 bpy.data.images.remove(original)
 bpy.ops.mesh.primitive_plane_add(size=100,location=(0,0,-.002));floor=bpy.context.object
 mat=bpy.data.materials.new('Shadow_Test_Floor');mat.use_nodes=True
 bsdf=mat.node_tree.nodes.get('Principled BSDF');bsdf.inputs['Base Color'].default_value=(.6,.6,.6,1);bsdf.inputs['Roughness'].default_value=1
 floor.data.materials.append(mat)
 receivers=[floor]
 if cfg.get('fissaggio')=='parete':
  from mathutils import Vector
  coords=[o.matrix_world@Vector(v) for o in objects for v in o.bound_box]
  rear=max(v.y for v in coords)
  bpy.ops.mesh.primitive_plane_add(size=100,location=(0,rear+.015,0),rotation=(1.57079632679,0,0))
  wall=bpy.context.object;wall.data.materials.append(mat);receivers.append(wall)
 bg=scene.world.node_tree.nodes['Background'].inputs['Strength'];bg.default_value=.15
 for light in [o for o in scene.objects if o.type=='LIGHT']:
  if light.data.type=='AREA':light.data.size=3
 def capture(name):
  scene.render.filepath=str(Path(output).with_name(name));bpy.ops.render.render(write_still=True)
  im=bpy.data.images.load(scene.render.filepath,check_existing=False)
  a=np.array(im.pixels[:],dtype=np.float32).reshape(h,w,4);bpy.data.images.remove(im);return a
 occupied=capture('floor-occupied.png')
 for o in objects:o.hide_render=True
 clean=capture('floor-clean.png')
 shade=np.clip(1-occupied[:,:,:3].mean(2)/np.maximum(clean[:,:,:3].mean(2),.001),0,.75)*.65
 shade[(alpha>.01)|(clean[:,:,3]<.99)]=0
 pixels=np.zeros((h,w,4),dtype=np.float32);pixels[:,:,3]=shade
 im=bpy.data.images.new('Eevee_Shadow_Layer',width=w,height=h,alpha=True)
 im.pixels.foreach_set(pixels.ravel());im.filepath_raw=str(Path(output).with_name('shadow.png'));im.file_format='PNG';im.save()
 for o in objects:o.hide_render=False
 for receiver in receivers:bpy.data.objects.remove(receiver,do_unlink=True)
