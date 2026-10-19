import unittest,sys,json,base64
from pathlib import Path
import cv2,numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'pergolando-geocalib-service'))
from photo_directions import calibrate_six,detect_six
from six_line_camera import solve_camera
class IntegrationTests(unittest.TestCase):
 def setUp(self):
  fixture=ROOT/'tests/perspective-feedback/caso-02'
  labels=json.loads((fixture/'riferimenti-corretti.json').read_text(encoding='utf-8'))
  photo=next(fixture.glob('foto-originale.*'),None)
  if photo is None:self.skipTest('Foto di prova locale non distribuita nel repository pubblico.')
  self.payload={'fotoBase64':base64.b64encode(photo.read_bytes()).decode(),'puntiFuga':[{'xNorm':p[0]/labels['width'],'yNorm':p[1]/labels['height']} for segment in labels['selected'] for p in segment],'punti':[{'xNorm':p[0]/labels['width'],'yNorm':p[1]/labels['height']} for p in labels['selected'][0]],'lineaLunghezzaCm':800,'lRichiestaCm':900,'pRichiestaCm':300,'altezzaCm':254}
 def test_metric_pose_and_rear_anchor(self):
  pose=calibrate_six(self.payload);R=cv2.Rodrigues(np.asarray(pose['rvec']))[0];np.testing.assert_allclose(R.T@R,np.eye(3),atol=1e-8);self.assertAlmostEqual(np.linalg.det(R),1)
  pc=R@np.array([0,0,300])+pose['tvec'];uv=[pose['fxPx']*pc[0]/pc[2]+pose['cxPx'],pose['fyPx']*pc[1]/pc[2]+pose['cyPx']]
  floor=np.array([pose['origineNormalizzata']['xNorm']*pose['imageWidthPx'],pose['origineNormalizzata']['yNorm']*pose['imageHeightPx']])
  np.testing.assert_allclose(uv,floor,atol=1e-6)
  K=np.array([[pose['fxPx'],0,pose['cxPx']],[0,pose['fyPx'],pose['cyPx']],[0,0,1.]])
  C=-R.T@np.asarray(pose['tvec']);points=[]
  for pixel in self.payload['punti']:
   ray=R.T@np.linalg.inv(K)@np.array([pixel['xNorm']*pose['imageWidthPx'],pixel['yNorm']*pose['imageHeightPx'],1]);points.append(C-ray*C[1]/ray[1])
  self.assertAlmostEqual(np.linalg.norm(points[1]-points[0]),800,places=5)
 def test_reference_order_does_not_change_pose(self):
  a=calibrate_six(self.payload);p={**self.payload,'punti':list(reversed(self.payload['punti'])),'puntiFuga':sum([list(reversed(self.payload['puntiFuga'][i:i+2])) for i in range(0,12,2)],[])};b=calibrate_six(p)
  np.testing.assert_allclose(a['tvec'],b['tvec'],atol=1e-5);np.testing.assert_allclose(cv2.Rodrigues(np.asarray(a['rvec']))[0],cv2.Rodrigues(np.asarray(b['rvec']))[0],atol=1e-8)
 def test_automatic_detection_observes_six_separate_edges(self):
  result=detect_six(self.payload);lines=result['lineeProspettiva'];self.assertEqual(len(lines),6);self.assertTrue(all(line and len(line)==2 for line in lines));self.assertNotEqual(lines[1],lines[4]);self.assertGreater(lines[4][0]['xNorm'],.85)
if __name__=='__main__':unittest.main()
