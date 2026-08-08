#!/usr/bin/env python3
from pathlib import Path
import argparse,json,subprocess
try:
 import qrcode, qrcode.image.svg
except ImportError:
 qrcode=None
ROOT=Path(__file__).resolve().parents[1];CFG=ROOT/'data/site.json'
p=argparse.ArgumentParser();p.add_argument('--phone');p.add_argument('--email');p.add_argument('--base-url');p.add_argument('--remote-config');p.add_argument('--tiktok');p.add_argument('--instagram');p.add_argument('--linkedin');p.add_argument('--service');p.add_argument('--add-service',action='store_true');p.add_argument('--remove-service',action='store_true');p.add_argument('--publish',action='store_true');a=p.parse_args();c=json.loads(CFG.read_text())
if a.phone:c['contact']['phone']=a.phone;c['routes']['call']='tel:+1'+''.join(filter(str.isdigit,a.phone))[-10:];c['routes']['quote']=c['routes']['call']
if a.email:c['contact']['email']=a.email
if a.base_url:c['base_url']=a.base_url.rstrip('/')
if a.remote_config is not None:c['runtime']['remote_config_url']=a.remote_config
for k in ('tiktok','instagram','linkedin'):
 v=getattr(a,k)
 if v:c['social'][k]=v
if a.service and a.add_service and a.service not in c['services']:c['services'].append(a.service)
if a.service and a.remove_service:c['services']=[x for x in c['services'] if x.lower()!=a.service.lower()]
CFG.write_text(json.dumps(c,indent=2)+'\n')
if qrcode:
 for name,path in [('socials','/go/?to=socials'),('call','/go/?to=call'),('instagram','/go/?to=instagram')]:
  qr=qrcode.make(c['base_url']+path,image_factory=qrcode.image.svg.SvgPathImage,box_size=10,border=2);qr.save(ROOT/f'assets/qr/{name}.svg')
else:print('Install QR support: pip install -r tools/requirements.txt')
print('Updated',CFG)
if a.publish:
 subprocess.run(['git','add','.'],cwd=ROOT,check=True);subprocess.run(['git','commit','-m','Trio: update Lawn-A-Mercy site'],cwd=ROOT,check=False);subprocess.run(['git','push'],cwd=ROOT,check=True)
