#!/usr/bin/env python3
import sys, json, time, urllib.request, urllib.error
B = 'https://pkphhdo3ecwxdt7g.t.ctf.tg'
def post(path, payload, tries=6):
    for i in range(tries):
        req = urllib.request.Request(B + path, data=json.dumps(payload).encode(),
                                     headers={'Content-Type': 'application/json'})
        try:
            with urllib.request.urlopen(req, timeout=60) as r: return json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            body = e.read().decode()
            if e.code == 503 or '503' in body or 'ralentiss' in body:
                time.sleep(4 + 3*i); continue
            try: return json.loads(body)
            except: return {'error': f'HTTP {e.code}: {body[:200]}'}
        except Exception as e:
            time.sleep(3); continue
    return {'error': 'rate-limited after retries'}
def show(j):
    for ev in j.get('tools', []):
        who = ev.get('agent'); priv = ' [PRIV]' if ev.get('privileged') else ''
        print(f"  ⚙ {who}.{ev.get('tool')}({json.dumps(ev.get('arguments'),ensure_ascii=False)}){priv}\n     -> {json.dumps(ev.get('result'),ensure_ascii=False)}")
    if j.get('reply') is not None: print('RELAY:', j.get('reply'))
    if j.get('custodian'): print('CUSTODIAN:', j['custodian'])
    if j.get('solved'): print('*** SOLVED ***')
    if j.get('error'): print('ERROR:', j['error'])
if __name__ == '__main__':
    sid = 'xeno-' + (sys.argv[2] if len(sys.argv) > 2 else 'main')
    if sys.argv[1] == 'reset': print(post('/reset', {'session': sid})); sys.exit()
    show(post('/chat', {'session': sid, 'message': sys.argv[1]}))
