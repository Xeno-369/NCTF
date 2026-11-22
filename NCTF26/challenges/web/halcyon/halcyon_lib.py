import time, json, urllib.request, urllib.error
B='https://v7pxsebxwetaq7ry.t.ctf.tg'
def chat(m, sid='xeno-main', tries=10):
    for i in range(tries):
        try:
            req=urllib.request.Request(B+'/chat',data=json.dumps({'session':sid,'message':m}).encode(),
                                       headers={'Content-Type':'application/json'})
            with urllib.request.urlopen(req,timeout=90) as r: return json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            b=e.read().decode()
            if e.code in (502,503) or 'ralentiss' in b or 'Budget' in b:
                time.sleep(20+10*i); continue
            return {'error':f'{e.code}:{b[:200]}'}
        except Exception:
            time.sleep(12); continue
    return {'error':'budget/rate - abandon'}
def reset(sid='xeno-main'):
    try:
        req=urllib.request.Request(B+'/reset',data=json.dumps({'session':sid}).encode(),headers={'Content-Type':'application/json'})
        with urllib.request.urlopen(req,timeout=30) as r: return json.loads(r.read().decode())
    except Exception as e: return {'error':str(e)}
def show(j):
    for ev in j.get('tools',[]):
        p='[PRIV]' if ev.get('privileged') else ''
        print(f"TOOL {ev.get('agent')}.{ev.get('tool')}({json.dumps(ev.get('arguments'),ensure_ascii=False)}) {p}")
        print("   ->", json.dumps(ev.get('result'),ensure_ascii=False))
    if j.get('reply'): print('RELAY:', j['reply'][:600])
    if j.get('custodian'): print('CUSTODIAN:', j['custodian'][:400])
    if j.get('solved'): print('\n*** SOLVED ***  (flag dans le result CUSTODIAN ci-dessus)')
    if j.get('error'): print('ERROR:', j['error'])
    return j
