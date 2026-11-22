import json, ipaddress
d=json.load(open('ruleset.json'))
rules=d['rules']; flows=d['flows']
def match(rule, fl):
    if ipaddress.ip_address(fl['src']) not in ipaddress.ip_network(rule['src']): return False
    if ipaddress.ip_address(fl['dst']) not in ipaddress.ip_network(rule['dst']): return False
    if rule['proto']!='any' and rule['proto']!=fl['proto']: return False
    dp=rule['dport']
    if dp!='any' and int(dp)!=int(fl['dport']): return False
    return True
accepted=[]
for fl in flows:
    act='deny'  # default DENY
    for r in rules:
        if match(r,fl):
            act=r['action']; break
    if act=='allow': accepted.append(fl)
accepted.sort(key=lambda f:f['id'])
flag=''.join(f['tag'] for f in accepted)
print('acceptés:',len(accepted),'/',len(flows))
print('FLAG:',flag)
