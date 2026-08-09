#!/usr/bin/env python3
"""Safely update Lawn-A-Mercy public JSON and regenerate permanent QR assets."""
from pathlib import Path
import json, argparse
import qrcode
from qrcode.image.svg import SvgPathImage

ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--phone');p.add_argument('--instagram');p.add_argument('--tiktok');p.add_argument('--linkedin');p.add_argument('--remote-config-url');a=p.parse_args()
path=ROOT/'data/site.json';c=json.loads(path.read_text())
if a.phone:
    digits=''.join(ch for ch in a.phone if ch.isdigit())[-10:]; pretty=f'{digits[:3]}-{digits[3:6]}-{digits[6:]}'
    c['contact']['phone']=pretty;c['contact']['phone_e164']='+1'+digits;c['routes']['call']='tel:+1'+digits;c['routes']['text']='sms:+1'+digits;c['routes']['quote']='sms:+1'+digits
for k in ('instagram','tiktok','linkedin'):
    v=getattr(a,k)
    if v:c['social'][k]=v
if a.remote_config_url is not None:c['runtime']['remote_config_url']=a.remote_config_url
path.write_text(json.dumps(c,indent=2)+'\n')
route=c['routes']['socials'];qr=qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H,box_size=14,border=4);qr.add_data(route);qr.make(fit=True);qr.make_image(fill_color='black',back_color='white').save(ROOT/'assets/qr/socials.png');svg=qr.make_image(image_factory=SvgPathImage);svg.save(str(ROOT/'assets/qr/socials.svg'))
print('Updated config; QR remains routed to:',route)
