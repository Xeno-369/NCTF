import re
src=open('/home/xeno369/Téléchargements/script_cine.js').read()

class V(str):
    def __index__(self):
        return ord(self[0])-48

# valeurs de l'objet jjencode $ (simulées)
vals={
 '___':'0','__$':'1','_$_':'2','_$$':'3','$__':'4','$_$':'5','$$_':'6','$$$':'7','$___':'8','$__$':'9',
 '$$$$':'f','$_$_':'a','$_$$':'b','$$__':'c','$$_$':'d','$$$_':'e',
 '$_':'constructor','_$':'o','$$':'return','__':'t','_':'u','$':'FUNC',
}
k={key:V(v) for key,v in vals.items()}

# isoler le payload : entre le premier  $.$$+"\""+   et   +"\"")())();  final
m=re.search(r'\$\.\$\$\+"\\""\+(.*)\+"\\""\)\(\)\)\(\);\s*$', src, re.S)
payload=m.group(1)

# transformer en expression Python
expr=payload
expr=expr.replace('(![]+"")','"false"').replace('(!""+"")','"true"').replace('({}+"")','"[object Object]"')
# $.KEY -> k['KEY']
expr=re.sub(r'\$\.([_$]+)', lambda mm:"k['%s']"%mm.group(1), expr)
phase1=eval(expr,{'k':k})
# phase 2 : résoudre les échappements JS (octal \ooo, \xNN, \\ , \" ...)
source=phase1.encode('latin1','backslashreplace').decode('unicode_escape')
print(source)
