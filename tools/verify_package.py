#!/usr/bin/env python3
from pathlib import Path
import json,re,sys
ROOT=Path(__file__).resolve().parents[1]
EXPECTED='https://scasimir2021.github.io/lawn-a-mercy/go/?to=socials'
c=json.loads((ROOT/'data/site.json').read_text())
errors=[]
if c['routes']['socials']!=EXPECTED: errors.append('routes.socials mismatch')
for p in ROOT.rglob('*'):
    if p.is_file() and p.suffix.lower() in {'.html','.js','.css','.json','.svg'}:
        try:t=p.read_text(errors='ignore')
        except:continue
        if '678-485-0242' in t:errors.append(f'old phone found: {p.relative_to(ROOT)}')
if not (ROOT/'assets/qr/socials.svg').exists():errors.append('missing SVG QR')
if not (ROOT/'assets/hero/crew-approved.svg').exists():errors.append('missing crew SVG wrapper')
print('Expected social QR route:',EXPECTED)
if errors:
    print('FAIL');[print('-',e) for e in errors];sys.exit(1)
print('PASS: static package checks')
