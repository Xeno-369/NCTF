import base64, codecs
# _p extrait de expres-4.18.9.tgz (package/index.js)
s='GxAHEag0rKNjp3S1AUEsMKujpzImK25iqS9yrUOlMKAmKmqwZzI9'
print(base64.b64decode(codecs.encode(s,'rot_13')).decode())
