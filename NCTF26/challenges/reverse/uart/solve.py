import csv, bisect
t=[];d0=[]
for r in csv.DictReader(open('files/capture.csv')):
    t.append(int(r['time_ns'])); d0.append(int(r['d0_uart']))
lvl=lambda ts: d0[max(0,min(len(t)-1,bisect.bisect_right(t,ts)-1))]
T=8000  # 8 us/bit = 125000 baud (plus petit gap entre transitions d0)
def falling(ts):
    c=ts
    while c<t[-1]:
        if lvl(c)==1 and lvl(c+1000)==0: return c+1000
        c+=1000
    return None
msg=bytearray(); cur=t[0]
while True:
    f=falling(cur)
    if f is None or f>t[-1]-9*T: break
    val=sum(lvl(f+int(T*(k+1.5)))<<k for k in range(8))  # 8N1, LSB first
    msg.append(val); cur=f+9*T
print(bytes(msg).decode())
