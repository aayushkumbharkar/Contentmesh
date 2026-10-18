"""Repeatable real HTTP demo; --restart additionally restarts owned Compose services."""
import argparse
import json
import subprocess
import time
import urllib.request
from pathlib import Path
from uuid import uuid4

parser = argparse.ArgumentParser()
parser.add_argument('--restart', action='store_true')
parser.add_argument('--url', default='http://localhost:5173')
args = parser.parse_args()
base = args.url + '/api/workspaces/acmeshop'

def request(path, body=None):
    req = urllib.request.Request(path, data=json.dumps(body).encode() if body is not None else None,
                                 headers={'Content-Type':'application/json'})
    with urllib.request.urlopen(req, timeout=60) as response:
        return json.load(response)

request(base + '/seed', {})
marker = 'CART-' + uuid4().hex[:8]
first = request(base + '/sessions', {'title':'Demo incident ' + marker})
r1 = request(base + '/sessions/' + first['id'] + '/runs', {'text':'Checkout API errors after release 2.4. Redis session expiry observation ' + marker})
second = request(base + '/sessions', {'title':'Demo recall ' + marker})
r2 = request(base + '/sessions/' + second['id'] + '/runs', {'text':'Which previous change could explain the Checkout API incident, who owns it, and what was learned earlier?'})
assert r1['status'] == r2['status'] == 'completed'
assert len(r2['steps']) == 4 and r2['paths']
assert all(term in r2['answer'] for term in [marker, 'Maya Chen', '3600'])
if args.restart:
    subprocess.run(['docker', 'compose', 'restart', 'falkordb', 'backend'], cwd=Path(__file__).resolve().parents[1], check=True)
    for attempt in range(30):
        try:
            request(args.url + '/api/health')
            break
        except Exception:
            time.sleep(1)
    else:
        raise RuntimeError('Application did not recover after restart')
saved = request(base + '/runs')['runs']
assert any(r['id'] == r2['id'] and marker in r['answer'] for r in saved)
print(json.dumps({'status':'passed','marker':marker,'sessions':[first['id'],second['id']], 'run':r2['id'],'paths':len(r2['paths']),'restart_verified':args.restart}, indent=2))
