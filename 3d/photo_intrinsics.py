def apply_photo_intrinsics(scene,data,config):
    w,h=config['imageWidthPx'],config['imageHeightPx']
    if not config.get('fxPx'):return
    fx=config['fxPx'];fy=config.get('fyPx') or fx;cx=config.get('cxPx',w/2);cy=config.get('cyPx',h/2)
    data.sensor_fit='HORIZONTAL';data.sensor_width=36.;data.lens=fx*36/w
    data.shift_x=(w/2-cx)/w;data.shift_y=(cy-h/2)*(fx/fy)/w
    scene.render.pixel_aspect_x=1.;scene.render.pixel_aspect_y=fx/fy
