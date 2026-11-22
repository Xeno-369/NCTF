import httpx, asyncio, json, time, sys
HOST='https://knyfhp57al3hs5ob.t.ctf.tg'
import urllib.request,ssl
ctx=ssl._create_unverified_context()
ch=json.loads(urllib.request.urlopen(HOST+'/challenge',context=ctx,timeout=15).read())
n=ch['n']; e=ch['e']; c0=ch['c']
k=(n.bit_length()+7)//8; B=1<<(8*(k-2))
twoB=2*B; threeB=3*B
print('k',k,'bits',n.bit_length(),flush=True)
CONC=80
client=None
qcount=[0]
async def oracle_many(cs):
    # cs: liste d'entiers (chiffrés). retourne liste de bool conforme.
    sem=asyncio.Semaphore(CONC)
    res=[None]*len(cs)
    async def one(i,c):
        async with sem:
            for _ in range(5):
                try:
                    r=await client.get('/oracle',params={'c':str(c)})
                    res[i]=(r.json().get('valid')==True); qcount[0]+=1; return
                except Exception:
                    await asyncio.sleep(0.3)
            res[i]=False
    await asyncio.gather(*(one(i,c) for i,c in enumerate(cs)))
    return res
def cof(s):  # chiffré pour multiplicateur s
    return (c0*pow(s,e,n))%n
async def find_s_from(start, step=1, batch=CONC):
    s=start
    while True:
        cand=[s+step*j for j in range(batch)]
        vals=await oracle_many([cof(x) for x in cand])
        for j,v in enumerate(vals):
            if v: return cand[j]
        if qcount[0]%2000<batch: print("  ...s1 search req",qcount[0],"s~2^%.1f"%(s.bit_length()),flush=True)
        s+=step*batch
async def main():
    global client
    limits=httpx.Limits(max_connections=CONC,max_keepalive_connections=CONC)
    async with httpx.AsyncClient(base_url=HOST,http2=True,verify=False,timeout=20,limits=limits) as cl:
        global client; client=cl
        # s0=1 si c0 conforme
        base=await oracle_many([c0]); print('c0 conforme:',base[0],flush=True)
        s0=1
        M=[(twoB, threeB-1)]
        import math
        # Step 2a
        s=await find_s_from(-(-n//threeB))  # ceil(n/3B)
        print('s1 trouvé, req',qcount[0],flush=True)
        def update(M,s):
            newM=set()
            for (a,b) in M:
                rlo=-(-(a*s-threeB+1)//n); rhi=(b*s-twoB)//n
                for r in range(rlo,rhi+1):
                    na=max(a, -(-(twoB+r*n)//s)); nb=min(b,(threeB-1+r*n)//s)
                    if na<=nb: newM.add((na,nb))
            return sorted(newM)
        M=update(M,s); prev_s=s; it=0
        t0=time.time()
        while True:
            it+=1
            if len(M)==1 and M[0][0]==M[0][1]:
                m=M[0][0]; EM=m.to_bytes(k,'big')
                # PKCS v1.5 decode: 00 02 PS 00 message
                idx=EM.find(b'\x00',2)
                print('FLAG:',EM[idx+1:],flush=True); return
            if len(M)>=2:
                s=await find_s_from(prev_s+1)
            else:
                (a,b)=M[0]
                r=-(-(2*(b*prev_s-twoB))//n)
                found=None
                while found is None:
                    lo=-(-(twoB+r*n)//b); hi=(threeB-1+r*n)//a
                    # cherche s dans [lo,hi] par batch
                    s=lo
                    while s<=hi:
                        cand=[s+j for j in range(min(CONC,hi-s+1))]
                        vals=await oracle_many([cof(x) for x in cand])
                        for j,v in enumerate(vals):
                            if v: found=cand[j]; break
                        if found: break
                        s+=CONC
                    if found is None: r+=1
                s=found
            M=update(M,s); prev_s=s
            if it%10==0 or len(M)==1:
                print(f'it{it} |M|={len(M)} req={qcount[0]} {qcount[0]/(time.time()-t0):.0f}req/s',flush=True)
asyncio.run(main())
